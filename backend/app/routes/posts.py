from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import PostRecord
from app.services.posts import list_posts

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostRecord])
def read_posts(
    filters: dict = Depends(dashboard_filters),
    university_id: str = Depends(dashboard_scope),
) -> list[PostRecord]:
    return list_posts(
        university_id=university_id,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
        week_start=filters["week_start"],
    )
