from app.schemas.dashboard import StaffMember
from app.services import mock_data


def list_staff(
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> list[StaffMember]:
    snap = mock_data.get_snapshot(period, month=month, year=year, week_start=week_start)
    return [StaffMember(**member) for member in snap["staff"]]
