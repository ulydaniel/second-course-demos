from app.schemas.dashboard import DemographicsResponse, ImpactResponse, SummaryKpis
from app.services import metrics
from app.services.firestore_metrics import build_demographics


def get_impact(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> ImpactResponse:
    snap = metrics.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    return ImpactResponse(
        waste_months=snap["waste_months"],
        waste_lbs=snap["waste_lbs"],
        climate_months=snap["climate_months"],
        climate_tco2=snap["climate_tco2"],
        summary=SummaryKpis(**snap["summary"]),
    )


def get_demographics(university_id: str | None = None) -> DemographicsResponse:
    """Return privacy-safe demographic aggregates for a campus.

    Falls back to an empty (but valid) response when Firestore is unavailable or
    the campus has no survey responses, so the Impact tab renders cleanly.
    """
    data = build_demographics(university_id)
    if data is None:
        data = {
            "respondentCount": 0,
            "userCount": 0,
            "minCellSize": 5,
            "suppressed": False,
            "fields": {},
        }
    return DemographicsResponse(**data)
