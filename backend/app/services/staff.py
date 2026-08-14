from app.schemas.dashboard import StaffMember
from app.services import metrics


def list_staff(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> list[StaffMember]:
    snap = metrics.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    return [StaffMember(**member) for member in snap.get("staff") or []]
