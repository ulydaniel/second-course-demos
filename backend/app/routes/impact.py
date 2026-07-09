from fastapi import APIRouter

from app.schemas.dashboard import ImpactResponse
from app.services.impact import get_impact

router = APIRouter(prefix="/impact", tags=["impact"])


@router.get("", response_model=ImpactResponse)
def read_impact() -> ImpactResponse:
    return get_impact()
