from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import ImpactResponse
from app.services.impact import get_impact

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("", response_model=ImpactResponse)
def read_impact(
    filters: dict = Depends(dashboard_filters),
    university_id: str = Depends(dashboard_scope),
) -> ImpactResponse:
    return get_impact(
        university_id=university_id,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
        week_start=filters["week_start"],
    )
