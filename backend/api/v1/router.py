from fastapi import APIRouter
from backend.api.v1 import rumors, trending, posts, entities, sources, alerts, scrape, seeds, analytics

v1_router = APIRouter()

v1_router.include_router(scrape.router, prefix="/scrape", tags=["Scrape"])
v1_router.include_router(seeds.router, prefix="/seeds", tags=["Seeds"])
v1_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
v1_router.include_router(rumors.router, prefix="/rumors", tags=["Rumors"])
v1_router.include_router(trending.router, prefix="/trending", tags=["Trending"])
v1_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
v1_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
v1_router.include_router(sources.router, prefix="/sources", tags=["Sources"])
v1_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
