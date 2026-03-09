import json
import logging
from backend.pipeline.cleaner import TextCleaner
from backend.pipeline.deduplicator import Deduplicator
from backend.pipeline.language_filter import LanguageFilter
from backend.pipeline.enricher import PostEnricher

logger = logging.getLogger("pipeline")


class DataPipeline:
    """Orchestrates the full cleaning pipeline."""

    def __init__(self):
        self.cleaner = TextCleaner()
        self.dedup = Deduplicator()
        self.lang_filter = LanguageFilter()
        self.enricher = PostEnricher()
        self.db = None

    async def _get_db(self):
        if self.db is None:
            from backend.db.mongodb import MongoDBClient
            self.db = MongoDBClient()
            await self.db.connect()
        return self.db

    async def process_raw_post(self, raw_json: str) -> bool:
        try:
            post = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in pipeline queue")
            return False
        content = post.get("content", "") or post.get("title", "")
        if not self.lang_filter.is_accepted(content):
            return False
        is_dup = await self.dedup.is_duplicate(
            post["source_platform"], post["source_id"], content
        )
        if is_dup:
            return False
        enriched = self.enricher.enrich(post)
        db = await self._get_db()
        await db.insert_post(enriched)
        await self.dedup.mark_seen(
            post["source_platform"], post["source_id"], content
        )
        logger.info(f"Post processed: {post['source_platform']}:{post['source_id']}")
        return True
