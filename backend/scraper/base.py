from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class RawPost(BaseModel):
    """Standardized raw post from any source."""
    source_platform: str
    source_id: str
    source_url: str
    author_username: str
    author_display_name: str
    author_followers: Optional[int] = None
    author_verified: bool = False
    content: str
    title: Optional[str] = None
    published_at: datetime
    scraped_at: datetime
    engagement: dict = {}
    media_urls: List[str] = []
    hashtags: List[str] = []
    subreddit: Optional[str] = None
    metadata: dict = {}


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()

    def _setup_logger(self):
        import logging
        logger = logging.getLogger(f"scraper.{self.name}")
        logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    async def scrape(self) -> List[RawPost]:
        """Execute scraping and return list of RawPost objects."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the scraper can reach its source."""
        pass

    def get_name(self) -> str:
        return self.name
