from app.schemas.dashboard import OverviewResponse, SummaryKpis
from app.services import mock_data


def get_overview() -> OverviewResponse:
    return OverviewResponse(
        university=mock_data.UNIVERSITY,
        date_range=mock_data.DATE_RANGE,
        summary=SummaryKpis(**mock_data.SUMMARY),
        months=mock_data.MONTHS,
        posts_by_month=mock_data.POSTS_BY_MONTH,
        claims_by_month=mock_data.CLAIMS_BY_MONTH,
        hours=mock_data.HOURS,
        claims_by_hour=mock_data.CLAIMS_BY_HOUR,
        locations=mock_data.LOCATIONS,
    )
