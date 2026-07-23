from app.schemas.dashboard import PostRecord
from app.services import mock_data


def list_posts(
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
) -> list[PostRecord]:
    snap = mock_data.get_snapshot(period, month=month, year=year)
    return [PostRecord(**post) for post in snap["posts"]]
