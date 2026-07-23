from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.schemas.dashboard import DemandResponse
from app.services.demand import get_demand_map

router = APIRouter(prefix="/demand", tags=["demand"])


@router.get("", response_model=DemandResponse)
def read_demand_map(filters: dict = Depends(dashboard_filters)) -> DemandResponse:
    return get_demand_map(
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
    )
