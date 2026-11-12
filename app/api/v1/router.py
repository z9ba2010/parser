from fastapi import APIRouter
from app.api.v1.endpoints import apparel, supplements, events, vision, parsers

api_router = APIRouter()

api_router.include_router(apparel.router)
api_router.include_router(vision.router)
api_router.include_router(supplements.router)
api_router.include_router(events.router)
api_router.include_router(parsers.router)
