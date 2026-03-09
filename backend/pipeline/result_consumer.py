"""
Consumes crawl results from Redis and runs NLP pipeline + storage (PROJECT_SPEC_CONTINUATION §2–3).
"""
import hashlib
import json
import logging
from datetime import datetime, timezone

from backend.pipeline.text_extractor import extract_text_from_html

logger = logging.getLogger("pipeline.consumer")


class ResultConsumer:
    """Reads from crawl:results, extracts text, runs pipeline, stores in MongoDB."""

    def __init__(self, redis_client=None, db=None):
        self._redis = redis_client
        self._db = db

    async def _get_redis(self):
        if self._redis is None:
            from backend.db.redis_client import RedisClient
            self._redis = RedisClient()
            await self._redis.connect()
        return self._redis

    async def _get_db(self):
        if self._db is None:
            from backend.db.mongodb import MongoDBClient
            self._db = MongoDBClient()
            await self._db.connect()
        return self._db

    async def run_once(self) -> bool:
        """Process one item from crawl:results. Returns True if one was processed."""
        redis = await self._get_redis()
        raw = await redis.dequeue("crawl:results")
        if not raw:
            return False
        try:
            payload = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
        except Exception as e:
            logger.warning("result_consumer: invalid json %s", e)
            return True
        await self._process_result(payload)
        return True

    async def _process_result(self, payload: dict):
        url = payload.get("url", "")
        html = payload.get("html", "")
        domain = payload.get("domain", "")
        source_type = payload.get("source_type", "generic")
        full_text = extract_text_from_html(html)
        if not full_text or len(full_text) < 50:
            logger.debug("result_consumer: skip short content url=%s", url)
            return
        source_id = hashlib.sha256(url.encode()).hexdigest()[:24]
        post = {
            "source_platform": domain or source_type,
            "source_id": source_id,
            "source_url": url,
            "author_username": "crawl",
            "author_display_name": "",
            "content": full_text,
            "title": full_text[:200],
            "published_at": payload.get("fetched_at") or datetime.now(timezone.utc),
            "scraped_at": datetime.now(timezone.utc),
            "engagement": {},
        }
        db = await self._get_db()
        from backend.pipeline.deduplicator import Deduplicator
        from backend.pipeline.language_filter import LanguageFilter
        from backend.pipeline.enricher import PostEnricher
        from backend.ai.classifier import LeakClassifier
        from backend.ai.entity_extractor import EntityExtractor
        dedup = Deduplicator()
        try:
            await dedup.redis.connect()
        except Exception:
            pass
        lang_filter = LanguageFilter()
        enricher = PostEnricher()
        classifier = LeakClassifier()
        entity_extractor = EntityExtractor()
        content = post.get("content", "") or post.get("title", "")
        if not lang_filter.is_accepted(content):
            return
        if await dedup.is_duplicate(post["source_platform"], post["source_id"], content):
            return
        enriched = enricher.enrich(post)
        full_text = enriched.get("full_text", content)
        result = classifier.classify(full_text)
        enriched["is_leak"] = result.is_leak
        enriched["leak_confidence"] = result.confidence
        enriched["leak_category"] = "HARDWARE_LEAK" if result.is_leak else "NONE"
        entities = entity_extractor.extract(full_text)
        enriched["entities"] = {
            "companies": entities.companies,
            "products": entities.products,
            "features": entities.features,
        }
        enriched["source_domain"] = domain
        post_id = await db.insert_post(enriched)
        await dedup.mark_seen(post["source_platform"], post["source_id"], content)
        if result.is_leak:
            rumor_id = await db.insert_rumor({
                "title": post.get("title") or full_text[:100],
                "summary": full_text[:300],
                "category": "HARDWARE_LEAK",
                "status": "active",
                "credibility_score": round(result.confidence * 100, 1),
                "trend_score": 50.0,
                "first_seen": post.get("published_at"),
                "last_seen": datetime.now(timezone.utc),
                "post_ids": [post_id],
                "entities": enriched["entities"],
            })
            from bson import ObjectId
            await db.db.posts.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"rumor_id": rumor_id}},
            )
        logger.info("result_consumer: stored post url=%s", url)
