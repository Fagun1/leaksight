from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import settings
from backend.api.v1.router import v1_router
import logging

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LeakSight API...")
    from backend.db.mongodb import MongoDBClient
    from backend.db.redis_client import RedisClient
    app.state.db = MongoDBClient()
    try:
        await app.state.db.connect()
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. API will work with limited functionality.")
    app.state.redis = RedisClient()
    try:
        await app.state.redis.connect()
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    logger.info("LeakSight API started successfully")
    yield
    logger.info("Shutting down LeakSight API...")
    await app.state.db.disconnect()
    await app.state.redis.disconnect()


app = FastAPI(
    title="LeakSight API",
    description="AI-Powered Tech Leak Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: allow frontend origins (API_CORS_ORIGINS as comma-separated string)
_cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
if isinstance(settings.api_cors_origins, str) and settings.api_cors_origins.strip():
    _cors_origins = [
        origin.strip()
        for origin in settings.api_cors_origins.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    from datetime import datetime, timezone
    checks = {}
    overall = True
    # MongoDB
    try:
        await app.state.db.client.admin.command("ping")
        checks["mongodb"] = {"status": "healthy"}
    except Exception as e:
        checks["mongodb"] = {"status": "unhealthy", "error": str(e)}
        overall = False
    # Redis
    try:
        await app.state.redis.client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
        overall = False
    # Queue depths (optional)
    try:
        high = await app.state.redis.client.llen("crawl:queue:high")
        medium = await app.state.redis.client.llen("crawl:queue:medium")
        low = await app.state.redis.client.llen("crawl:queue:low")
        results = await app.state.redis.client.llen("crawl:results")
        checks["queues"] = {"status": "healthy", "high": high, "medium": medium, "low": low, "results": results}
    except Exception as e:
        checks["queues"] = {"status": "unknown", "error": str(e)}
    status_code = 200 if overall else 503
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "status": "healthy" if overall else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app": settings.app_name,
            "version": "1.0.0",
            "checks": checks,
        },
        status_code=status_code,
    )


@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics from Redis (PROJECT_SPEC_CONTINUATION §9.3)."""
    from backend.core.metrics import MetricsCollector
    collector = MetricsCollector()
    data = await collector.get_all_metrics()
    return data
