from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.dependencies.scope import dashboard_scope
from app.schemas.dashboard import StaffMember
from app.services.staff import list_staff

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", response_model=list[StaffMember])
def read_staff(
    filters: dict = Depends(dashboard_filters),
    university_id: str = Depends(dashboard_scope),
) -> list[StaffMember]:
    return list_staff(
        university_id=university_id,
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
        week_start=filters["week_start"],
    )
