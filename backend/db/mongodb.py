from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger("db.mongodb")


class MongoDBClient:
    """Async MongoDB client using Motor."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.mongo_db_name]
        await self._ensure_indexes()
        logger.info(f"Connected to MongoDB: {settings.mongo_db_name}")

    async def disconnect(self):
        if self.client:
            self.client.close()

    async def _ensure_indexes(self):
        try:
            await self.db.posts.create_index(
                [("source_platform", 1), ("source_id", 1)], unique=True
            )
            await self.db.posts.create_index([("published_at", -1)])
            await self.db.posts.create_index([("is_leak", 1)])
            await self.db.posts.create_index([("rumor_id", 1)])
            await self.db.rumors.create_index([("credibility_score", -1)])
            await self.db.rumors.create_index([("first_seen", -1)])
            await self.db.rumors.create_index([("trend_score", -1)])
            await self.db.rumors.create_index([("status", 1)])
            await self.db.sources.create_index(
                [("username", 1), ("platform", 1)], unique=True
            )
            await self.db.sources.create_index([("credibility_score", -1)])
            await self.db.entities.create_index([("name", 1), ("type", 1)])
            await self.db.trend_stats.create_index([("computed_at", -1)])
            await self.db.seed_urls.create_index([("domain", 1)])
            await self.db.seed_urls.create_index([("is_active", 1), ("priority", -1)])
            logger.info("MongoDB indexes ensured")
        except Exception as e:
            logger.warning(f"Index creation: {e}")

    async def insert_post(self, post: dict) -> str:
        result = await self.db.posts.insert_one(post)
        return str(result.inserted_id)

    async def get_post(self, post_id: str) -> Optional[dict]:
        try:
            return await self.db.posts.find_one({"_id": ObjectId(post_id)})
        except Exception:
            return None

    async def get_posts(
        self,
        skip: int = 0,
        limit: int = 50,
        is_leak: Optional[bool] = None,
        platform: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[dict]:
        query = {}
        if is_leak is not None:
            query["is_leak"] = is_leak
        if platform:
            query["source_platform"] = platform
        if since:
            query["published_at"] = {"$gte": since}
        cursor = self.db.posts.find(query).sort("published_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_posts_for_rumor(self, rumor_id: str) -> List[dict]:
        try:
            cursor = self.db.posts.find({"rumor_id": rumor_id})
            return await cursor.to_list(length=1000)
        except Exception:
            return []

    async def count_posts(self, query: dict = None) -> int:
        return await self.db.posts.count_documents(query or {})

    async def insert_rumor(self, rumor: dict) -> str:
        result = await self.db.rumors.insert_one(rumor)
        return str(result.inserted_id)

    async def get_rumor(self, rumor_id: str) -> Optional[dict]:
        try:
            return await self.db.rumors.find_one({"_id": ObjectId(rumor_id)})
        except Exception:
            return None

    async def get_rumors(
        self,
        skip: int = 0,
        limit: int = 50,
        min_credibility: Optional[float] = None,
        category: Optional[str] = None,
        company: Optional[str] = None,
    ) -> List[dict]:
        query = {}
        if min_credibility is not None:
            query["credibility_score"] = {"$gte": min_credibility}
        if category:
            query["category"] = category
        if company:
            query["entities.companies"] = company
        cursor = (
            self.db.rumors.find(query)
            .sort("credibility_score", -1)
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_rumors_since(self, since: datetime) -> List[dict]:
        cursor = self.db.rumors.find({"last_seen": {"$gte": since}})
        return await cursor.to_list(length=10000)

    async def update_rumor(self, rumor_id: str, update: dict):
        await self.db.rumors.update_one(
            {"_id": ObjectId(rumor_id)}, {"$set": update}
        )

    async def upsert_source(self, source: dict):
        await self.db.sources.update_one(
            {"username": source["username"], "platform": source["platform"]},
            {"$set": source},
            upsert=True,
        )

    async def get_source_by_username(
        self, username: str, platform: str
    ) -> Optional[dict]:
        return await self.db.sources.find_one(
            {"username": username, "platform": platform}
        )

    async def get_top_sources(self, limit: int = 20) -> List[dict]:
        cursor = (
            self.db.sources.find()
            .sort("credibility_score", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def upsert_entity(self, entity: dict):
        await self.db.entities.update_one(
            {"name": entity["name"], "type": entity["type"]},
            {
                "$set": entity,
                "$inc": {"mention_count": 1},
            },
            upsert=True,
        )

    async def get_entities(
        self, entity_type: Optional[str] = None, limit: int = 50
    ) -> List[dict]:
        query = {}
        if entity_type:
            query["type"] = entity_type
        cursor = (
            self.db.entities.find(query)
            .sort("mention_count", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def save_trend_snapshot(self, snapshot: dict):
        await self.db.trend_stats.insert_one(snapshot)

    async def get_latest_trends(self) -> Optional[dict]:
        return await self.db.trend_stats.find_one(
            sort=[("computed_at", -1)]
        )

    # Seed URLs (PROJECT_SPEC_CONTINUATION §1.3)
    async def get_seed_urls(self, active_only: bool = True) -> List[dict]:
        query = {"is_active": True} if active_only else {}
        cursor = self.db.seed_urls.find(query).sort("priority", -1)
        return await cursor.to_list(length=500)

    async def get_known_domains(self) -> List[str]:
        return await self.db.seed_urls.distinct("domain")

    async def insert_seed_url(self, doc: dict) -> str:
        result = await self.db.seed_urls.insert_one(doc)
        return str(result.inserted_id)

    async def upsert_seed_url(self, url: str, doc: dict):
        await self.db.seed_urls.update_one(
            {"url": url},
            {"$set": doc},
            upsert=True,
        )
