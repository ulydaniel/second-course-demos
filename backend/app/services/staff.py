from app.schemas.dashboard import StaffMember
from app.services import mock_data


def list_staff(
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
) -> list[StaffMember]:
    snap = mock_data.get_snapshot(period, month=month, year=year)
    return [StaffMember(**member) for member in snap["staff"]]
