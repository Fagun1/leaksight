"""
Distributed crawl worker: pulls tasks from Redis queues (PROJECT_SPEC_CONTINUATION §2.3).
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

logger = __import__("logging").getLogger("scraper.worker")


class CrawlWorker:
    """Pulls crawl tasks from Redis priority queues, fetches pages, pushes to crawl:results."""

    QUEUES = ["crawl:queue:high", "crawl:queue:medium", "crawl:queue:low"]
    RESULTS_QUEUE = "crawl:results"
    HEARTBEAT_INTERVAL = 30
    MAX_RETRIES = 3

    def __init__(self, worker_id: str, redis_url: Optional[str] = None):
        self.worker_id = worker_id
        self._redis_url = redis_url
        self.redis: Optional[object] = None
        self.running = False
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

    async def connect(self):
        import redis.asyncio as aioredis
        from backend.config import settings
        url = self._redis_url or getattr(settings, "redis_url", "redis://localhost:6379")
        self.redis = aioredis.from_url(url, decode_responses=True)

    async def start(self):
        await self.connect()
        self.running = True
        asyncio.create_task(self._heartbeat_loop())
        while self.running:
            task = await self._dequeue_task()
            if task:
                await self._process_task(task)
            else:
                await asyncio.sleep(1)

    async def _dequeue_task(self) -> Optional[dict]:
        for queue in self.QUEUES:
            result = await self.redis.lpop(queue)
            if result:
                return json.loads(result)
        return None

    async def _process_task(self, task: dict):
        url = task.get("url", "")
        domain = task.get("domain", "") or urlparse(url).netloc
        attempt = task.get("attempt", 1)
        source_type = task.get("source_type", "generic")

        lock_acquired = await self._acquire_domain_lock(domain)
        if not lock_acquired:
            await self._requeue(task, 10)
            return
        try:
            result = await self._fetch_page(url)
            await self.redis.rpush(
                self.RESULTS_QUEUE,
                json.dumps({
                    "url": url,
                    "domain": domain,
                    "source_type": source_type,
                    "html": result.get("html", ""),
                    "status_code": result.get("status_code", 0),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "worker_id": self.worker_id,
                    "response_time_ms": result.get("response_time_ms", 0),
                }),
            )
            self.stats["tasks_completed"] += 1
        except Exception as e:
            if attempt < self.MAX_RETRIES:
                task["attempt"] = attempt + 1
                await self._requeue(task, 2 ** attempt * 5)
            else:
                await self.redis.rpush(
                    "crawl:failures",
                    json.dumps({
                        "url": url,
                        "error": str(e),
                        "attempts": attempt,
                        "worker_id": self.worker_id,
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                    }),
                )
                self.stats["tasks_failed"] += 1
        finally:
            await self._release_domain_lock(domain)

    async def _acquire_domain_lock(self, domain: str, ttl: int = 30) -> bool:
        lock_key = f"crawl:lock:{domain}"
        return bool(await self.redis.set(lock_key, self.worker_id, nx=True, ex=ttl))

    async def _release_domain_lock(self, domain: str):
        lock_key = f"crawl:lock:{domain}"
        cur = await self.redis.get(lock_key)
        if cur == self.worker_id:
            await self.redis.delete(lock_key)

    async def _requeue(self, task: dict, delay_seconds: int):
        execute_at = time.time() + delay_seconds
        await self.redis.zadd("crawl:delayed", {json.dumps(task): execute_at})

    async def _fetch_page(self, url: str) -> dict:
        start = time.time()
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={"User-Agent": "TechLeakBot/1.0 (+https://techleakplatform.example/bot)"},
                ) as resp:
                    html = await resp.text()
                    return {
                        "html": html,
                        "status_code": resp.status,
                        "response_time_ms": int((time.time() - start) * 1000),
                    }
        except Exception as e:
            logger.warning("fetch failed url=%s %s", url, e)
            return {
                "html": "",
                "status_code": 0,
                "response_time_ms": int((time.time() - start) * 1000),
            }

    async def _heartbeat_loop(self):
        while self.running:
            await self.redis.hset(
                "crawl:workers",
                self.worker_id,
                json.dumps({
                    "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                    "stats": self.stats,
                }),
            )
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def stop(self):
        self.running = False
