"""Search routes for movies and TV series"""
from fastapi import APIRouter, Depends, Query
from loguru import logger
from app.schemas import SearchRequest, SearchResponse, MovieBasic, SeriesBasic
from app.services.moviebox_service import MovieboxService
from app.dependencies import get_http_client, limiter
from app.exceptions import SearchError, ValidationError
import httpx

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/movies", response_model=SearchResponse)
@limiter.limit("50/minute")
async def search_movies(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Search for movies by title or keywords
    
    - **q**: Search query (required, 1-200 characters)
    - **page**: Page number (default: 1)
    - **limit**: Results per page (default: 20, max: 100)
    """
    try:
        if not q.strip():
            raise ValidationError("Search query cannot be empty", field="q")
        
        logger.info(f"Movie search endpoint called: q={q}, page={page}")
        
        service = MovieboxService(client)
        results = await service.search_movies(query=q, page=page)
        
        # Transform results to match schema
        movies = [
            MovieBasic(
                id=item.get("id"),
                title=item.get("title"),
                poster_url=item.get("poster"),
                year=item.get("year"),
                rating=item.get("rating"),
                description=item.get("description")
            )
            for item in results.get("results", [])
        ]
        
        return SearchResponse(
            query=q,
            content_type="movie",
            total_results=results.get("total", 0),
            page=page,
            total_pages=results.get("total_pages", 1),
            results=[movie.dict() for movie in movies]
        )
        
    except SearchError as e:
        logger.error(f"Search error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_movies: {e}")
        raise SearchError(query=q, message="Failed to search movies")


@router.get("/series", response_model=SearchResponse)
@limiter.limit("50/minute")
async def search_series(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Search for TV series by title or keywords
    
    - **q**: Search query (required, 1-200 characters)
    - **page**: Page number (default: 1)
    - **limit**: Results per page (default: 20, max: 100)
    """
    try:
        if not q.strip():
            raise ValidationError("Search query cannot be empty", field="q")
        
        logger.info(f"Series search endpoint called: q={q}, page={page}")
        
        service = MovieboxService(client)
        results = await service.search_series(query=q, page=page)
        
        # Transform results to match schema
        series = [
            SeriesBasic(
                id=item.get("id"),
                title=item.get("title"),
                poster_url=item.get("poster"),
                year=item.get("year"),
                rating=item.get("rating"),
                total_seasons=item.get("seasons")
            )
            for item in results.get("results", [])
        ]
        
        return SearchResponse(
            query=q,
            content_type="series",
            total_results=results.get("total", 0),
            page=page,
            total_pages=results.get("total_pages", 1),
            results=[s.dict() for s in series]
        )
        
    except SearchError as e:
        logger.error(f"Search error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_series: {e}")
        raise SearchError(query=q, message="Failed to search series")


@router.get("/all", response_model=SearchResponse)
@limiter.limit("50/minute")
async def search_all(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Search for both movies and TV series
    
    - **q**: Search query (required, 1-200 characters)
    - **page**: Page number (default: 1)
    - **limit**: Results per page (default: 20, max: 100)
    """
    try:
        if not q.strip():
            raise ValidationError("Search query cannot be empty", field="q")
        
        logger.info(f"Combined search endpoint called: q={q}, page={page}")
        
        service = MovieboxService(client)
        
        # Search both movies and series concurrently
        import asyncio
        movie_results, series_results = await asyncio.gather(
            service.search_movies(query=q, page=page),
            service.search_series(query=q, page=page)
        )
        
        # Combine and transform results
        all_results = []
        
        for item in movie_results.get("results", []):
            all_results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "type": "movie",
                "poster": item.get("poster"),
                "year": item.get("year"),
                "rating": item.get("rating")
            })
        
        for item in series_results.get("results", []):
            all_results.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "type": "series",
                "poster": item.get("poster"),
                "year": item.get("year"),
                "rating": item.get("rating")
            })
        
        return SearchResponse(
            query=q,
            content_type="all",
            total_results=len(all_results),
            page=page,
            total_pages=1,
            results=all_results
        )
        
    except SearchError as e:
        logger.error(f"Search error: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_all: {e}")
        raise SearchError(query=q, message="Failed to search content")
