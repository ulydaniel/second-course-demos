from fastapi import APIRouter

from app.routes import demand, health, impact, overview, posts, staff

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(overview.router)
api_router.include_router(posts.router)
api_router.include_router(demand.router)
api_router.include_router(staff.router)
api_router.include_router(impact.router)
