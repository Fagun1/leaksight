"""
HTML to plain-text extraction for crawl results (PROJECT_SPEC_CONTINUATION §3).
"""
import re
from typing import Optional


def extract_text_from_html(html: str, max_chars: int = 50000) -> str:
    """
    Extract main text from HTML. Strips scripts, styles, nav, footer.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return _fallback_strip(html)[:max_chars]

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()[:max_chars]


def _fallback_strip(html: str) -> str:
    """Strip tags when BeautifulSoup is not available."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
