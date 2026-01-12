from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Riot API
    riot_api_key: str = ""
    riot_api_region: str = "americas"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    
    # Database
    chroma_persist_directory: str = "./data/chroma_db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Redis
    redis_url: Optional[str] = None
    
    # Data
    match_data_cache_dir: str = "./data/cache"
    playbooks_dir: str = "./data/playbooks"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
