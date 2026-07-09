"""Main FastAPI application"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import get_settings
from app.dependencies import setup_logging, limiter
from app.exceptions import CymoreException, RateLimitExceeded
from app.routes.search import router as search_router
from app.routes.streaming import router as streaming_router


# Setup logging on startup
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle"""
    logger.info("🚀 Starting Cymor Movie API...")
    logger.info(f"Version: {get_settings().app_version}")
    logger.info(f"Environment: {get_settings().environment}")
    yield
    logger.info("🛑 Shutting down Cymor Movie API...")


# Initialize FastAPI app
app = FastAPI(
    title="Cymor Movie API",
    description="A high-performance API for searching and streaming movies and TV series",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Setup rate limiter
app.state.limiter = limiter

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors"""
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "You have made too many requests. Please try again later.",
            "retry_after": exc.retry_after
        }
    )


@app.exception_handler(CymoreException)
async def cymor_exception_handler(request: Request, exc: CymoreException):
    """Handle Cymor custom exceptions"""
    logger.error(f"Cymor exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "detail": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(search_router)
app.include_router(streaming_router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Cymor Movie API",
        "version": get_settings().app_version
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Cymor Movie API",
        "version": "1.0.0",
        "description": "A high-performance API for searching and streaming movies and TV series",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "search": "/api/v1/search",
            "streaming": "/api/v1/streaming",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=not settings.is_production,
        log_level="info"
    )
