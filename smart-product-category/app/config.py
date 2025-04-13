import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    
    # API settings
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    model_name: str = Field("gemini-2.0-flash", env="MODEL_NAME")
    temperature: float = Field(0.7, env="MODEL_TEMPERATURE")
    max_output_tokens: int = Field(2048, env="MAX_OUTPUT_TOKENS")
    
    # API Rate limiting
    rate_limit_enabled: bool = Field(True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(10, env="RATE_LIMIT_REQUESTS")
    rate_limit_timeframe: int = Field(60, env="RATE_LIMIT_TIMEFRAME")  # in seconds
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    @validator('google_api_key')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError("GOOGLE_API_KEY is required")
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in allowed_levels:
            logger.warning(f"Invalid log level: {v}, defaulting to INFO")
            return "INFO"
        return v
        
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create settings instance
try:
    settings = Settings()
    
    # Configure logging based on settings
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
except Exception as e:
    # Fallback logging configuration if settings can't be loaded
    logging.basicConfig(level=logging.INFO)
    logger.error(f"Failed to load settings: {str(e)}")
    raise
