from fastapi import APIRouter, Depends

from app.dependencies.filters import dashboard_filters
from app.schemas.dashboard import StaffMember
from app.services.staff import list_staff

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", response_model=list[StaffMember])
def read_staff(filters: dict = Depends(dashboard_filters)) -> list[StaffMember]:
    return list_staff(
        period=filters["period"],
        month=filters["month"],
        year=filters["year"],
    )
