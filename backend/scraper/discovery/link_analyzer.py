"""
Outbound link analysis for domain discovery (PROJECT_SPEC_CONTINUATION §1.4).
"""
from urllib.parse import urlparse
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class DiscoveredDomain:
    domain: str
    source_url: str
    context: str
    discovery_date: str
    leak_proximity_score: float


class OutboundLinkAnalyzer:
    """Extracts and scores outbound links from pages for tech-leak relevance."""

    EXCLUDED_DOMAINS = {
        "google.com", "facebook.com", "instagram.com", "youtube.com",
        "amazon.com", "wikipedia.org", "linkedin.com", "tiktok.com",
        "pinterest.com", "twitter.com", "x.com", "reddit.com",
    }

    TECH_DOMAIN_KEYWORDS = [
        "tech", "leak", "rumor", "gadget", "hardware", "phone", "chip",
        "gpu", "cpu", "apple", "nvidia", "intel", "samsung", "google",
        "benchmark", "spec", "review", "news",
    ]

    def __init__(self, db_client=None):
        self.db = db_client

    def extract_outbound_links(self, html: str, source_url: str) -> List[Dict]:
        """Extract all outbound links from HTML."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return []
        soup = BeautifulSoup(html, "html.parser")
        source_domain = urlparse(source_url).netloc.lower()
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = (a_tag.get("href") or "").strip()
            if not href or href.startswith("#"):
                continue
            parsed = urlparse(href)
            netloc = (parsed.netloc or "").lower()
            if not netloc or netloc == source_domain:
                continue
            if netloc in self.EXCLUDED_DOMAINS:
                continue
            anchor = a_tag.get_text(strip=True)
            parent_text = (a_tag.parent.get_text(strip=True) if a_tag.parent else "")[:200]
            links.append({
                "url": href,
                "domain": netloc,
                "anchor_text": anchor,
                "context": parent_text,
                "source_url": source_url,
            })
        return links

    def score_domain(self, domain: str, links: List[Dict]) -> float:
        """Score a domain for tech-leak relevance (0.0–1.0)."""
        score = 0.0
        domain_lower = domain.lower()
        keyword_hits = sum(1 for kw in self.TECH_DOMAIN_KEYWORDS if kw in domain_lower)
        score += min(keyword_hits * 0.15, 0.45)
        for link in links:
            context = f"{link.get('anchor_text', '')} {link.get('context', '')}".lower()
            context_hits = sum(1 for kw in self.TECH_DOMAIN_KEYWORDS if kw in context)
            score += min(context_hits * 0.05, 0.2)
        return min(score, 1.0)
