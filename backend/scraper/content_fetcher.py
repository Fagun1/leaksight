"""
Shared utility: fetch article page and extract body text.
Used by all scrapers to get real article content for classification.
"""
import asyncio
import logging
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("scraper.content_fetcher")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

STRIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "iframe"}

ARTICLE_SELECTORS = [
    "article",
    '[itemprop="articleBody"]',
    ".article-body",
    ".article-content",
    ".entry-content",
    ".post-content",
    ".story-body",
    ".content-text",
    "#article-body",
    ".td-post-content",
    "main",
]


def extract_body_text(html: str, max_chars: int = 1500) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(STRIP_TAGS):
        tag.decompose()

    content_el = None
    for sel in ARTICLE_SELECTORS:
        content_el = soup.select_one(sel)
        if content_el:
            break
    if not content_el:
        content_el = soup.body or soup

    paragraphs = content_el.find_all("p")
    text_parts = []
    total = 0
    for p in paragraphs:
        t = p.get_text(separator=" ", strip=True)
        if len(t) < 15:
            continue
        text_parts.append(t)
        total += len(t)
        if total >= max_chars:
            break

    return " ".join(text_parts)[:max_chars]


async def fetch_article_text(
    client: httpx.AsyncClient,
    url: str,
    max_chars: int = 1500,
) -> Optional[str]:
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        text = extract_body_text(resp.text, max_chars)
        return text if len(text) >= 40 else None
    except Exception:
        return None


async def fetch_articles_batch(
    client: httpx.AsyncClient,
    articles: list,
    max_concurrent: int = 6,
) -> list:
    """Fetch body text for a batch of articles concurrently.
    Each article dict must have 'url' and 'title' keys.
    Returns the same list with 'body' key added.
    """
    sem = asyncio.Semaphore(max_concurrent)

    async def _fetch_one(article: dict) -> dict:
        async with sem:
            body = await fetch_article_text(client, article["url"])
            return {**article, "body": body}

    results = await asyncio.gather(*[_fetch_one(a) for a in articles])
    return list(results)
