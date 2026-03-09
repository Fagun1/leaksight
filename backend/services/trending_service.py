from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import math
import logging

logger = logging.getLogger("services.trending")


def _ensure_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure datetime is timezone-aware for comparison."""
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class TrendingDetector:
    """Detects and ranks trending tech leaks."""

    def __init__(self):
        self.db = None

    async def _get_db(self):
        if self.db is None:
            from backend.db.mongodb import MongoDBClient
            self.db = MongoDBClient()
            await self.db.connect()
        return self.db

    async def compute_trending(self, top_n: int = 20) -> List[Dict]:
        db = await self._get_db()
        now = datetime.now(timezone.utc)
        window_48h = now - timedelta(hours=48)
        active_rumors = await db.get_rumors_since(window_48h)
        if not active_rumors:
            all_rumors = await db.get_rumors(skip=0, limit=50)
            active_rumors = all_rumors
        trending = []
        for rumor in active_rumors:
            rumor_id = str(rumor["_id"])
            posts = await db.get_posts_for_rumor(rumor_id)
            if not posts:
                posts = []
            window_6h = now - timedelta(hours=6)
            window_12h = now - timedelta(hours=12)
            pt_get = lambda p: _ensure_aware(p.get("published_at")) or now
            mentions_6h = len([p for p in posts if pt_get(p) >= window_6h])
            mentions_prev_6h = len([p for p in posts if window_12h <= pt_get(p) < window_6h])
            total_mentions = len(posts)
            unique_sources = len(set((p.get("source_platform"), p.get("author_username")) for p in posts))
            first_seen = _ensure_aware(rumor.get("first_seen")) or now
            hours_since_first = max(1, (now - first_seen).total_seconds() / 3600)
            velocity = mentions_6h
            acceleration = (mentions_6h - mentions_prev_6h) / max(mentions_prev_6h, 1)
            diversity = unique_sources / max(total_mentions, 1)
            recency = 1.0 / (1.0 + hours_since_first / 48.0)
            trend_score = velocity * 0.4 + max(0, acceleration) * 0.3 + diversity * 0.2 + recency * 0.1
            trending.append({
                "rumor_id": rumor_id,
                "title": rumor.get("title", "Unknown Rumor"),
                "summary": rumor.get("summary", ""),
                "trend_score": round(trend_score, 4),
                "velocity": velocity,
                "acceleration": round(acceleration, 2),
                "total_mentions": total_mentions,
                "unique_sources": unique_sources,
                "unique_platforms": len(set(p.get("source_platform") for p in posts)),
                "credibility_score": rumor.get("credibility_score", 0),
                "first_seen": first_seen,
                "last_seen": rumor.get("last_seen", now),
                "entities": rumor.get("entities", {}),
                "category": rumor.get("category", "UNKNOWN"),
            })
        if trending:
            max_vel = max(t["velocity"] for t in trending) or 1
            for t in trending:
                hrs = max(1, (now - t["first_seen"]).total_seconds() / 3600)
                t["trend_score"] = round(
                    (t["velocity"] / max_vel) * 0.4
                    + max(0, t["acceleration"]) * 0.3
                    + (t["unique_sources"] / max(t["total_mentions"], 1)) * 0.2
                    + (1.0 / (1.0 + hrs / 48.0)) * 0.1,
                    1
                )
        trending.sort(key=lambda x: x["trend_score"], reverse=True)
        await db.save_trend_snapshot({
            "computed_at": now,
            "top_rumors": trending[:top_n],
            "total_active_rumors": len(active_rumors),
        })
        return trending[:top_n]

    async def get_rumor_timeline(self, rumor_id: str) -> List[Dict]:
        db = await self._get_db()
        posts = await db.get_posts_for_rumor(rumor_id)
        posts.sort(key=lambda p: p.get("published_at", datetime.min))
        return [
            {
                "timestamp": p.get("published_at"),
                "source": p.get("source_platform"),
                "author": p.get("author_username"),
                "snippet": (p.get("cleaned_content", "") or "")[:200],
                "engagement": p.get("engagement_score", 0),
                "url": p.get("source_url"),
            }
            for p in posts
        ]
