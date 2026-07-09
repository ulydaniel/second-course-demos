from fastapi import APIRouter

from app.schemas.dashboard import OverviewResponse
from app.services.overview import get_overview

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("", response_model=OverviewResponse)
def read_overview() -> OverviewResponse:
    return get_overview()
