import asyncio
from typing import List, Dict
from datetime import datetime, timezone
from backend.scraper.base import RawPost
from backend.scraper.forum_scraper import ForumScraper
from backend.scraper.macrumors_scraper import MacRumorsScraper
from backend.scraper.notebookcheck_scraper import NotebookCheckScraper
from backend.scraper.techradar_scraper import TechRadarScraper
import logging

logger = logging.getLogger("scraper.manager")


class ScrapingManager:
    """Orchestrates scrapers: Forums, MacRumors, NotebookCheck, TechRadar. No API keys required."""

    def __init__(self):
        self.scrapers = [
            ForumScraper(),
            MacRumorsScraper(),
            NotebookCheckScraper(),
            TechRadarScraper(),
        ]
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            from backend.db.redis_client import RedisClient
            self.redis = RedisClient()
            await self.redis.connect()
        return self.redis

    async def run_all(self) -> Dict[str, int]:
        results = {}
        tasks = [self._run_scraper(s) for s in self.scrapers]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        for scraper, result in zip(self.scrapers, completed):
            if isinstance(result, Exception):
                logger.error("Scraper %s failed: %s", scraper.get_name(), result)
                results[scraper.get_name()] = 0
            else:
                results[scraper.get_name()] = len(result)
        return results

    async def _run_scraper(self, scraper) -> List[RawPost]:
        logger.info("Starting scraper %s", scraper.get_name())
        posts = await scraper.scrape()
        logger.info("Scraper %s returned %s posts", scraper.get_name(), len(posts))
        redis = await self._get_redis()
        for post in posts:
            await redis.enqueue("pipeline:raw_posts", post.model_dump_json())
        return posts
