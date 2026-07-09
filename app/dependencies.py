"""Dependency injection and shared utilities for Cymor Movie API"""
from typing import AsyncGenerator
from functools import lru_cache
from loguru import logger
from app.config import get_settings, Settings
from app.exceptions import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address
import httpx


# Rate Limiter instance
limiter = Limiter(key_func=get_remote_address)


@lru_cache()
def get_settings_cached() -> Settings:
    """Get cached settings"""
    return get_settings()


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create and manage HTTP client for Moviebox API requests"""
    settings = get_settings_cached()
    async with httpx.AsyncClient(
        timeout=settings.moviebox_api_timeout,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
    ) as client:
        logger.debug("HTTP client created")
        yield client
        logger.debug("HTTP client closed")


def check_rate_limit(
    key: str,
    limit: int = None,
    period: int = None
) -> bool:
    """Check if request should be rate limited"""
    settings = get_settings_cached()
    
    if not settings.rate_limit_enabled:
        return True
    
    limit = limit or settings.rate_limit_requests
    period = period or settings.rate_limit_period
    
    # This would integrate with Redis or in-memory store in production
    return True


def setup_logging():
    """Configure loguru logger"""
    settings = get_settings_cached()
    
    logger.remove()  # Remove default handler
    logger.add(
        sink=lambda msg: None,  # Sink for production
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    logger.info(f"Logging configured - Level: {settings.log_level}")
