"""Scrape endpoint - triggers parallel data collection, classification, and storage."""
import asyncio
import logging
import traceback
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger("api.scrape")

_scrape_status = {"running": False, "last_result": None}


@router.get("/status")
async def scrape_status():
    return _scrape_status


async def _run_pipeline(all_posts: list, scraper_counts: dict, errors: dict):
    """Background pipeline: classify, extract entities, store."""
    global _scrape_status
    try:
        from backend.pipeline.enricher import PostEnricher
        from backend.ai.classifier import LeakClassifier
        from backend.ai.entity_extractor import EntityExtractor
        from backend.db.mongodb import MongoDBClient

        enricher = PostEnricher()
        classifier = LeakClassifier()
        entity_extractor = EntityExtractor()
        db = MongoDBClient()
        await db.connect()

        stored = 0
        leaks = 0
        skipped_short = 0
        skipped_dup = 0

        logger.info("Pipeline: processing %d posts...", len(all_posts))

        for idx, raw_post in enumerate(all_posts):
            try:
                post = raw_post.model_dump()
                content = post.get("content", "") or post.get("title", "")

                if not content or len(content.strip()) < 20:
                    skipped_short += 1
                    continue

                enriched = enricher.enrich(post)
                full_text = enriched.get("full_text", content)

                result = classifier.classify(full_text)
                enriched["is_leak"] = result.is_leak
                enriched["leak_confidence"] = result.confidence
                enriched["leak_category"] = result.label

                entities = entity_extractor.extract(full_text)
                enriched["entities"] = {
                    "companies": entities.companies,
                    "products": entities.products,
                    "features": entities.features,
                }

                try:
                    post_id = await db.insert_post(enriched)
                except Exception as e:
                    err_str = str(e).lower()
                    if "duplicate key" in err_str or "e11000" in err_str:
                        skipped_dup += 1
                        continue
                    raise
                stored += 1

                if result.is_leak:
                    category = "HARDWARE_LEAK"
                    if entities.products:
                        category = "PRODUCT_LEAK"
                    elif entities.features:
                        category = "FEATURE_LEAK"

                    rumor_id = await db.insert_rumor({
                        "title": post.get("title") or full_text[:120],
                        "summary": full_text[:500],
                        "category": category,
                        "status": "active",
                        "credibility_score": round(result.confidence * 100, 1),
                        "trend_score": 50.0,
                        "first_seen": post.get("published_at", datetime.now(timezone.utc)),
                        "last_seen": datetime.now(timezone.utc),
                        "post_ids": [post_id],
                        "entities": enriched["entities"],
                    })
                    from bson import ObjectId
                    await db.db.posts.update_one(
                        {"_id": ObjectId(post_id)},
                        {"$set": {"rumor_id": rumor_id}},
                    )
                    leaks += 1

                    await db.upsert_source({
                        "username": post.get("author_username", "unknown"),
                        "platform": post.get("source_platform", "unknown"),
                        "display_name": post.get("author_display_name", "unknown"),
                        "credibility_score": round(result.confidence * 100, 1),
                    })

                    for c in entities.companies:
                        await db.upsert_entity({"name": c, "type": "COMPANY"})
                    for p in entities.products:
                        await db.upsert_entity({"name": p, "type": "PRODUCT"})

            except Exception as e:
                logger.warning("Pipeline error on post %d: %s", idx, e)
                continue

        result_info = {
            "scraped": len(all_posts),
            "stored": stored,
            "leaks": leaks,
            "skipped": {"short": skipped_short, "duplicate": skipped_dup},
            "scraper_counts": scraper_counts,
            "errors": errors if errors else None,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        _scrape_status["last_result"] = result_info
        _scrape_status["running"] = False
        logger.info(
            "Pipeline done: scraped=%d stored=%d leaks=%d skip_short=%d skip_dup=%d",
            len(all_posts), stored, leaks, skipped_short, skipped_dup,
        )
    except Exception as e:
        logger.error("Pipeline crashed: %s\n%s", e, traceback.format_exc())
        _scrape_status["running"] = False
        _scrape_status["last_result"] = {"error": str(e)}


@router.post("")
async def run_scrape(background_tasks: BackgroundTasks):
    """
    Trigger a scrape cycle: fetch from Forums, MacRumors, NotebookCheck, TechRadar
    in parallel; then classify + store in background.
    Returns immediately after scraping completes with post counts.
    """
    global _scrape_status

    if _scrape_status["running"]:
        return {
            "scraped": 0, "stored": 0, "leaks": 0,
            "message": "A scrape is already running. Check /api/v1/scrape/status for progress.",
        }

    _scrape_status["running"] = True
    _scrape_status["last_result"] = None

    from backend.scraper.manager import ScrapingManager
    manager = ScrapingManager()

    async def _run_one(scraper):
        try:
            return scraper.get_name(), await scraper.scrape(), None
        except Exception as e:
            return scraper.get_name(), [], str(e)

    tasks = [_run_one(s) for s in manager.scrapers]
    results = await asyncio.gather(*tasks)

    all_posts = []
    errors = {}
    scraper_counts = {}
    for name, posts, err in results:
        scraper_counts[name] = len(posts)
        all_posts.extend(posts)
        if err:
            errors[name] = err

    logger.info("Scrapers finished: %s (total %d posts)", scraper_counts, len(all_posts))

    if not all_posts:
        _scrape_status["running"] = False
        msg = "No posts fetched."
        if errors:
            msg += " Errors: " + "; ".join(f"{k}: {v}" for k, v in errors.items())
        return {"scraped": 0, "stored": 0, "leaks": 0, "message": msg, "errors": errors}

    background_tasks.add_task(_run_pipeline, all_posts, scraper_counts, errors)

    return {
        "scraped": len(all_posts),
        "stored": "processing...",
        "leaks": "processing...",
        "scraper_counts": scraper_counts,
        "errors": errors if errors else None,
        "message": f"Fetched {len(all_posts)} posts from {len(scraper_counts)} sources. Classifying and storing in background...",
    }
