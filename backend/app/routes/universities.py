from fastapi import APIRouter

from app.schemas.auth import UniversityOut
from app.services.user_store import serialize_university, user_store

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=list[UniversityOut])
def list_universities() -> list[UniversityOut]:
    return [serialize_university(university) for university in user_store.list_universities()]
