"""
Leak timeline tracking: lifecycle events for rumors (PROJECT_SPEC_CONTINUATION §6.3).
"""
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum


class RumorStatus(str, Enum):
    EMERGING = "emerging"
    DEVELOPING = "developing"
    WIDESPREAD = "widespread"
    CONFIRMED = "confirmed"
    DENIED = "denied"
    EXPIRED = "expired"


class TimelineEventType(str, Enum):
    FIRST_MENTION = "first_mention"
    CORROBORATION = "corroboration"
    NEW_DETAIL = "new_detail"
    MEDIA_PICKUP = "media_pickup"
    VIRAL_SPIKE = "viral_spike"
    OFFICIAL_RESPONSE = "official_response"
    CONFIRMED = "confirmed"
    DENIED = "denied"


MEDIA_DOMAINS = {
    "macrumors.com", "theverge.com", "techcrunch.com", "arstechnica.com",
    "engadget.com", "9to5mac.com", "9to5google.com", "tomshardware.com",
    "anandtech.com", "techradar.com", "notebookcheck.net", "wccftech.com",
    "videocardz.com", "cnet.com",
}


class TimelineTracker:
    """Tracks evolution of a rumor; detects and records lifecycle events."""

    def __init__(self, db=None):
        self._db = db

    async def _get_db(self):
        if self._db is None:
            from backend.db.mongodb import MongoDBClient
            self._db = MongoDBClient()
            await self._db.connect()
        return self._db

    async def process_new_post(self, rumor_id: str, post: dict):
        """When a new post is added to a rumor, evaluate if a timeline event should be recorded."""
        from bson import ObjectId
        db = await self._get_db()
        rid = ObjectId(rumor_id) if isinstance(rumor_id, str) and len(rumor_id) == 24 else rumor_id
        rumor = await db.db.rumors.find_one({"_id": rid})
        if not rumor:
            return
        events_to_add = []
        now = datetime.now(timezone.utc).isoformat()
        source_domain = post.get("source_domain", post.get("source_platform", ""))
        author = post.get("author_username", post.get("author", ""))
        post_id = str(post.get("_id", ""))

        if rumor.get("source_count", 0) <= 1:
            events_to_add.append({
                "type": TimelineEventType.FIRST_MENTION,
                "date": now,
                "source": source_domain,
                "author": author,
                "post_id": post_id,
                "description": f"First mention by {author} on {source_domain}",
            })

        existing_authors = set()
        for event in rumor.get("timeline", []):
            if event.get("author"):
                existing_authors.add(event["author"])
        if author and author not in existing_authors and len(existing_authors) > 0:
            events_to_add.append({
                "type": TimelineEventType.CORROBORATION,
                "date": now,
                "source": source_domain,
                "author": author,
                "post_id": post_id,
                "description": f"Corroborated by {author} on {source_domain}",
            })

        if source_domain in MEDIA_DOMAINS:
            events_to_add.append({
                "type": TimelineEventType.MEDIA_PICKUP,
                "date": now,
                "source": source_domain,
                "post_id": post_id,
                "description": f"Covered by {source_domain}",
            })

        new_details = self._detect_new_details(rumor, post)
        if new_details:
            events_to_add.append({
                "type": TimelineEventType.NEW_DETAIL,
                "date": now,
                "details": new_details,
                "post_id": post_id,
                "description": f"New details: {', '.join(new_details)}",
            })

        if events_to_add:
            new_status = self._determine_status(rumor, events_to_add)
            await db.db.rumors.update_one(
                {"_id": rid},
                {
                    "$push": {"timeline": {"$each": events_to_add}},
                    "$set": {"status": new_status, "updated_at": now},
                },
            )

    def _detect_new_details(self, rumor: dict, post: dict) -> List[str]:
        new_details = []
        rumor_entities = rumor.get("entities", {})
        rumor_features = set(rumor_entities.get("features", []))
        rumor_specs = set()
        for event in rumor.get("timeline", []):
            for d in event.get("details", []):
                rumor_specs.add(str(d).lower())
        post_entities = post.get("entities", {})
        for f in post_entities.get("features", []):
            if f not in rumor_features:
                new_details.append(f)
        for s in post_entities.get("specifications", []):
            if str(s).lower() not in rumor_specs:
                new_details.append(s)
        return new_details

    def _determine_status(self, rumor: dict, new_events: List[dict]) -> str:
        all_events = rumor.get("timeline", []) + new_events
        event_types = set(e.get("type", "") for e in all_events)
        if TimelineEventType.CONFIRMED in event_types:
            return RumorStatus.CONFIRMED
        if TimelineEventType.DENIED in event_types:
            return RumorStatus.DENIED
        source_count = rumor.get("source_count", 0) + 1
        if TimelineEventType.MEDIA_PICKUP in event_types or source_count >= 5:
            return RumorStatus.WIDESPREAD
        if source_count >= 2:
            return RumorStatus.DEVELOPING
        return RumorStatus.EMERGING

    async def get_timeline(self, rumor_id: str) -> Optional[dict]:
        from bson import ObjectId
        db = await self._get_db()
        rid = ObjectId(rumor_id) if isinstance(rumor_id, str) and len(rumor_id) == 24 else rumor_id
        rumor = await db.db.rumors.find_one(
            {"_id": rid},
            {"timeline": 1, "title": 1, "status": 1, "first_seen": 1},
        )
        if not rumor:
            return None
        timeline = rumor.get("timeline", [])
        timeline.sort(key=lambda e: e.get("date", ""))
        return {
            "rumor_id": str(rumor_id),
            "title": rumor.get("title"),
            "status": rumor.get("status"),
            "first_seen": rumor.get("first_seen"),
            "events": timeline,
            "total_events": len(timeline),
        }
