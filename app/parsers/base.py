import abc
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from app.core.proxy_manager import proxy_manager

logger = logging.getLogger(__name__)

class BaseParser(abc.ABC):
    """
    Abstract Base Class for all multi-domain parsers in Sport, Supplements & Events Hub.
    Equipped with IP proxy rotation (Proxy6 / HTTP / SOCKS5), User-Agent spoofing,
    and anti-bot retry logic.
    """
    def __init__(self, name: str, source: str, timeout: float = 15.0, max_retries: int = 3):
        self.name = name
        self.source = source
        self.timeout = timeout
        self.max_retries = max_retries

    def _create_client(self, proxy_url: Optional[str] = None) -> httpx.AsyncClient:
        headers = proxy_manager.get_random_headers()
        return httpx.AsyncClient(
            headers=headers,
            proxy=proxy_url,
            timeout=self.timeout,
            follow_redirects=True,
            verify=False
        )

    async def fetch_html(self, url: str) -> str:
        """
        Fetches raw HTML with automated proxy rotation and header randomization.
        """
        for attempt in range(1, self.max_retries + 1):
            proxy_url = proxy_manager.get_proxy()
            async with self._create_client(proxy_url=proxy_url) as client:
                try:
                    response = await client.get(url)
                    if response.status_code in (403, 429, 503):
                        logger.warning(f"[{self.name}] Received status {response.status_code} on attempt {attempt}. Rotating proxy...")
                        proxy_manager.report_failure(proxy_url)
                        await asyncio.sleep(attempt * 1.5)
                        continue

                    response.raise_for_status()
                    proxy_manager.report_success(proxy_url)
                    return response.text
                except Exception as e:
                    logger.warning(f"[{self.name}] Attempt {attempt} failed for {url} via proxy {proxy_url}: {e}")
                    proxy_manager.report_failure(proxy_url)
                    if attempt == self.max_retries:
                        raise
                    await asyncio.sleep(attempt * 1.0)
        raise RuntimeError(f"[{self.name}] Failed to fetch {url} after {self.max_retries} attempts.")

    async def fetch_json(self, url: str) -> Dict[str, Any]:
        """
        Fetches JSON API endpoints with proxy and headers.
        """
        for attempt in range(1, self.max_retries + 1):
            proxy_url = proxy_manager.get_proxy()
            async with self._create_client(proxy_url=proxy_url) as client:
                try:
                    response = await client.get(url)
                    if response.status_code in (403, 429, 503):
                        proxy_manager.report_failure(proxy_url)
                        await asyncio.sleep(attempt * 1.5)
                        continue
                    response.raise_for_status()
                    proxy_manager.report_success(proxy_url)
                    return response.json()
                except Exception as e:
                    proxy_manager.report_failure(proxy_url)
                    if attempt == self.max_retries:
                        raise
                    await asyncio.sleep(attempt * 1.0)
        raise RuntimeError(f"[{self.name}] Failed to fetch JSON {url} after {self.max_retries} attempts.")

    @abc.abstractmethod
    async def parse(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Parses source items and returns structured dictionaries."""
        pass

    @abc.abstractmethod
    def save_items(self, db: Session, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Saves or updates parsed items into database."""
        pass

    async def close(self):
        """Clean up resources if needed."""
        pass
