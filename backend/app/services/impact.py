from app.schemas.dashboard import ImpactResponse, SummaryKpis
from app.services import mock_data


def get_impact() -> ImpactResponse:
    return ImpactResponse(
        waste_months=mock_data.WASTE_MONTHS,
        waste_lbs=mock_data.WASTE_LBS,
        climate_months=mock_data.CLIMATE_MONTHS,
        climate_tco2=mock_data.CLIMATE_TCO2,
        summary=SummaryKpis(**mock_data.SUMMARY),
    )
