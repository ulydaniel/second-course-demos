from fastapi import APIRouter

from app.routes import admin, auth, demand, health, impact, overview, posts, staff, universities

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(universities.router)
api_router.include_router(admin.router)
api_router.include_router(overview.router)
api_router.include_router(posts.router)
api_router.include_router(demand.router)
api_router.include_router(staff.router)
api_router.include_router(impact.router)
