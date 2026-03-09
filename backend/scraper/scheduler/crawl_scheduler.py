"""
Crawl scheduler: enqueues seed URLs into Redis queues (PROJECT_SPEC_CONTINUATION §2).
"""
import json
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from backend.scraper.utils.url_normalizer import normalize_url

logger = logging.getLogger("scraper.scheduler")


class CrawlScheduler:
    """Loads seed URLs from DB and pushes due URLs to Redis priority queues."""

    QUEUES = {"high": "crawl:queue:high", "medium": "crawl:queue:medium", "low": "crawl:queue:low"}

    def __init__(self, db=None, redis_client=None):
        self._db = db
        self._redis = redis_client

    async def _get_db(self):
        if self._db is None:
            from backend.db.mongodb import MongoDBClient
            self._db = MongoDBClient()
            await self._db.connect()
        return self._db

    async def _get_redis(self):
        if self._redis is None:
            from backend.db.redis_client import RedisClient
            self._redis = RedisClient()
            await self._redis.connect()
        return self._redis

    async def run_once(self) -> int:
        """Enqueue seeds that are due for crawling. Returns count enqueued."""
        db = await self._get_db()
        redis = await self._get_redis()
        seeds = await db.get_seed_urls(active_only=True)
        now = datetime.now(timezone.utc)
        enqueued = 0
        for seed in seeds:
            url = seed.get("url", "").strip()
            if not url:
                continue
            normalized = normalize_url(url)
            domain = urlparse(normalized).netloc or seed.get("domain", "unknown")
            priority = seed.get("priority", 5)
            if priority >= 8:
                queue_name = self.QUEUES["high"]
            elif priority >= 5:
                queue_name = self.QUEUES["medium"]
            else:
                queue_name = self.QUEUES["low"]
            task = {
                "url": normalized,
                "domain": domain,
                "source_type": seed.get("category", "generic"),
                "seed_id": str(seed.get("_id", "")),
                "attempt": 1,
            }
            await redis.enqueue(queue_name, json.dumps(task))
            enqueued += 1
            logger.debug("enqueued %s -> %s", normalized, queue_name)
        return enqueued
