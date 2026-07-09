"""Service layer for Moviebox API integration"""
import httpx
from typing import Optional, List, Dict, Any
from loguru import logger
from app.config import get_settings
from app.exceptions import MovieboxAPIError, SearchError
import asyncio


class MovieboxService:
    """Handles all interactions with Moviebox API"""
    
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.settings = get_settings()
        self.base_urls = {
            "v1": f"https://{self.settings.moviebox_api_v1_host}",
            "v2": f"https://{self.settings.moviebox_api_v2_host}",
            "v3": f"https://{self.settings.moviebox_api_v3_host}"
        }
    
    async def search_movies(
        self, 
        query: str, 
        page: int = 1,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search for movies"""
        try:
            timeout = timeout or self.settings.moviebox_api_timeout
            
            logger.info(f"Searching movies: {query} (page: {page})")
            
            params = {
                "q": query,
                "page": page,
                "type": "movie"
            }
            
            response = await self.client.get(
                f"{self.base_urls['v1']}/api/v1/search",
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Search successful: found {len(data.get('results', []))} results")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Moviebox API error: {e}")
            raise MovieboxAPIError(f"Failed to search movies: {str(e)}", original_error=e)
        except Exception as e:
            logger.error(f"Unexpected error during movie search: {e}")
            raise SearchError(query=query, message="Unexpected error during search")
    
    async def search_series(
        self, 
        query: str, 
        page: int = 1,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search for TV series"""
        try:
            timeout = timeout or self.settings.moviebox_api_timeout
            
            logger.info(f"Searching series: {query} (page: {page})")
            
            params = {
                "q": query,
                "page": page,
                "type": "tv"
            }
            
            response = await self.client.get(
                f"{self.base_urls['v1']}/api/v1/search",
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Search successful: found {len(data.get('results', []))} results")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Moviebox API error: {e}")
            raise MovieboxAPIError(f"Failed to search series: {str(e)}", original_error=e)
        except Exception as e:
            logger.error(f"Unexpected error during series search: {e}")
            raise SearchError(query=query, message="Unexpected error during search")
    
    async def get_movie_details(self, movie_id: str) -> Dict[str, Any]:
        """Get detailed movie information"""
        try:
            logger.info(f"Fetching movie details: {movie_id}")
            
            response = await self.client.get(
                f"{self.base_urls['v2']}/api/v2/movie/{movie_id}",
                timeout=self.settings.moviebox_api_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Movie details fetched successfully")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch movie details: {e}")
            raise MovieboxAPIError(f"Failed to get movie details: {str(e)}", original_error=e)
    
    async def get_series_details(self, series_id: str) -> Dict[str, Any]:
        """Get detailed series information"""
        try:
            logger.info(f"Fetching series details: {series_id}")
            
            response = await self.client.get(
                f"{self.base_urls['v2']}/api/v2/series/{series_id}",
                timeout=self.settings.moviebox_api_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Series details fetched successfully")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch series details: {e}")
            raise MovieboxAPIError(f"Failed to get series details: {str(e)}", original_error=e)
    
    async def get_streaming_links(
        self, 
        item_id: str, 
        item_type: str = "movie"
    ) -> Dict[str, Any]:
        """Get streaming links for a movie or series"""
        try:
            logger.info(f"Fetching streaming links for {item_type}: {item_id}")
            
            endpoint = f"/api/v1/{item_type}/{item_id}/links"
            response = await self.client.get(
                f"{self.base_urls['v3']}{endpoint}",
                timeout=self.settings.moviebox_api_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Streaming links fetched successfully")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch streaming links: {e}")
            raise MovieboxAPIError(f"Failed to get streaming links: {str(e)}", original_error=e)
    
    async def get_trending(self, content_type: str = "all") -> Dict[str, Any]:
        """Get trending content"""
        try:
            logger.info(f"Fetching trending {content_type} content")
            
            params = {"type": content_type}
            response = await self.client.get(
                f"{self.base_urls['v1']}/api/v1/trending",
                params=params,
                timeout=self.settings.moviebox_api_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Trending content fetched successfully")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch trending content: {e}")
            raise MovieboxAPIError(f"Failed to get trending content: {str(e)}", original_error=e)
