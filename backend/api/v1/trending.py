from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timezone, timedelta

router = APIRouter()


@router.get("")
async def get_trending(
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = None,
    company: Optional[str] = None,
):
    from backend.services.trending_service import TrendingDetector
    from backend.db.mongodb import MongoDBClient

    detector = TrendingDetector()
    trending = await detector.compute_trending(top_n=limit)

    if category:
        trending = [t for t in trending if t.get("category") == category]
    if company:
        trending = [
            t for t in trending
            if company in t.get("entities", {}).get("companies", [])
        ]

    db = MongoDBClient()
    await db.connect()

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_rumors = await db.db.rumors.count_documents({})
    total_posts = await db.db.posts.count_documents({})
    posts_today = await db.db.posts.count_documents({"scraped_at": {"$gte": today_start}})
    leaks_total = await db.db.posts.count_documents({"is_leak": True})
    sources_count = await db.db.sources.count_documents({})

    pipeline = [
        {"$match": {"is_leak": True, "leak_confidence": {"$gt": 0}}},
        {"$group": {"_id": None, "avg": {"$avg": "$leak_confidence"}}},
    ]
    agg = await db.db.posts.aggregate(pipeline).to_list(1)
    avg_confidence = round((agg[0]["avg"] * 100) if agg else 0, 1)

    return {
        "computed_at": now.isoformat(),
        "trending": trending,
        "stats": {
            "total_rumors": total_rumors,
            "total_posts": total_posts,
            "posts_today": posts_today,
            "leaks_total": leaks_total,
            "avg_confidence": avg_confidence,
            "sources_count": sources_count,
        },
    }
