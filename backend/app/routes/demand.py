from fastapi import APIRouter

from app.schemas.dashboard import DemandResponse
from app.services.demand import get_demand_map

router = APIRouter(prefix="/demand", tags=["demand"])


@router.get("", response_model=DemandResponse)
def read_demand_map() -> DemandResponse:
    return get_demand_map()
