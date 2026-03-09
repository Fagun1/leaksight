import math
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger("services.credibility")


class CredibilityScorer:
    """Computes credibility scores for rumors."""

    WEIGHTS = {
        "source_accuracy": 0.30,
        "corroboration": 0.25,
        "authority": 0.10,
        "engagement_velocity": 0.10,
        "specificity": 0.10,
        "temporal_consistency": 0.10,
        "media_evidence": 0.05,
    }

    def __init__(self):
        self.db = None

    async def _get_db(self):
        if self.db is None:
            from backend.db.mongodb import MongoDBClient
            self.db = MongoDBClient()
            await self.db.connect()
        return self.db

    async def score_rumor(self, rumor_id: str) -> float:
        db = await self._get_db()
        rumor = await db.get_rumor(rumor_id)
        if not rumor:
            return 0.0
        signals = {}
        signals["source_accuracy"] = 0.5
        posts = await db.get_posts_for_rumor(rumor_id)
        n_sources = len(set((p.get("author_username", ""), p.get("source_platform", "")) for p in posts))
        signals["corroboration"] = min(1.0, math.log(max(n_sources, 1) + 1) / 3.0)
        signals["authority"] = 0.3
        total_engagement = sum(p.get("engagement_score", 0) for p in posts)
        age_hours = max(1, (datetime.now(timezone.utc) - rumor.get("first_seen", datetime.now(timezone.utc))).total_seconds() / 3600)
        signals["engagement_velocity"] = min(1.0, (total_engagement / age_hours) * 10)
        entities = rumor.get("entities", {})
        entity_count = sum(len(v) for v in entities.values() if isinstance(v, list))
        signals["specificity"] = min(1.0, entity_count / 5.0)
        signals["temporal_consistency"] = 0.6
        has_media = any(len(p.get("media_urls", [])) > 0 for p in posts)
        signals["media_evidence"] = 1.0 if has_media else 0.0
        score = sum(self.WEIGHTS[k] * signals.get(k, 0) for k in self.WEIGHTS)
        final_score = round(score * 100, 1)
        await db.update_rumor(rumor_id, {
            "credibility_score": final_score,
            "credibility_signals": signals,
            "scored_at": datetime.now(timezone.utc),
        })
        return final_score
