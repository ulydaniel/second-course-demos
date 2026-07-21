"""Demo metrics ported from src/data.ts, sliced by date-range period.

Serves as the data source until SQL / Firebase aggregates replace this module.
Callers pass period ("week" | "month" | "year"); get_snapshot() returns the
matching numbers so routes stay identical when the store becomes live queries.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from app.config import settings

Period = Literal["week", "month", "year"]

UNIVERSITY = settings.university_name

PERIOD_LABELS: dict[Period, str] = {
    "week": "Last 7 days",
    "month": "Last 30 days",
    "year": "Aug 2025 – Jun 2026",
}

# ---------------------------------------------------------------------------
# Academic year (default) — matches historical src/data.ts constants
# ---------------------------------------------------------------------------

_YEAR: dict[str, Any] = {
    "date_range": PERIOD_LABELS["year"],
    "months": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "posts_by_month": [42, 68, 91, 78, 55, 72, 88, 95, 102, 86, 70],
    "claims_by_month": [198, 312, 410, 356, 248, 334, 401, 438, 472, 398, 364],
    "hours": ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"],
    "claims_by_hour": [12, 48, 92, 156, 134, 98, 64, 28],
    "locations": [
        {"name": "Alumni Center", "posts": 312, "claim_rate": 76},
        {"name": "Student Union", "posts": 248, "claim_rate": 71},
        {"name": "Aztec Recreation", "posts": 186, "claim_rate": 52},
        {"name": "Engineering Quad", "posts": 142, "claim_rate": 64},
        {"name": "Campus Events", "posts": 98, "claim_rate": 58},
    ],
    "demand_grid": [
        [2, 4, 8, 12, 10, 6, 3, 1],
        [3, 6, 14, 18, 15, 9, 4, 2],
        [1, 3, 9, 11, 8, 5, 2, 1],
        [4, 8, 16, 20, 17, 11, 5, 2],
        [2, 5, 11, 14, 12, 7, 3, 1],
    ],
    "demand_locations": ["Alumni Ctr", "Student Union", "Aztec Rec", "Eng. Quad", "Events"],
    "demand_times": ["7–9a", "9–11a", "11a–1p", "1–3p", "3–5p", "5–7p", "7–9p", "9–11p"],
    "staff": [
        {
            "name": "Maria G.",
            "role": "Dining Hall Mgr",
            "posts": 142,
            "last_post": "Today, 11:40a",
            "avg_claim_min": 9.2,
            "utilization": "high",
        },
        {
            "name": "James T.",
            "role": "Events Catering",
            "posts": 118,
            "last_post": "Yesterday, 4:15p",
            "avg_claim_min": 11.8,
            "utilization": "high",
        },
        {
            "name": "Priya S.",
            "role": "Student Union",
            "posts": 96,
            "last_post": "3 days ago",
            "avg_claim_min": 14.1,
            "utilization": "medium",
        },
        {
            "name": "Alex R.",
            "role": "Aztec Recreation",
            "posts": 34,
            "last_post": "12 days ago",
            "avg_claim_min": 22.4,
            "utilization": "low",
        },
        {
            "name": "Chris L.",
            "role": "Campus Events",
            "posts": 18,
            "last_post": "21 days ago",
            "avg_claim_min": 31.6,
            "utilization": "low",
        },
    ],
    "posts": [
        {
            "id": "P-1042",
            "title": "Catered lunch surplus — sandwiches & fruit",
            "staff": "Maria G.",
            "location": "Alumni Center",
            "posted": "Jun 12, 11:35a",
            "posted_at": "2026-06-12T11:35",
            "claims": 28,
            "views": 41,
            "claim_rate": 68,
            "first_claim_min": 4.2,
            "allergens": "Gluten, dairy",
            "description": "Assorted wraps, fruit cups, and cookies from a 120-person conference.",
            "lbs_diverted": 42,
        },
        {
            "id": "P-1038",
            "title": "Pizza & salad bar leftovers",
            "staff": "James T.",
            "location": "Student Union",
            "posted": "Jun 11, 1:10p",
            "posted_at": "2026-06-11T13:10",
            "claims": 44,
            "views": 52,
            "claim_rate": 85,
            "first_claim_min": 3.1,
            "allergens": "Gluten, dairy, tree nuts",
            "description": "Whole pizzas and mixed greens from a student org mixer.",
            "lbs_diverted": 58,
        },
        {
            "id": "P-1031",
            "title": "Breakfast pastries & coffee service",
            "staff": "Priya S.",
            "location": "Engineering Quad",
            "posted": "Jun 10, 8:50a",
            "posted_at": "2026-06-10T08:50",
            "claims": 19,
            "views": 36,
            "claim_rate": 53,
            "first_claim_min": 18.7,
            "allergens": "Gluten, eggs, dairy",
            "description": "Croissants, muffins, and fruit from a morning department meeting.",
            "lbs_diverted": 24,
        },
        {
            "id": "P-1024",
            "title": "Post-game catering trays",
            "staff": "Alex R.",
            "location": "Aztec Recreation",
            "posted": "May 28, 6:20p",
            "posted_at": "2026-05-28T18:20",
            "claims": 8,
            "views": 22,
            "claim_rate": 36,
            "first_claim_min": 42.0,
            "allergens": "None listed",
            "description": "Chicken tenders, veggie trays, and bottled water from intramural finals.",
            "lbs_diverted": 16,
        },
    ],
    "waste_months": ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"],
    "waste_lbs": [180, 310, 420, 520, 680, 820],
    "climate_months": ["Aug", "Oct", "Dec", "Feb", "Apr", "Jun"],
    "climate_tco2": [0.08, 0.14, 0.19, 0.23, 0.3, 0.36],
    "summary": {
        "total_posts": 847,
        "total_claims": 4231,
        "claim_rate": 68,
        "avg_first_claim_min": 12.4,
        "lbs_diverted": 3420,
        "tco2e": 1.2,
        "hauling_savings": 4280,
    },
}

# ---------------------------------------------------------------------------
# Last 30 days — scaled subset; time axis is weekly buckets
# ---------------------------------------------------------------------------

_MONTH: dict[str, Any] = {
    "date_range": PERIOD_LABELS["month"],
    "months": ["W1", "W2", "W3", "W4"],
    "posts_by_month": [18, 22, 26, 21],
    "claims_by_month": [86, 104, 128, 98],
    "hours": ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"],
    "claims_by_hour": [3, 14, 28, 48, 41, 30, 18, 6],
    "locations": [
        {"name": "Alumni Center", "posts": 28, "claim_rate": 79},
        {"name": "Student Union", "posts": 24, "claim_rate": 74},
        {"name": "Aztec Recreation", "posts": 14, "claim_rate": 48},
        {"name": "Engineering Quad", "posts": 12, "claim_rate": 66},
        {"name": "Campus Events", "posts": 9, "claim_rate": 55},
    ],
    "demand_grid": [
        [1, 3, 6, 10, 8, 4, 2, 1],
        [2, 5, 11, 15, 12, 7, 3, 1],
        [1, 2, 7, 9, 6, 3, 1, 1],
        [3, 6, 13, 17, 14, 8, 4, 2],
        [1, 3, 8, 11, 9, 5, 2, 1],
    ],
    "demand_locations": ["Alumni Ctr", "Student Union", "Aztec Rec", "Eng. Quad", "Events"],
    "demand_times": ["7–9a", "9–11a", "11a–1p", "1–3p", "3–5p", "5–7p", "7–9p", "9–11p"],
    "staff": [
        {
            "name": "Maria G.",
            "role": "Dining Hall Mgr",
            "posts": 14,
            "last_post": "Today, 11:40a",
            "avg_claim_min": 8.4,
            "utilization": "high",
        },
        {
            "name": "James T.",
            "role": "Events Catering",
            "posts": 11,
            "last_post": "Yesterday, 4:15p",
            "avg_claim_min": 10.2,
            "utilization": "high",
        },
        {
            "name": "Priya S.",
            "role": "Student Union",
            "posts": 9,
            "last_post": "3 days ago",
            "avg_claim_min": 13.5,
            "utilization": "medium",
        },
        {
            "name": "Alex R.",
            "role": "Aztec Recreation",
            "posts": 2,
            "last_post": "12 days ago",
            "avg_claim_min": 24.0,
            "utilization": "low",
        },
        {
            "name": "Chris L.",
            "role": "Campus Events",
            "posts": 1,
            "last_post": "21 days ago",
            "avg_claim_min": 36.0,
            "utilization": "low",
        },
    ],
    "posts": [
        {
            "id": "P-1042",
            "title": "Catered lunch surplus — sandwiches & fruit",
            "staff": "Maria G.",
            "location": "Alumni Center",
            "posted": "Jun 12, 11:35a",
            "posted_at": "2026-06-12T11:35",
            "claims": 28,
            "views": 41,
            "claim_rate": 68,
            "first_claim_min": 4.2,
            "allergens": "Gluten, dairy",
            "description": "Assorted wraps, fruit cups, and cookies from a 120-person conference.",
            "lbs_diverted": 42,
        },
        {
            "id": "P-1038",
            "title": "Pizza & salad bar leftovers",
            "staff": "James T.",
            "location": "Student Union",
            "posted": "Jun 11, 1:10p",
            "posted_at": "2026-06-11T13:10",
            "claims": 44,
            "views": 52,
            "claim_rate": 85,
            "first_claim_min": 3.1,
            "allergens": "Gluten, dairy, tree nuts",
            "description": "Whole pizzas and mixed greens from a student org mixer.",
            "lbs_diverted": 58,
        },
        {
            "id": "P-1031",
            "title": "Breakfast pastries & coffee service",
            "staff": "Priya S.",
            "location": "Engineering Quad",
            "posted": "Jun 10, 8:50a",
            "posted_at": "2026-06-10T08:50",
            "claims": 19,
            "views": 36,
            "claim_rate": 53,
            "first_claim_min": 18.7,
            "allergens": "Gluten, eggs, dairy",
            "description": "Croissants, muffins, and fruit from a morning department meeting.",
            "lbs_diverted": 24,
        },
    ],
    "waste_months": ["W1", "W2", "W3", "W4"],
    "waste_lbs": [48, 62, 78, 70],
    "climate_months": ["W1", "W2", "W3", "W4"],
    "climate_tco2": [0.02, 0.03, 0.04, 0.03],
    "summary": {
        "total_posts": 87,
        "total_claims": 416,
        "claim_rate": 72,
        "avg_first_claim_min": 10.8,
        "lbs_diverted": 258,
        "tco2e": 0.12,
        "hauling_savings": 340,
    },
}

# ---------------------------------------------------------------------------
# Last 7 days — daily axis; fewer posts
# ---------------------------------------------------------------------------

_WEEK: dict[str, Any] = {
    "date_range": PERIOD_LABELS["week"],
    "months": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "posts_by_month": [3, 5, 4, 6, 4, 2, 1],
    "claims_by_month": [14, 28, 22, 36, 24, 10, 4],
    "hours": ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"],
    "claims_by_hour": [1, 4, 9, 22, 18, 12, 6, 2],
    "locations": [
        {"name": "Alumni Center", "posts": 8, "claim_rate": 81},
        {"name": "Student Union", "posts": 7, "claim_rate": 76},
        {"name": "Aztec Recreation", "posts": 3, "claim_rate": 44},
        {"name": "Engineering Quad", "posts": 4, "claim_rate": 70},
        {"name": "Campus Events", "posts": 3, "claim_rate": 58},
    ],
    "demand_grid": [
        [0, 2, 4, 8, 6, 3, 1, 0],
        [1, 3, 8, 12, 10, 5, 2, 1],
        [0, 1, 4, 6, 4, 2, 1, 0],
        [2, 4, 9, 14, 11, 6, 2, 1],
        [0, 2, 5, 8, 6, 3, 1, 0],
    ],
    "demand_locations": ["Alumni Ctr", "Student Union", "Aztec Rec", "Eng. Quad", "Events"],
    "demand_times": ["7–9a", "9–11a", "11a–1p", "1–3p", "3–5p", "5–7p", "7–9p", "9–11p"],
    "staff": [
        {
            "name": "Maria G.",
            "role": "Dining Hall Mgr",
            "posts": 4,
            "last_post": "Today, 11:40a",
            "avg_claim_min": 7.1,
            "utilization": "high",
        },
        {
            "name": "James T.",
            "role": "Events Catering",
            "posts": 3,
            "last_post": "Yesterday, 4:15p",
            "avg_claim_min": 9.5,
            "utilization": "high",
        },
        {
            "name": "Priya S.",
            "role": "Student Union",
            "posts": 2,
            "last_post": "3 days ago",
            "avg_claim_min": 12.0,
            "utilization": "medium",
        },
        {
            "name": "Alex R.",
            "role": "Aztec Recreation",
            "posts": 0,
            "last_post": "12 days ago",
            "avg_claim_min": 22.4,
            "utilization": "low",
        },
        {
            "name": "Chris L.",
            "role": "Campus Events",
            "posts": 0,
            "last_post": "21 days ago",
            "avg_claim_min": 31.6,
            "utilization": "low",
        },
    ],
    "posts": [
        {
            "id": "P-1042",
            "title": "Catered lunch surplus — sandwiches & fruit",
            "staff": "Maria G.",
            "location": "Alumni Center",
            "posted": "Jun 12, 11:35a",
            "posted_at": "2026-06-12T11:35",
            "claims": 28,
            "views": 41,
            "claim_rate": 68,
            "first_claim_min": 4.2,
            "allergens": "Gluten, dairy",
            "description": "Assorted wraps, fruit cups, and cookies from a 120-person conference.",
            "lbs_diverted": 42,
        },
        {
            "id": "P-1038",
            "title": "Pizza & salad bar leftovers",
            "staff": "James T.",
            "location": "Student Union",
            "posted": "Jun 11, 1:10p",
            "posted_at": "2026-06-11T13:10",
            "claims": 44,
            "views": 52,
            "claim_rate": 85,
            "first_claim_min": 3.1,
            "allergens": "Gluten, dairy, tree nuts",
            "description": "Whole pizzas and mixed greens from a student org mixer.",
            "lbs_diverted": 58,
        },
    ],
    "waste_months": ["Mon", "Wed", "Fri", "Sun"],
    "waste_lbs": [12, 22, 28, 18],
    "climate_months": ["Mon", "Wed", "Fri", "Sun"],
    "climate_tco2": [0.005, 0.01, 0.012, 0.008],
    "summary": {
        "total_posts": 25,
        "total_claims": 138,
        "claim_rate": 76,
        "avg_first_claim_min": 8.6,
        "lbs_diverted": 80,
        "tco2e": 0.035,
        "hauling_savings": 95,
    },
}

_SNAPSHOTS: dict[Period, dict[str, Any]] = {
    "week": _WEEK,
    "month": _MONTH,
    "year": _YEAR,
}

# Academic-year series is Aug → Jun (11 buckets). Calendar month → series index.
_ACADEMIC_MONTH_INDEX: dict[int, int] = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    1: 5,
    2: 6,
    3: 7,
    4: 8,
    5: 9,
    6: 10,
}

_MONTH_NAMES = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

# Module-level aliases kept for any imports that still expect year constants
DATE_RANGE = _YEAR["date_range"]
MONTHS = _YEAR["months"]
POSTS_BY_MONTH = _YEAR["posts_by_month"]
CLAIMS_BY_MONTH = _YEAR["claims_by_month"]
HOURS = _YEAR["hours"]
CLAIMS_BY_HOUR = _YEAR["claims_by_hour"]
LOCATIONS = _YEAR["locations"]
DEMAND_GRID = _YEAR["demand_grid"]
DEMAND_LOCATIONS = _YEAR["demand_locations"]
DEMAND_TIMES = _YEAR["demand_times"]
STAFF = _YEAR["staff"]
POSTS = _YEAR["posts"]
WASTE_MONTHS = _YEAR["waste_months"]
WASTE_LBS = _YEAR["waste_lbs"]
CLIMATE_MONTHS = _YEAR["climate_months"]
CLIMATE_TCO2 = _YEAR["climate_tco2"]
SUMMARY = _YEAR["summary"]

DEFAULT_CALENDAR_MONTH = 6
DEFAULT_CALENDAR_YEAR = 2026
AVAILABLE_YEARS = (2024, 2025, 2026)


def normalize_period(period: str | None) -> Period:
    if period in ("week", "month", "year"):
        return period  # type: ignore[return-value]
    return "year"


def _clamp_month(month: int | None) -> int:
    if month is None or month < 1 or month > 12:
        return DEFAULT_CALENDAR_MONTH
    return month


def _clamp_year(year: int | None) -> int:
    if year is None or year < min(AVAILABLE_YEARS) or year > max(AVAILABLE_YEARS):
        return DEFAULT_CALENDAR_YEAR
    return year


def _scale_int(value: int, factor: float) -> int:
    return max(0, int(round(value * factor)))


def _academic_year_label(start_year: int) -> str:
    return f"Aug {start_year} – Jun {start_year + 1}"


def _calendar_month_snapshot(month: int, year: int) -> dict[str, Any]:
    """Build a calendar-month view from the academic-year series + post dates.

    Mimics a Firebase/SQL query filtered to posted_at within [year-month].
    """
    month = _clamp_month(month)
    year = _clamp_year(year)
    label = f"{_MONTH_NAMES[month - 1]} {year}"

    # July sits outside the Aug–Jun academic series — use a light placeholder.
    if month == 7:
        snap = deepcopy(_MONTH)
        snap["date_range"] = label
        snap["months"] = ["W1", "W2", "W3", "W4"]
        snap["posts_by_month"] = [4, 5, 3, 2]
        snap["claims_by_month"] = [18, 24, 14, 10]
        snap["summary"] = {
            "total_posts": 14,
            "total_claims": 66,
            "claim_rate": 58,
            "avg_first_claim_min": 16.2,
            "lbs_diverted": 42,
            "tco2e": 0.02,
            "hauling_savings": 55,
        }
        snap["posts"] = []
        snap["waste_months"] = snap["months"]
        snap["waste_lbs"] = [8, 12, 10, 6]
        snap["climate_months"] = snap["months"]
        snap["climate_tco2"] = [0.004, 0.006, 0.005, 0.003]
        return snap

    idx = _ACADEMIC_MONTH_INDEX[month]
    year_posts = _YEAR["posts_by_month"][idx]
    year_claims = _YEAR["claims_by_month"][idx]
    # Spread the month total across four week buckets with a mild curve.
    week_weights = [0.2, 0.28, 0.3, 0.22]
    posts_by_week = [_scale_int(year_posts, w) for w in week_weights]
    claims_by_week = [_scale_int(year_claims, w) for w in week_weights]

    # Scale relative to a typical mid-year month (~90 posts) so KPIs shift by month.
    factor = year_posts / 90.0 if year_posts else 0.5
    # Slight year-to-year variation so changing year is visible in the demo.
    year_factor = 1.0 + 0.04 * (year - DEFAULT_CALENDAR_YEAR)
    factor *= year_factor

    snap = deepcopy(_MONTH)
    snap["date_range"] = label
    snap["months"] = ["W1", "W2", "W3", "W4"]
    snap["posts_by_month"] = posts_by_week
    snap["claims_by_month"] = claims_by_week
    snap["claims_by_hour"] = [_scale_int(v, factor) for v in _YEAR["claims_by_hour"]]
    snap["locations"] = [
        {
            "name": loc["name"],
            "posts": _scale_int(loc["posts"], factor / 10.0),
            "claim_rate": min(95, max(30, loc["claim_rate"] + (idx - 5))),
        }
        for loc in _YEAR["locations"]
    ]
    snap["demand_grid"] = [
        [max(0, min(20, _scale_int(cell, factor))) for cell in row] for row in _YEAR["demand_grid"]
    ]
    snap["staff"] = [
        {
            **member,
            "posts": _scale_int(member["posts"], factor / 10.0),
        }
        for member in _YEAR["staff"]
    ]
    snap["posts"] = [
        post
        for post in _YEAR["posts"]
        if post["posted_at"].startswith(f"{year}-{month:02d}")
    ]
    # If no sample posts fall in that month, keep the newest 1–2 as placeholders
    # so the Posts tab is never empty in the demo.
    if not snap["posts"]:
        snap["posts"] = deepcopy(_YEAR["posts"][: max(1, min(2, year_posts // 40 or 1))])

    snap["waste_months"] = snap["months"]
    snap["waste_lbs"] = [_scale_int(v, factor / 4.0) for v in (180, 220, 260, 200)]
    snap["climate_months"] = snap["months"]
    snap["climate_tco2"] = [round(0.01 * factor * w, 3) for w in (0.8, 1.0, 1.2, 0.9)]
    snap["summary"] = {
        "total_posts": year_posts if year_factor == 1.0 else _scale_int(year_posts, year_factor),
        "total_claims": year_claims if year_factor == 1.0 else _scale_int(year_claims, year_factor),
        "claim_rate": min(95, max(40, 60 + idx)),
        "avg_first_claim_min": round(14.0 - idx * 0.3, 1),
        "lbs_diverted": _scale_int(320, factor),
        "tco2e": round(0.11 * factor, 3),
        "hauling_savings": _scale_int(400, factor),
    }
    return snap


def _academic_year_snapshot(start_year: int) -> dict[str, Any]:
    start_year = _clamp_year(start_year)
    # Only 2025 has the full demo series; shift labels/factor for other years.
    snap = deepcopy(_YEAR)
    snap["date_range"] = _academic_year_label(start_year)
    if start_year != 2025:
        factor = 1.0 + 0.06 * (start_year - 2025)
        snap["posts_by_month"] = [_scale_int(v, factor) for v in snap["posts_by_month"]]
        snap["claims_by_month"] = [_scale_int(v, factor) for v in snap["claims_by_month"]]
        snap["claims_by_hour"] = [_scale_int(v, factor) for v in snap["claims_by_hour"]]
        snap["locations"] = [
            {**loc, "posts": _scale_int(loc["posts"], factor)} for loc in snap["locations"]
        ]
        snap["staff"] = [
            {**member, "posts": _scale_int(member["posts"], factor)} for member in snap["staff"]
        ]
        snap["waste_lbs"] = [_scale_int(v, factor) for v in snap["waste_lbs"]]
        snap["climate_tco2"] = [round(v * factor, 3) for v in snap["climate_tco2"]]
        summary = snap["summary"]
        snap["summary"] = {
            "total_posts": _scale_int(summary["total_posts"], factor),
            "total_claims": _scale_int(summary["total_claims"], factor),
            "claim_rate": summary["claim_rate"],
            "avg_first_claim_min": summary["avg_first_claim_min"],
            "lbs_diverted": _scale_int(summary["lbs_diverted"], factor),
            "tco2e": round(summary["tco2e"] * factor, 3),
            "hauling_savings": _scale_int(summary["hauling_savings"], factor),
        }
    return snap


def get_snapshot(
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """Return mock metrics for the requested filter.

    - week: rolling last-7-days snapshot
    - month: calendar month (month + year required; defaults to Jun 2026)
    - year: academic year starting in August of `year` (default 2025)

    Deep copy so handlers can mutate safely (same idea as materializing DB rows).
    """
    key = normalize_period(period)
    if key == "month":
        return _calendar_month_snapshot(_clamp_month(month), _clamp_year(year))
    if key == "year":
        # Academic year labeled by its August start year.
        start = _clamp_year(year) if year is not None else 2025
        # If caller passes calendar year 2026 while browsing "year", treat as AY 2025–26.
        if start == 2026:
            start = 2025
        return _academic_year_snapshot(start)
    return deepcopy(_SNAPSHOTS["week"])
