from app.schemas.dashboard import OverviewResponse, SummaryKpis
from app.services import metrics, mock_data


def get_overview(
    university_id: str | None = None,
    university_name: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> OverviewResponse:
    snap = metrics.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    return OverviewResponse(
        university=university_name or mock_data.UNIVERSITY,
        date_range=snap["date_range"],
        summary=SummaryKpis(**snap["summary"]),
        months=snap["months"],
        posts_by_month=snap["posts_by_month"],
        claims_by_month=snap["claims_by_month"],
        hours=snap["hours"],
        claims_by_hour=snap["claims_by_hour"],
        locations=snap["locations"],
    )
