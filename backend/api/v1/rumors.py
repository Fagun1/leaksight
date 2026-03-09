from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import math

from backend.utils.serial import serialize_doc

router = APIRouter()


@router.get("")
async def list_rumors(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    min_credibility: Optional[float] = Query(None, ge=0, le=100),
    category: Optional[str] = None,
    company: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("credibility_score"),
    sort_order: str = Query("desc"),
):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    skip = (page - 1) * per_page
    rumors = await db.get_rumors(
        skip=skip, limit=per_page,
        min_credibility=min_credibility,
        category=category, company=company,
    )
    total = await db.db.rumors.count_documents({})
    serialized = [serialize_doc(r) for r in rumors]
    for r in serialized:
        r["id"] = r.get("_id", "")
    return {
        "data": serialized,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page) if total else 1,
    }


@router.get("/{rumor_id}")
async def get_rumor(rumor_id: str):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    rumor = await db.get_rumor(rumor_id)
    if not rumor:
        raise HTTPException(status_code=404, detail="Rumor not found")
    posts = await db.get_posts_for_rumor(rumor_id)
    rumor["posts"] = posts
    out = serialize_doc(rumor)
    out["id"] = out.get("_id", "")
    return out


@router.get("/{rumor_id}/timeline")
async def get_rumor_timeline(rumor_id: str):
    from backend.services.trending_service import TrendingDetector
    detector = TrendingDetector()
    timeline = await detector.get_rumor_timeline(rumor_id)
    return {"rumor_id": rumor_id, "timeline": timeline}


@router.post("/{rumor_id}/rescore")
async def rescore_rumor(rumor_id: str):
    from backend.services.credibility_service import CredibilityScorer
    scorer = CredibilityScorer()
    new_score = await scorer.score_rumor(rumor_id)
    return {"rumor_id": rumor_id, "credibility_score": new_score}
