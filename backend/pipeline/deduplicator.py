import hashlib
from backend.db.redis_client import RedisClient


class Deduplicator:
    """Detects and prevents duplicate posts."""

    CACHE_PREFIX = "dedup:"
    CACHE_TTL = 86400 * 7

    def __init__(self):
        self.redis = RedisClient()

    def compute_content_hash(self, text: str) -> str:
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def compute_source_hash(self, platform: str, source_id: str) -> str:
        key = f"{platform}:{source_id}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    async def is_duplicate(self, platform: str, source_id: str, content: str) -> bool:
        source_hash = self.compute_source_hash(platform, source_id)
        try:
            if await self.redis.exists(f"{self.CACHE_PREFIX}src:{source_hash}"):
                return True
        except Exception:
            pass
        content_hash = self.compute_content_hash(content)
        try:
            if await self.redis.exists(f"{self.CACHE_PREFIX}txt:{content_hash}"):
                return True
        except Exception:
            pass
        return False

    async def mark_seen(self, platform: str, source_id: str, content: str):
        source_hash = self.compute_source_hash(platform, source_id)
        content_hash = self.compute_content_hash(content)
        try:
            await self.redis.set_with_ttl(
                f"{self.CACHE_PREFIX}src:{source_hash}", "1", self.CACHE_TTL
            )
            await self.redis.set_with_ttl(
                f"{self.CACHE_PREFIX}txt:{content_hash}", "1", self.CACHE_TTL
            )
        except Exception:
            pass
