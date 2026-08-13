from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import DemographicsResponse, ImpactResponse
from app.services.impact import get_demographics, get_impact

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


@router.get("/demographics", response_model=DemographicsResponse)
def read_demographics(
    university_id: str = Depends(dashboard_scope),
) -> DemographicsResponse:
    """Cohort-level demographics only — scoped to the caller's campus and
    suppressed below the campus minimum cell size. Never returns student PII."""
    return get_demographics(university_id=university_id)
