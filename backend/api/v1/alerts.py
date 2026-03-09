from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

router = APIRouter()


class AlertConditions(BaseModel):
    company: Optional[str] = None
    product: Optional[str] = None
    keywords: List[str] = []
    min_credibility: float = 0
    min_sources: int = 1


class NotificationConfig(BaseModel):
    type: str = "webhook"
    url: Optional[str] = None
    email: Optional[str] = None


class CreateAlertRequest(BaseModel):
    name: str
    conditions: AlertConditions
    notification: NotificationConfig


@router.get("")
async def list_alerts():
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    cursor = db.db.alerts.find().sort("created_at", -1)
    alerts = await cursor.to_list(length=100)
    return {"data": alerts, "total": len(alerts)}


@router.post("")
async def create_alert(request: CreateAlertRequest):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    alert = {
        "name": request.name,
        "conditions": request.conditions.model_dump(),
        "notification": request.notification.model_dump(),
        "status": "active",
        "triggered_count": 0,
        "last_triggered": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    result = await db.db.alerts.insert_one(alert)
    alert["_id"] = str(result.inserted_id)
    return alert


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    from backend.db.mongodb import MongoDBClient
    db = MongoDBClient()
    await db.connect()
    result = await db.db.alerts.delete_one({"_id": ObjectId(alert_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "deleted"}
