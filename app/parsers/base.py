import abc
import logging
from typing import List, Dict, Any
import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

class BaseParser(abc.ABC):
    """
    Abstract Base Class for all multi-domain parsers in Sport, Supplements & Events Hub.
    """
    def __init__(self, name: str, source: str, timeout: float = 15.0):
        self.name = name
        self.source = source
        self.timeout = timeout
        self.client = httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True)

    async def fetch_html(self, url: str) -> str:
        """Helper to fetch raw HTML content with error handling."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"[{self.name}] Failed to fetch URL {url}: {e}")
            raise

    async def fetch_json(self, url: str) -> Dict[str, Any]:
        """Helper to fetch JSON API endpoints."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[{self.name}] Failed to fetch JSON {url}: {e}")
            raise

    @abc.abstractmethod
    async def parse(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Parses source items and returns structured dictionaries."""
        pass

    @abc.abstractmethod
    def save_items(self, db: Session, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Saves or updates parsed items into database."""
        pass

    async def close(self):
        """Clean up HTTP client."""
        await self.client.aclose()
