from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    model_name: str = "gemini-pro"
    temperature: float = 0.7
    max_output_tokens: int = 2048

    class Config:
        env_file = ".env"

settings = Settings()
