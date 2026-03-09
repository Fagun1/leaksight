"""
robots.txt compliance check before crawling (PROJECT_SPEC_CONTINUATION §1.8).
"""
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Optional
import logging

logger = logging.getLogger("scraper.robots")

USER_AGENT = "TechLeakBot/1.0"


class RobotsChecker:
    """Checks robots.txt before crawling a URL. Cache in Redis optional."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._cache: dict = {}  # in-memory fallback
        self._cache_ttl = 86400

    async def is_allowed(self, url: str) -> bool:
        """Return True if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        netloc = parsed.netloc or ""
        robots_url = f"{parsed.scheme or 'https'}://{netloc}/robots.txt"
        cache_key = f"robots:{netloc}"

        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached is not None:
                    return self._check_content(cached, url)
            except Exception:
                pass

        if cache_key in self._cache:
            return self._check_content(self._cache[cache_key], url)

        content = await self._fetch_robots(robots_url)
        if self.redis and content is not None:
            try:
                await self.redis.set(cache_key, content, ex=self._cache_ttl)
            except Exception:
                pass
        self._cache[cache_key] = content or ""
        return self._check_content(content or "", url)

    def _check_content(self, robots_content: str, url: str) -> bool:
        if not robots_content.strip():
            return True
        rp = RobotFileParser()
        try:
            rp.parse(robots_content.splitlines())
            return bool(rp.can_fetch(USER_AGENT, url))
        except Exception:
            return True

    async def _fetch_robots(self, robots_url: str) -> Optional[str]:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(robots_url)
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            logger.debug(f"Could not fetch robots: {e}")
        return None
