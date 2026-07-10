from app.schemas.dashboard import PostRecord
from app.services import mock_data


def list_posts() -> list[PostRecord]:
    return [PostRecord(**post) for post in mock_data.POSTS]
