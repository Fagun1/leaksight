"""Seed URL management (PROJECT_SPEC_CONTINUATION §1.3)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

router = APIRouter()


class SeedUrlCreate(BaseModel):
    url: str
    domain: str
    category: str = "generic"
    subcategory: Optional[str] = None
    priority: int = 5
    crawl_frequency_minutes: int = 60


@router.get("")
async def list_seeds(active_only: bool = True):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    seeds = await db.get_seed_urls(active_only=active_only)
    for s in seeds:
        s["id"] = str(s["_id"])
    return {"data": seeds, "total": len(seeds)}


@router.post("")
async def create_seed(body: SeedUrlCreate):
    from backend.db.mongodb import MongoDBClient
    from backend.scraper.utils.url_normalizer import normalize_url

    db = MongoDBClient()
    await db.connect()
    doc = {
        "url": normalize_url(body.url) or body.url,
        "domain": body.domain.lower().replace("www.", ""),
        "category": body.category,
        "subcategory": body.subcategory or "",
        "priority": min(10, max(0, body.priority)),
        "crawl_frequency_minutes": body.crawl_frequency_minutes,
        "last_crawled": None,
        "total_leaks_found": 0,
        "leak_yield_rate": 0.0,
        "is_active": True,
        "discovery_method": "manual",
        "added_at": datetime.now(timezone.utc),
        "robots_txt_allows": True,
    }
    seed_id = await db.insert_seed_url(doc)
    return {"id": seed_id, **doc}


@router.delete("/{seed_id}")
async def delete_seed(seed_id: str):
    from backend.db.mongodb import MongoDBClient
    from bson import ObjectId

    db = MongoDBClient()
    await db.connect()
    result = await db.db.seed_urls.delete_one({"_id": ObjectId(seed_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Seed not found")
    return {"status": "deleted"}
