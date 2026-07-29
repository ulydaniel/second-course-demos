from app.schemas.dashboard import DemandResponse
from app.services import mock_data


def get_demand_map(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> DemandResponse:
    snap = mock_data.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    return DemandResponse(
        locations=snap["demand_locations"],
        times=snap["demand_times"],
        grid=snap["demand_grid"],
    )
