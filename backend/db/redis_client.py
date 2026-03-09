import redis.asyncio as redis
from backend.config import settings
from typing import Optional
import logging

logger = logging.getLogger("db.redis")


class RedisClient:
    """Async Redis client for queues and caching."""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = redis.from_url(
            settings.redis_url, decode_responses=True
        )
        logger.info("Connected to Redis")

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def enqueue(self, queue_name: str, data: str):
        if self.client:
            await self.client.lpush(queue_name, data)

    async def dequeue(self, queue_name: str) -> Optional[str]:
        if self.client:
            return await self.client.rpop(queue_name)
        return None

    async def queue_length(self, queue_name: str) -> int:
        if self.client:
            return await self.client.llen(queue_name)
        return 0

    async def set_with_ttl(self, key: str, value: str, ttl: int):
        if self.client:
            await self.client.setex(key, ttl, value)

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            return await self.client.get(key)
        return None

    async def exists(self, key: str) -> bool:
        if self.client:
            return bool(await self.client.exists(key))
        return False

    async def set_cache(self, key: str, value: str, ttl: int = None):
        ttl = ttl or settings.redis_cache_ttl
        if self.client:
            await self.client.setex(f"cache:{key}", ttl, value)

    async def get_cache(self, key: str) -> Optional[str]:
        if self.client:
            return await self.client.get(f"cache:{key}")
        return None
