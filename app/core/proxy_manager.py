import os
import random
import logging
from typing import List, Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Modern realistic User-Agent rotation pool for anti-fraud bypass
USER_AGENTS = [
    # Chrome on Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Safari on macOS Sonoma
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    # Mobile Safari on iPhone (iOS 17.5)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    # Chrome on Android 14 (Samsung Galaxy)
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
]

class ProxyManager:
    """
    Manages proxy pool rotation (e.g. Proxy6 HTTP/SOCKS5), health checking,
    and anti-detection request headers.
    """
    def __init__(self):
        self._proxies: List[str] = []
        self._failed_counts: Dict[str, int] = {}
        self._index: int = 0
        self.load_proxies()

    def load_proxies(self):
        """Loads proxies from environment or proxies.txt file."""
        proxies = []

        # 1. From settings PROXIES_LIST (comma-separated)
        if settings.PROXIES_LIST:
            for p in settings.PROXIES_LIST.split(","):
                p = p.strip()
                if p:
                    proxies.append(p)

        # 2. From proxy file if present
        if os.path.exists(settings.PROXY_FILE):
            try:
                with open(settings.PROXY_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            proxies.append(line)
            except Exception as e:
                logger.warning(f"Failed to read proxy file {settings.PROXY_FILE}: {e}")

        self._proxies = proxies
        if self._proxies:
            logger.info(f"Loaded {len(self._proxies)} proxies into rotation pool.")
        else:
            logger.info("No proxy list configured. Operating in direct connection mode.")

    def add_proxy(self, proxy_url: str):
        proxy_url = proxy_url.strip()
        if proxy_url and proxy_url not in self._proxies:
            self._proxies.append(proxy_url)

    def get_proxy(self) -> Optional[str]:
        """Returns the next healthy proxy via round-robin."""
        if not self._proxies:
            return None

        # Filter out proxies with excessive consecutive errors (> 5)
        healthy = [p for p in self._proxies if self._failed_counts.get(p, 0) < 5]
        if not healthy:
            # If all marked failed, reset failure counters to retry
            self._failed_counts.clear()
            healthy = self._proxies

        self._index = (self._index + 1) % len(healthy)
        return healthy[self._index]

    def report_success(self, proxy_url: Optional[str]):
        if proxy_url and proxy_url in self._failed_counts:
            self._failed_counts[proxy_url] = 0

    def report_failure(self, proxy_url: Optional[str]):
        if proxy_url:
            self._failed_counts[proxy_url] = self._failed_counts.get(proxy_url, 0) + 1
            logger.warning(f"Proxy {proxy_url} reported failure (count={self._failed_counts[proxy_url]})")

    def get_random_headers(self) -> Dict[str, str]:
        """
        Generates realistic browser headers to evade antifraud/anti-bot systems.
        """
        ua = random.choice(USER_AGENTS)
        is_mobile = "Mobile" in ua

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Ch-Ua-Mobile": "?1" if is_mobile else "?0",
            "Sec-Ch-Ua-Platform": '"Android"' if "Android" in ua else ('"iOS"' if "iPhone" in ua else '"Windows"'),
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        return headers

    def get_status(self) -> Dict[str, Any]:
        return {
            "total_proxies": len(self._proxies),
            "healthy_proxies": len([p for p in self._proxies if self._failed_counts.get(p, 0) < 5]),
            "failed_proxies": len([p for p in self._proxies if self._failed_counts.get(p, 0) >= 5]),
            "active_proxies": self._proxies
        }

proxy_manager = ProxyManager()
