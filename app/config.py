"""Configuration module for Cymor Movie API"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_title: str = "Cymor Movie API"
    api_version: str = "1.0.0"
    api_description: str = "Modern streaming and movie download API powered by Moviebox"
    api_debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Moviebox API Configuration
    moviebox_api_v1_host: str = "h5.aoneroom.com"
    moviebox_api_v2_host: str = "h5-api.aoneroom.com"
    moviebox_api_v3_host: str = "h5-api.aoneroom.com"
    moviebox_api_timeout: int = 25  # Render timeout safety margin
    
    # Redis Configuration (Optional - Render free tier doesn't include Redis)
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False  # Disabled by default for Render free tier
    cache_ttl: int = 3600  # 1 hour
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]
    cors_credentials: bool = True
    cors_methods: List[str] = ["GET", "POST", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Rate Limiting (Render free tier friendly)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 50  # Conservative for free tier
    rate_limit_period: int = 60
    
    # Download Configuration (Render has 30s timeout)
    download_timeout: int = 25  # Safe timeout for Render
    download_max_concurrent: int = 1  # Conservative for free tier RAM
    download_temp_dir: str = "/tmp/cymor_downloads"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Render Deployment Specific
    render_environment: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
