"""Convert MongoDB documents to JSON-serializable dicts (ObjectId/datetime handling)."""
from datetime import datetime
from typing import Any

from bson import ObjectId


def serialize_doc(doc: Any) -> Any:
    """Recursively convert MongoDB doc to JSON-serializable form."""
    if doc is None:
        return None
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat() if hasattr(doc, "isoformat") else str(doc)
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [serialize_doc(x) for x in doc]
    return doc
