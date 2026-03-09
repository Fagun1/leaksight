"""
Analytics endpoints for dashboard charts (PROJECT_SPEC_CONTINUATION §8.3).
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/velocity")
async def leak_velocity(
    days: int = Query(default=30, le=365),
    company: str = Query(default=None),
):
    """Daily leak counts for velocity chart."""
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    since = datetime.now(timezone.utc) - timedelta(days=days)
    match = {"is_leak": True}
    try:
        match["published_at"] = {"$gte": since}
    except Exception:
        pass
    cursor = db.db.posts.aggregate([
        {"$match": match},
        {"$addFields": {"date": {"$cond": {
            "if": {"$eq": [{"$type": "$published_at"}, "date"]},
            "then": {"$dateToString": {"format": "%Y-%m-%d", "date": "$published_at"}},
            "else": {"$substr": [{"$ifNull": ["$published_at", ""]}, 0, 10]},
        }}}},
        {"$match": {"date": {"$ne": ""}}},
        {"$group": {"_id": "$date", "total": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": 500},
    ])
    rows = await cursor.to_list(length=500)
    data = [{"date": r["_id"], "total": r["total"]} for r in rows]
    return {"data": data}


@router.get("/company-distribution")
async def company_distribution():
    """Leak counts by company for bar chart."""
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    cursor = db.db.posts.aggregate([
        {"$match": {"is_leak": True}},
        {"$unwind": "$entities.companies"},
        {"$group": {"_id": "$entities.companies", "count": {"$sum": 1}, "avg_confidence": {"$avg": "$leak_confidence"}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ])
    rows = await cursor.to_list(length=20)
    data = [{"company": r["_id"] or "Unknown", "count": r["count"], "avg_confidence": round(r.get("avg_confidence") or 0, 2)} for r in rows]
    return {"data": data}


@router.get("/category-distribution")
async def category_distribution():
    """Distribution of leak categories for pie chart."""
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    cursor = db.db.rumors.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ])
    rows = await cursor.to_list(length=20)
    total = sum(r["count"] for r in rows) or 1
    data = [{"category": r["_id"] or "other", "count": r["count"], "percentage": round(r["count"] / total, 2)} for r in rows]
    return {"data": data}


@router.get("/rumor/{rumor_id}/spread")
async def rumor_spread(rumor_id: str):
    """Spread data for a single rumor over time."""
    from bson import ObjectId
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    rumor = await db.db.rumors.find_one({"_id": ObjectId(rumor_id)})
    if not rumor:
        return {"data": []}
    timeline = rumor.get("timeline", [])
    by_date = {}
    for e in timeline:
        d = (e.get("date") or "")[:10]
        if not d:
            continue
        if d not in by_date:
            by_date[d] = {"cumulative_sources": 0, "platforms": {}}
        by_date[d]["cumulative_sources"] = by_date[d]["cumulative_sources"] + 1
        src = e.get("source", "other")
        by_date[d]["platforms"][src] = by_date[d]["platforms"].get(src, 0) + 1
    data = [{"date": k, **v} for k, v in sorted(by_date.items())]
    return {"data": data}
