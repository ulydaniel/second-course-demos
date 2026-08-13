"""Metrics source selector: Firestore when available, else bundled mock data.

Keeps a single entry point so overview/posts/staff/impact don't each duplicate the
fallback logic. Firestore is the source of truth (DATA_CONTRACT.md); the mock
snapshot is only a last resort so the demo still boots offline or for campuses
that aren't mirrored in Firestore.
"""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.services import mock_data
from app.services.firestore_metrics import available_periods as _firestore_available_periods
from app.services.firestore_metrics import build_snapshot as _firestore_snapshot


def get_snapshot(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> dict[str, Any]:
    if settings.metrics_source != "mock":
        snap = _firestore_snapshot(university_id, period, month=month, year=year, week_start=week_start)
        if snap is not None:
            return snap

    snap = mock_data.get_snapshot(
        university_id, period, month=month, year=year, week_start=week_start
    )
    # Mock summaries predate meal value — approximate it so the Impact tab still
    # shows a plausible student-savings figure when running without Firestore.
    summary = snap.get("summary")
    if isinstance(summary, dict) and "meal_value" not in summary:
        default_meal = 10
        summary["meal_value"] = int(summary.get("total_claims", 0)) * default_meal
    return snap


def get_available_periods(university_id: str | None = None) -> dict[str, Any]:
    """Return date-filter options that have posts/claims for this campus."""
    if settings.metrics_source != "mock":
        periods = _firestore_available_periods(university_id)
        if periods is not None:
            return periods
    return mock_data.available_periods(university_id)
