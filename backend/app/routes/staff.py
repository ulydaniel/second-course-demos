from fastapi import APIRouter

from app.schemas.dashboard import StaffMember
from app.services.staff import list_staff

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", response_model=list[StaffMember])
def read_staff() -> list[StaffMember]:
    return list_staff()
