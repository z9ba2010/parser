import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Sport, Supplements & Events Hub API"
    PROJECT_DESCRIPTION: str = (
        "Мультидоменный бэкенд и поисковая система: каталог экипировки и обуви с Visual Search, "
        "каталог спортивного питания и БАДов, единый агрегатор спортивных событий РФ для интеграции с MaxFunFit."
    )
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database configuration (SQLite by default for standalone run; PostgreSQL for production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sporthub.db")

    # AI / Vision configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    ENABLE_MOCK_VISION_FALLBACK: bool = os.getenv("ENABLE_MOCK_VISION_FALLBACK", "true").lower() in ("true", "1", "yes")

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()
