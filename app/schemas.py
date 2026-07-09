"""Pydantic schemas for API request/response validation"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Search and Discovery Models
class MovieBasic(BaseModel):
    """Basic movie information"""
    id: str = Field(..., description="Unique movie ID")
    title: str = Field(..., description="Movie title")
    poster_url: Optional[str] = Field(None, description="Movie poster URL")
    year: Optional[int] = Field(None, description="Release year")
    rating: Optional[float] = Field(None, description="IMDb rating (0-10)")
    description: Optional[str] = Field(None, description="Short description")

    class Config:
        from_attributes = True


class MovieDetail(MovieBasic):
    """Detailed movie information"""
    genres: Optional[List[str]] = Field(default_factory=list, description="Movie genres")
    director: Optional[str] = Field(None, description="Director name")
    cast: Optional[List[str]] = Field(default_factory=list, description="Cast members")
    duration: Optional[int] = Field(None, description="Duration in minutes")
    country: Optional[str] = Field(None, description="Production country")
    language: Optional[str] = Field(None, description="Original language")
    quality_options: Optional[List[str]] = Field(default_factory=list, description="Available qualities")


class SeriesBasic(BaseModel):
    """Basic TV series information"""
    id: str = Field(..., description="Unique series ID")
    title: str = Field(..., description="Series title")
    poster_url: Optional[str] = Field(None, description="Series poster URL")
    year: Optional[int] = Field(None, description="Release year")
    rating: Optional[float] = Field(None, description="IMDb rating")
    total_seasons: Optional[int] = Field(None, description="Total seasons")

    class Config:
        from_attributes = True


class SeriesDetail(SeriesBasic):
    """Detailed TV series information"""
    genres: Optional[List[str]] = Field(default_factory=list, description="Series genres")
    cast: Optional[List[str]] = Field(default_factory=list, description="Cast members")
    description: Optional[str] = Field(None, description="Series description")
    status: Optional[str] = Field(None, description="Ongoing, Completed, etc.")


class Episode(BaseModel):
    """TV series episode information"""
    season: int = Field(..., description="Season number")
    episode: int = Field(..., description="Episode number")
    title: Optional[str] = Field(None, description="Episode title")
    description: Optional[str] = Field(None, description="Episode description")
    aired_date: Optional[datetime] = Field(None, description="Air date")
    quality_options: Optional[List[str]] = Field(default_factory=list, description="Available qualities")


# Search Request/Response
class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    content_type: Optional[str] = Field("all", description="'movie', 'series', or 'all'")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Results per page")


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    content_type: str
    total_results: int
    page: int
    total_pages: int
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Movie or Series results")


# Streaming Models
class StreamingLink(BaseModel):
    """Streaming link information"""
    quality: str = Field(..., description="Video quality (1080p, 720p, etc.)")
    url: str = Field(..., description="Streaming URL")
    is_direct: bool = Field(default=True, description="Is direct link or redirecting")


class StreamingResponse(BaseModel):
    """Streaming response"""
    item_id: str
    item_title: str
    item_type: str = Field(..., description="'movie' or 'series'")
    links: List[StreamingLink] = Field(default_factory=list)
    subtitles: Optional[Dict[str, str]] = Field(default_factory=dict, description="Language: URL mapping")


# Download Models
class DownloadRequest(BaseModel):
    """Download request parameters"""
    item_id: str = Field(..., description="Movie or Series ID")
    item_type: str = Field(..., description="'movie' or 'series'")
    quality: str = Field(default="best", description="Desired quality")
    subtitle_language: Optional[str] = Field("english", description="Subtitle language")
    season: Optional[int] = Field(None, description="Season number (for series)")
    episode: Optional[int] = Field(None, description="Episode number (for series)")


class DownloadResponse(BaseModel):
    """Download response"""
    download_id: str = Field(..., description="Unique download ID")
    status: str = Field(..., description="'queued', 'downloading', 'completed', 'failed'")
    item_title: str
    quality: str
    progress_percent: float = Field(default=0.0, ge=0, le=100)
    estimated_time_remaining: Optional[int] = Field(None, description="Seconds remaining")
    created_at: datetime
    updated_at: datetime


# Trending and Discovery
class TrendingResponse(BaseModel):
    """Trending content response"""
    movies: List[MovieBasic] = Field(default_factory=list, description="Trending movies")
    series: List[SeriesBasic] = Field(default_factory=list, description="Trending series")
    last_updated: datetime


class GenresResponse(BaseModel):
    """Available genres response"""
    genres: List[str] = Field(..., description="List of available genres")


# Error Response
class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    detail: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)
