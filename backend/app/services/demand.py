from app.schemas.dashboard import DemandResponse
from app.services import mock_data


def get_demand_map() -> DemandResponse:
    return DemandResponse(
        locations=mock_data.DEMAND_LOCATIONS,
        times=mock_data.DEMAND_TIMES,
        grid=mock_data.DEMAND_GRID,
    )
