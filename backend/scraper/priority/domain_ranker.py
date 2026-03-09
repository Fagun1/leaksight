"""
Domain priority scoring for crawl frequency (PROJECT_SPEC_CONTINUATION §1.7).
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DomainStats:
    domain: str
    total_crawls: int
    total_leaks_found: int
    avg_leak_confidence: float
    last_leak_date: Optional[str] = None
    uptime_ratio: float = 1.0
    avg_response_time_ms: float = 0.0


def compute_domain_priority(stats: DomainStats) -> float:
    """
    Priority score 0.0–10.0. Higher = crawl more often.
    """
    leak_yield = 0.0
    if stats.total_crawls > 0:
        leak_yield = min(stats.total_leaks_found / stats.total_crawls, 1.0)

    recency_bonus = 0.0
    if stats.last_leak_date:
        try:
            last = datetime.fromisoformat(stats.last_leak_date.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days_since = (now - last).days
            if days_since <= 1:
                recency_bonus = 1.0
            elif days_since <= 7:
                recency_bonus = 0.7
            elif days_since <= 30:
                recency_bonus = 0.4
            else:
                recency_bonus = 0.1
        except Exception:
            recency_bonus = 0.2

    speed_bonus = 0.0
    if stats.avg_response_time_ms < 500:
        speed_bonus = 1.0
    elif stats.avg_response_time_ms < 1500:
        speed_bonus = 0.5

    priority = (
        leak_yield * 4.0
        + (stats.avg_leak_confidence or 0) * 2.0
        + recency_bonus * 2.0
        + stats.uptime_ratio * 1.0
        + speed_bonus * 1.0
    )
    return round(min(priority, 10.0), 2)
