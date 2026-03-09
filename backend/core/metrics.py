"""
Metrics collection in Redis; /metrics endpoint (PROJECT_SPEC_CONTINUATION §9.3).
"""
import time
from functools import wraps
from typing import Optional


class MetricsCollector:
    """Collects counters/gauges/histograms in Redis."""

    def __init__(self, redis_client=None):
        self._redis = redis_client

    async def _get_redis(self):
        if self._redis is None:
            from backend.db.redis_client import RedisClient
            self._redis = RedisClient()
            await self._redis.connect()
        return self._redis

    async def increment(self, metric: str, value: int = 1, tags: Optional[dict] = None):
        key = f"metrics:counter:{metric}"
        r = await self._get_redis()
        if r.client:
            await r.client.incrby(key, value)
        if tags:
            for k, v in tags.items():
                tk = f"metrics:counter:{metric}:{k}:{v}"
                if r.client:
                    await r.client.incrby(tk, value)

    async def gauge(self, metric: str, value: float):
        r = await self._get_redis()
        if r.client:
            await r.client.set(f"metrics:gauge:{metric}", value)

    async def histogram(self, metric: str, value: float):
        r = await self._get_redis()
        if r.client:
            key = f"metrics:histogram:{metric}"
            await r.client.lpush(key, value)
            await r.client.ltrim(key, 0, 999)

    async def get_all_metrics(self) -> dict:
        r = await self._get_redis()
        if not r.client:
            return {}
        metrics = {}
        async for key in r.client.scan_iter("metrics:counter:*"):
            val = await r.client.get(key)
            name = key.replace("metrics:counter:", "", 1) if isinstance(key, str) else key.decode().replace("metrics:counter:", "", 1)
            metrics[f"counter_{name}"] = int(val or 0)
        async for key in r.client.scan_iter("metrics:gauge:*"):
            val = await r.client.get(key)
            name = key.replace("metrics:gauge:", "", 1) if isinstance(key, str) else key.decode().replace("metrics:gauge:", "", 1)
            metrics[f"gauge_{name}"] = float(val or 0)
        return metrics


def track_duration(metrics: MetricsCollector, metric_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                await metrics.histogram(f"{metric_name}_duration_ms", (time.time() - start) * 1000)
                await metrics.increment(f"{metric_name}_success")
                return result
            except Exception:
                await metrics.histogram(f"{metric_name}_duration_ms", (time.time() - start) * 1000)
                await metrics.increment(f"{metric_name}_error")
                raise
        return wrapper
    return decorator
