from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import math

from backend.utils.serial import serialize_doc

router = APIRouter()


@router.get("")
async def list_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    platform: Optional[str] = None,
    is_leak: Optional[bool] = None,
    since: Optional[datetime] = None,
    search: Optional[str] = None,
):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    skip = (page - 1) * per_page
    if search:
        query = {"$text": {"$search": search}}
        if platform:
            query["source_platform"] = platform
        if is_leak is not None:
            query["is_leak"] = is_leak
        if since:
            query["published_at"] = {"$gte": since}
        try:
            cursor = db.db.posts.find(query).sort("published_at", -1).skip(skip).limit(per_page)
            posts = await cursor.to_list(length=per_page)
            total = await db.db.posts.count_documents(query)
        except Exception:
            posts = await db.get_posts(skip=skip, limit=per_page, is_leak=is_leak, platform=platform, since=since)
            total = await db.count_posts()
    else:
        posts = await db.get_posts(skip=skip, limit=per_page, is_leak=is_leak, platform=platform, since=since)
        total = await db.count_posts()
    serialized = [serialize_doc(p) for p in posts]
    for p in serialized:
        p["id"] = p.get("_id", "")
    return {
        "data": serialized,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page) if total else 1,
    }


@router.get("/{post_id}")
async def get_post(post_id: str):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    post = await db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    serialized = serialize_doc(post)
    serialized["id"] = serialized.get("_id", "")
    return serialized
