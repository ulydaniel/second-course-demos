"""Shared dashboard date-range query params."""

from typing import Literal

from fastapi import Query

PeriodQuery = Literal["week", "month", "year"]


def dashboard_filters(
    period: PeriodQuery = Query("year", description="Date range: week | month | year"),
    month: int | None = Query(
        None,
        ge=1,
        le=12,
        description="Calendar month (1–12). Used when period=month.",
    ),
    year: int | None = Query(
        None,
        ge=2024,
        le=2026,
        description="Calendar year, or academic-year August start when period=year.",
    ),
) -> dict[str, int | str | None]:
    return {"period": period, "month": month, "year": year}
