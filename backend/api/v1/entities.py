from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter()


@router.get("")
async def list_entities(
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    entities = await db.get_entities(entity_type=type, limit=limit)
    if search:
        entities = [e for e in entities if search.lower() in e.get("name", "").lower()]
    return {"data": entities, "total": len(entities)}


@router.get("/{entity_name}")
async def get_entity(entity_name: str):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    entity = await db.db.entities.find_one({"normalized_name": entity_name.lower().replace(" ", "_")})
    if not entity:
        entity = await db.db.entities.find_one({"name": {"$regex": entity_name, "$options": "i"}})
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    rumor_ids = entity.get("associated_rumors", [])
    rumors = []
    for rid in rumor_ids[:10]:
        rumor = await db.get_rumor(str(rid))
        if rumor:
            rumors.append(rumor)
    entity["rumors"] = rumors
    return entity
