from app.schemas.dashboard import PostRecord
from app.services import metrics


def list_posts(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> list[PostRecord]:
    snap = metrics.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    return [PostRecord(**post) for post in snap["posts"]]
