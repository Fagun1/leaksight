"""
Forum scraper: collects thread listings from tech forums and fetches thread content.
"""
import hashlib
import re
from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from backend.scraper.base import BaseScraper, RawPost
from backend.scraper.content_fetcher import fetch_articles_batch, USER_AGENT

logger = __import__("logging").getLogger("scraper.forum")

DEFAULT_FORUM_SEEDS = [
    {"url": "https://forums.macrumors.com/forums/iphone.100/", "category": "forum", "priority": 9},
    {"url": "https://forums.macrumors.com/forums/apple-silicon-and-m-series-chips.236/", "category": "forum", "priority": 8},
    {"url": "https://forums.macrumors.com/forums/mac-mini.38/", "category": "forum", "priority": 7},
]

THREAD_PATH_PATTERNS = (
    re.compile(r"/threads/", re.I),
    re.compile(r"/t\d+", re.I),
    re.compile(r"/topic/\d+", re.I),
    re.compile(r"-\d+\.html?$", re.I),
    re.compile(r"thread-\d+", re.I),
)


class ForumScraper(BaseScraper):
    def __init__(self, max_threads_per_forum: int = 15, timeout_seconds: int = 20):
        super().__init__("forum")
        self.max_threads_per_forum = max_threads_per_forum
        self.timeout = timeout_seconds

    async def _get_seed_urls(self) -> List[dict]:
        try:
            from backend.db.mongodb import MongoDBClient
            db = MongoDBClient()
            await db.connect()
            seeds = await db.get_seed_urls(active_only=True)
            forum_seeds = [s for s in seeds if (s.get("category") or "").lower() == "forum"]
            if forum_seeds:
                return [{"url": s["url"], "category": "forum", "priority": s.get("priority", 5)} for s in forum_seeds]
        except Exception as e:
            logger.warning("Could not load forum seeds from DB: %s", e)
        return DEFAULT_FORUM_SEEDS

    def _is_thread_url(self, base_netloc: str, href: str) -> bool:
        if not href or href.startswith("#") or href.startswith("javascript:"):
            return False
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc.lower() != base_netloc.lower():
            return False
        path = (parsed.path or "").strip("/")
        if len(path) < 5:
            return False
        return any(p.search("/" + path) for p in THREAD_PATH_PATTERNS)

    def _extract_threads_from_html(self, html: str, base_url: str, base_netloc: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        seen_urls = set()
        threads = []
        for a in soup.find_all("a", href=True):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            full_url = urljoin(base_url, href)
            if not self._is_thread_url(base_netloc, full_url):
                continue
            norm = full_url.split("?")[0].split("#")[0].rstrip("/")
            if norm in seen_urls:
                continue
            title = (a.get_text(strip=True) or "").strip()
            if len(title) < 10 or len(title) > 500:
                continue
            seen_urls.add(norm)
            threads.append({"url": full_url, "title": title})
            if len(threads) >= self.max_threads_per_forum:
                break
        return threads

    async def scrape(self) -> List[RawPost]:
        posts: List[RawPost] = []
        seeds = await self._get_seed_urls()
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(self.timeout),
            headers={"User-Agent": USER_AGENT},
        ) as client:
            all_threads = []
            for seed in seeds:
                url = (seed.get("url") or "").strip()
                if not url:
                    continue
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    base_netloc = urlparse(url).netloc
                    threads = self._extract_threads_from_html(resp.text, url, base_netloc)
                    all_threads.extend(threads)
                    logger.info("Forum %s: found %d threads", base_netloc, len(threads))
                except Exception as e:
                    logger.warning("Forum scrape failed for %s: %s", url, e)

            enriched = await fetch_articles_batch(client, all_threads)

            for item in enriched:
                body = item.get("body") or ""
                content = f"{item['title']}. {body}".strip() if body else item["title"]
                base_netloc = urlparse(item["url"]).netloc
                source_id = hashlib.sha256(item["url"].encode()).hexdigest()[:24]
                posts.append(
                    RawPost(
                        source_platform=base_netloc or "forum",
                        source_id=source_id,
                        source_url=item["url"],
                        author_username="forum_user",
                        author_display_name="Forum",
                        content=content,
                        title=item["title"],
                        published_at=now,
                        scraped_at=now,
                        engagement={},
                    )
                )
            logger.info("Forum total: %d posts with content", len(posts))
        return posts

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5, headers={"User-Agent": USER_AGENT}) as c:
                r = await c.get("https://forums.macrumors.com/")
                return r.status_code == 200
        except Exception:
            return False
