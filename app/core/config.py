from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "FormulaHub API"
    
    # CORS Configuration
    backend_cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Cache Configuration
    redis_url: Optional[str] = "redis://localhost:6379"
    cache_ttl: int = 3600  # 1 hour default cache TTL
    
    # FastF1 Configuration
    fastf1_cache_dir: str = "./cache"
    fastf1_verbose: bool = False
    
    # Data Configuration
    current_season: int = 2025
    supported_seasons: list = [2020, 2021, 2022, 2023, 2024, 2025]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure cache directory exists
os.makedirs(settings.fastf1_cache_dir, exist_ok=True)
