"""
Data retention policies and cleanup job (PROJECT_SPEC_CONTINUATION §10.6).
"""
from datetime import datetime, timezone, timedelta
from typing import Optional


class DataRetentionManager:
    """Enforces retention policies; run daily as a cron job."""

    RETENTION_POLICIES = {
        "raw_pages": 30,
        "posts": 180,
        "rumors": 365,
        "trend_stats": 365,
    }

    def __init__(self, db=None):
        self._db = db

    async def _get_db(self):
        if self._db is None:
            from backend.db.mongodb import MongoDBClient
            self._db = MongoDBClient()
            await self._db.connect()
        return self._db

    async def run_cleanup(self) -> dict:
        """Delete documents older than retention period. Returns counts deleted."""
        db = await self._get_db()
        now = datetime.now(timezone.utc)
        result = {}
        for collection_name, days in self.RETENTION_POLICIES.items():
            if not hasattr(db.db, collection_name):
                continue
            cutoff = now - timedelta(days=days)
            cutoff_str = cutoff.isoformat()
            try:
                coll = getattr(db.db, collection_name)
                r = await coll.delete_many({"created_at": {"$lt": cutoff_str}})
                result[collection_name] = r.deleted_count
            except Exception:
                try:
                    r = await coll.delete_many({"created_at": {"$lt": cutoff}})
                    result[collection_name] = r.deleted_count
                except Exception:
                    result[collection_name] = 0
        return result
