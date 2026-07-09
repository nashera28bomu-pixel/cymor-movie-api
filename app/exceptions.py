"""Custom exceptions for Cymor Movie API"""
from typing import Optional, Dict, Any


class CymoreAPIException(Exception):
    """Base exception for Cymor API"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class MovieboxAPIError(CymoreAPIException):
    """Error from Moviebox API"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, status_code=502, detail={"error": str(original_error)})
        self.original_error = original_error


class SearchError(CymoreAPIException):
    """Error during search operation"""
    
    def __init__(self, query: str, message: str = "Search failed"):
        super().__init__(
            f"{message} for query: {query}",
            status_code=400,
            detail={"query": query}
        )


class DownloadError(CymoreAPIException):
    """Error during download operation"""
    
    def __init__(self, item_id: str, message: str = "Download failed"):
        super().__init__(
            f"{message} for item: {item_id}",
            status_code=500,
            detail={"item_id": item_id}
        )


class StreamingError(CymoreAPIException):
    """Error during streaming operation"""
    
    def __init__(self, item_id: str, message: str = "Streaming failed"):
        super().__init__(
            f"{message} for item: {item_id}",
            status_code=500,
            detail={"item_id": item_id}
        )


class ValidationError(CymoreAPIException):
    """Invalid request data"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            status_code=422,
            detail={"field": field} if field else {}
        )


class RateLimitExceeded(CymoreAPIException):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=429,
            detail={"retry_after": retry_after}
        )


class ResourceNotFound(CymoreAPIException):
    """Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            f"{resource_type} with ID '{resource_id}' not found",
            status_code=404,
            detail={"resource_type": resource_type, "resource_id": resource_id}
        )
