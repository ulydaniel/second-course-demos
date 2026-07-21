from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_optional
from app.dependencies.filters import dashboard_filters
from app.schemas.dashboard import OverviewResponse
from app.services.overview import get_overview
from app.services.user_store import DashboardUser, user_store

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("", response_model=OverviewResponse)
def read_overview(
    filters: dict = Depends(dashboard_filters),
    user: DashboardUser | None = Depends(get_current_user_optional),
) -> OverviewResponse:
    university_name = None
    if user is not None and user.university_id is not None:
        university = user_store.get_university(user.university_id)
        university_name = university.name if university else None
    return get_overview(
        university_name,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
    )
