"""
Seed the database with sample rumors and posts for development.
Run from project root: python -m infra.scripts.seed_db
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime, timezone, timedelta
from bson import ObjectId


async def seed():
    from backend.db.mongodb import MongoDBClient
    from backend.config import settings

    db = MongoDBClient()
    await db.connect()

    now = datetime.now(timezone.utc)

    # Sample posts
    posts = [
        {
            "source_platform": "reddit",
            "source_id": "seed_1",
            "source_url": "https://reddit.com/r/apple/comments/seed1",
            "author_username": "tech_leaker",
            "author_display_name": "Tech Leaker",
            "content": "iPhone 18 Dynamic Island might shrink significantly according to supply chain sources.",
            "cleaned_content": "iPhone 18 Dynamic Island might shrink significantly according to supply chain sources",
            "full_text": "iPhone 18 Dynamic Island might shrink significantly according to supply chain sources",
            "published_at": now - timedelta(hours=2),
            "scraped_at": now,
            "engagement": {"upvotes": 450, "comments": 89},
            "engagement_score": 0.72,
            "is_leak": True,
            "leak_confidence": 0.88,
            "leak_category": "HARDWARE_LEAK",
            "entities": {"companies": ["Apple"], "products": ["iPhone 18"], "features": ["Dynamic Island"]},
        },
        {
            "source_platform": "reddit",
            "source_id": "seed_2",
            "source_url": "https://reddit.com/r/nvidia/comments/seed2",
            "author_username": "gpu_insider",
            "author_display_name": "GPU Insider",
            "content": "RTX 5090 specs: 21760 CUDA cores, 32GB GDDR7, 512-bit bus. Launch Q1 2025.",
            "cleaned_content": "RTX 5090 specs 21760 CUDA cores 32GB GDDR7 512-bit bus Launch Q1 2025",
            "full_text": "RTX 5090 specs 21760 CUDA cores 32GB GDDR7 512-bit bus Launch Q1 2025",
            "published_at": now - timedelta(hours=5),
            "scraped_at": now,
            "engagement": {"upvotes": 1200, "comments": 234},
            "engagement_score": 0.85,
            "is_leak": True,
            "leak_confidence": 0.92,
            "leak_category": "HARDWARE_LEAK",
            "entities": {"companies": ["Nvidia"], "products": ["RTX 5090"], "features": ["GDDR7"]},
        },
    ]

    inserted_ids = []
    for post in posts:
        r = await db.db.posts.insert_one(post)
        inserted_ids.append(r.inserted_id)

    rumor_id = await db.db.rumors.insert_one({
        "title": "Nvidia RTX 5090 Specifications",
        "summary": "Multiple sources suggest RTX 5090 will feature 21760 CUDA cores, 32GB GDDR7, Q1 2025 launch.",
        "category": "HARDWARE_LEAK",
        "status": "active",
        "credibility_score": 78.5,
        "trend_score": 85.2,
        "first_seen": now - timedelta(hours=24),
        "last_seen": now,
        "post_ids": [str(oid) for oid in inserted_ids],
        "entities": {"companies": ["Nvidia"], "products": ["RTX 5090"], "features": ["GDDR7", "CUDA cores"]},
    })
    rumor_id_str = str(rumor_id.inserted_id)

    await db.db.posts.update_many(
        {"_id": {"$in": inserted_ids}},
        {"$set": {"rumor_id": rumor_id_str}}
    )

    await db.db.sources.insert_many([
        {"username": "tech_leaker", "platform": "reddit", "display_name": "Tech Leaker", "credibility_score": 72},
        {"username": "gpu_insider", "platform": "reddit", "display_name": "GPU Insider", "credibility_score": 85},
    ])

    await db.db.entities.insert_many([
        {"name": "RTX 5090", "type": "PRODUCT", "mention_count": 45, "normalized_name": "rtx_5090"},
        {"name": "iPhone 18", "type": "PRODUCT", "mention_count": 32, "normalized_name": "iphone_18"},
        {"name": "Nvidia", "type": "COMPANY", "mention_count": 67, "normalized_name": "nvidia"},
        {"name": "Apple", "type": "COMPANY", "mention_count": 54, "normalized_name": "apple"},
    ])

    await db.db.trend_stats.insert_one({
        "computed_at": now,
        "total_active_rumors": 2,
        "posts_today": 15,
        "avg_credibility": 65.0,
        "total_sources": 2,
    })

    print("Seed complete. Sample data inserted.")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
