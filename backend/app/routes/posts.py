from fastapi import APIRouter

from app.schemas.dashboard import PostRecord
from app.services.posts import list_posts

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostRecord])
def read_posts() -> list[PostRecord]:
    return list_posts()
