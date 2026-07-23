from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.schemas.dashboard import ImpactResponse
from app.services.impact import get_impact

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("", response_model=ImpactResponse)
def read_impact(filters: dict = Depends(dashboard_filters)) -> ImpactResponse:
    return get_impact(
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
    )
