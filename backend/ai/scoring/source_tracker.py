"""
Source credibility tracking: record predictions, confirm/deny rumors (PROJECT_SPEC_CONTINUATION §5.5).
"""
from datetime import datetime, timezone
from typing import Optional


class SourceCredibilityTracker:
    """Tracks historical accuracy of leak sources; updates on rumor confirm/deny."""

    def __init__(self, db=None):
        self._db = db

    async def _get_db(self):
        if self._db is None:
            from backend.db.mongodb import MongoDBClient
            self._db = MongoDBClient()
            await self._db.connect()
        return self._db

    async def record_prediction(
        self,
        source_id: str,
        platform: str,
        rumor_id: str,
        prediction_text: str,
    ):
        """Record that a source made a prediction (leak claim)."""
        db = await self._get_db()
        await db.db.sources.update_one(
            {"username": source_id, "platform": platform},
            {
                "$push": {
                    "predictions": {
                        "rumor_id": rumor_id,
                        "text": prediction_text[:500],
                        "date": datetime.now(timezone.utc).isoformat(),
                        "outcome": "pending",
                    }
                },
                "$inc": {"total_predictions": 1},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

    async def confirm_rumor(self, rumor_id: str, confirmed: bool):
        """When a rumor is confirmed or denied, update all contributing sources."""
        db = await self._get_db()
        outcome = "correct" if confirmed else "incorrect"
        cursor = db.db.sources.find({"predictions.rumor_id": rumor_id})
        async for source in cursor:
            await db.db.sources.update_one(
                {
                    "username": source.get("username"),
                    "platform": source.get("platform"),
                    "predictions.rumor_id": rumor_id,
                },
                {
                    "$set": {"predictions.$.outcome": outcome},
                    "$inc": {f"outcomes.{outcome}": 1},
                },
            )
            await self._recalculate_accuracy(db, source.get("username"), source.get("platform"))

    async def _recalculate_accuracy(self, db, source_id: str, platform: str):
        source = await db.db.sources.find_one(
            {"username": source_id, "platform": platform}
        )
        if not source:
            return
        outcomes = source.get("outcomes", {})
        correct = outcomes.get("correct", 0)
        incorrect = outcomes.get("incorrect", 0)
        total_resolved = correct + incorrect
        accuracy = correct / total_resolved if total_resolved > 0 else 0.0
        tier = "unknown"
        if total_resolved >= 20 and accuracy >= 0.80:
            tier = "elite"
        elif total_resolved >= 10 and accuracy >= 0.65:
            tier = "verified"
        elif total_resolved >= 5:
            tier = "established"
        elif total_resolved >= 1:
            tier = "new"
        await db.db.sources.update_one(
            {"username": source_id, "platform": platform},
            {
                "$set": {
                    "accuracy_rate": round(accuracy, 3),
                    "tier": tier,
                    "total_resolved": total_resolved,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
