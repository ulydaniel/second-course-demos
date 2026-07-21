from app.schemas.dashboard import ImpactResponse, SummaryKpis
from app.services import mock_data


def get_impact(
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
) -> ImpactResponse:
    snap = mock_data.get_snapshot(period, month=month, year=year)
    return ImpactResponse(
        waste_months=snap["waste_months"],
        waste_lbs=snap["waste_lbs"],
        climate_months=snap["climate_months"],
        climate_tco2=snap["climate_tco2"],
        summary=SummaryKpis(**snap["summary"]),
    )
