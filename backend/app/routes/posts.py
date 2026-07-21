from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.schemas.dashboard import PostRecord
from app.services.posts import list_posts

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostRecord])
def read_posts(filters: dict = Depends(dashboard_filters)) -> list[PostRecord]:
    return list_posts(
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
    )
