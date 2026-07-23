from app.schemas.dashboard import OverviewResponse, SummaryKpis
from app.services import mock_data


def get_overview(
    university: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
) -> OverviewResponse:
    snap = mock_data.get_snapshot(period, month=month, year=year)
    return OverviewResponse(
        university=university or mock_data.UNIVERSITY,
        date_range=snap["date_range"],
        summary=SummaryKpis(**snap["summary"]),
        months=snap["months"],
        posts_by_month=snap["posts_by_month"],
        claims_by_month=snap["claims_by_month"],
        hours=snap["hours"],
        claims_by_hour=snap["claims_by_hour"],
        locations=snap["locations"],
    )
