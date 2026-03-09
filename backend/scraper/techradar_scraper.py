"""
TechRadar scraper: fetches article listings + body text.
"""
import hashlib
from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from backend.scraper.base import BaseScraper, RawPost
from backend.scraper.content_fetcher import fetch_articles_batch, USER_AGENT

logger = __import__("logging").getLogger("scraper.techradar")

TECHRADAR_URLS = [
    "https://www.techradar.com/phones",
    "https://www.techradar.com/computing",
    "https://www.techradar.com/tablets",
]


class TechRadarScraper(BaseScraper):
    def __init__(self, max_articles: int = 12, timeout_seconds: int = 15):
        super().__init__("techradar")
        self.max_articles = max_articles
        self.timeout = timeout_seconds

    SKIP_PATHS = {
        "/best", "/reviews", "/deals", "/coupons", "/software",
        "/phones", "/computing", "/tablets", "/news",
    }

    def _extract_article_links(self, html: str, base_url: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        seen = set()
        articles = []
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or "javascript:" in href:
                continue
            full = urljoin(base_url, href)
            if "techradar.com" not in urlparse(full).netloc:
                continue
            path = urlparse(full).path or ""
            if not path or path == "/":
                continue
            if path.count("/") < 2:
                continue
            skip = False
            for sp in self.SKIP_PATHS:
                if path.rstrip("/") == sp or path.startswith(sp + "/") and path.count("/") < 3:
                    skip = True
                    break
            if skip or "/coupons/" in path or "/best" in path:
                continue
            title = (a.get_text(strip=True) or "").strip()
            if len(title) < 20 or len(title) > 300:
                continue
            key = full.split("?")[0].split("#")[0]
            if key in seen:
                continue
            seen.add(key)
            articles.append({"url": key, "title": title})
            if len(articles) >= self.max_articles:
                break
        return articles

    async def scrape(self) -> List[RawPost]:
        posts: List[RawPost] = []
        now = datetime.now(timezone.utc)
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(self.timeout),
            headers={"User-Agent": USER_AGENT},
        ) as client:
            all_articles = []
            for url in TECHRADAR_URLS:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    items = self._extract_article_links(resp.text, url)
                    all_articles.extend(items)
                    logger.info("TechRadar listing %s: %d links", url, len(items))
                except Exception as e:
                    logger.warning("TechRadar listing %s failed: %s", url, e)

            seen_urls = set()
            unique = []
            for a in all_articles:
                if a["url"] not in seen_urls:
                    seen_urls.add(a["url"])
                    unique.append(a)
            unique = unique[: self.max_articles]

            enriched = await fetch_articles_batch(client, unique)

            for item in enriched:
                body = item.get("body") or ""
                content = f"{item['title']}. {body}".strip() if body else item["title"]
                sid = hashlib.sha256(item["url"].encode()).hexdigest()[:24]
                posts.append(
                    RawPost(
                        source_platform="techradar.com",
                        source_id=sid,
                        source_url=item["url"],
                        author_username="techradar",
                        author_display_name="TechRadar",
                        content=content,
                        title=item["title"],
                        published_at=now,
                        scraped_at=now,
                        engagement={},
                    )
                )
            logger.info("TechRadar total: %d posts with content", len(posts))
        return posts

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5, headers={"User-Agent": USER_AGENT}) as c:
                r = await c.get("https://www.techradar.com/")
                return r.status_code == 200
        except Exception:
            return False
