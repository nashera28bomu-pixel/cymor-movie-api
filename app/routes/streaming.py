"""Streaming routes for movies and TV series"""
from fastapi import APIRouter, Depends, Query
from loguru import logger
from app.schemas import StreamingResponse, StreamingLink
from app.services.moviebox_service import MovieboxService
from app.dependencies import get_http_client, limiter
from app.exceptions import StreamingError
import httpx

router = APIRouter(prefix="/api/v1/streaming", tags=["streaming"])


@router.get("/{item_type}/{item_id}", response_model=StreamingResponse)
@limiter.limit("30/minute")
async def get_streaming_links(
    item_type: str = Query(..., regex="^(movie|series)$", description="'movie' or 'series'"),
    item_id: str = Query(..., min_length=1, description="Movie or Series ID"),
    quality: str = Query("all", description="Specific quality or 'all'"),
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Get streaming links for a movie or TV series
    
    - **item_type**: 'movie' or 'series'
    - **item_id**: Unique identifier for the content
    - **quality**: 'all', '1080p', '720p', '480p', etc.
    """
    try:
        logger.info(f"Streaming links requested: {item_type}/{item_id}")
        
        service = MovieboxService(client)
        links_data = await service.get_streaming_links(item_id=item_id, item_type=item_type)
        
        # Transform links
        streaming_links = []
        for link in links_data.get("links", []):
            streaming_links.append(
                StreamingLink(
                    quality=link.get("quality", "unknown"),
                    url=link.get("url"),
                    is_direct=link.get("direct", True)
                )
            )
        
        return StreamingResponse(
            item_id=item_id,
            item_title=links_data.get("title", ""),
            item_type=item_type,
            links=streaming_links,
            subtitles=links_data.get("subtitles", {})
        )
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise StreamingError(item_id=item_id, message="Failed to get streaming links")
