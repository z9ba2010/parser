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
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"

    # Database configuration (SQLite by default for standalone run; PostgreSQL for production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sporthub.db")

    # AI / Vision configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    ENABLE_MOCK_VISION_FALLBACK: bool = os.getenv("ENABLE_MOCK_VISION_FALLBACK", "true").lower() in ("true", "1", "yes")

    # Proxy Infrastructure (e.g. Proxy6: http://user:pass@ip:port or comma-separated list)
    PROXIES_LIST: str = os.getenv("PROXIES_LIST", "")
    PROXY_FILE: str = os.getenv("PROXY_FILE", "proxies.txt")
    PROXY_TIMEOUT: float = float(os.getenv("PROXY_TIMEOUT", "15.0"))
    ROTATE_USER_AGENTS: bool = os.getenv("ROTATE_USER_AGENTS", "true").lower() in ("true", "1", "yes")

    # Automated Scheduling configuration
    ENABLE_PARSER_SCHEDULER: bool = os.getenv("ENABLE_PARSER_SCHEDULER", "false").lower() in ("true", "1", "yes")
    PARSER_INTERVAL_HOURS: int = int(os.getenv("PARSER_INTERVAL_HOURS", "6"))

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()
