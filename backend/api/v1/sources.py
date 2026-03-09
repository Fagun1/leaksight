from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter()


@router.get("")
async def list_sources(
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    sort_by: str = Query("credibility_score"),
):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    sources = await db.get_top_sources(limit=limit)
    if platform:
        sources = [s for s in sources if s.get("platform") == platform]
    return {"data": sources, "total": len(sources)}


@router.get("/{platform}/{username}")
async def get_source(platform: str, username: str):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    source = await db.get_source_by_username(username, platform)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    posts = await db.db.posts.find(
        {"author_username": username, "source_platform": platform}
    ).sort("published_at", -1).limit(20).to_list(length=20)
    source["recent_posts"] = posts
    return source
