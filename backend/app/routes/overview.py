from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import AvailablePeriodsResponse, OverviewResponse
from app.services.overview import get_available_periods, get_overview
from app.services.user_store import user_store

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/available-periods", response_model=AvailablePeriodsResponse)
def read_available_periods(
    university_id: str = Depends(dashboard_scope),
) -> AvailablePeriodsResponse:
    """Date-filter options that contain posts/claims for this campus."""
    return get_available_periods(university_id)


@router.get("", response_model=OverviewResponse)
def read_overview(
    filters: dict = Depends(dashboard_filters),
    university_id: str = Depends(dashboard_scope),
) -> OverviewResponse:
    university = user_store.get_university(university_id)
    return get_overview(
        university_id=university_id,
        university_name=university.name if university else None,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
        week_start=filters["week_start"],
    )
