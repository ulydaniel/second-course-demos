from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import DemandResponse
from app.services.demand import get_demand_map

router = APIRouter(prefix="/demand", tags=["demand"])


@router.get("", response_model=DemandResponse)
def read_demand_map(
    filters: dict = Depends(dashboard_filters),
    university_id: str = Depends(dashboard_scope),
) -> DemandResponse:
    return get_demand_map(
        university_id=university_id,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
        week_start=filters["week_start"],
    )
