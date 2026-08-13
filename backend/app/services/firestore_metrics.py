"""Compute dashboard metrics from the mirrored Firestore collections.

Every formula here mirrors DATA_CONTRACT.md §5/§6 and the reference
implementation in the handoff's `verify-metrics.js`:

  - claim rate = claims / sum(posts.viewCount)   (unique viewers, not impressions)
  - food diverted = sum(claims.estimatedWeightLbs), backfilled from the post's
    keywords only when a legacy claim lacks the stamp (never recomputed otherwise)
  - student meal value = sum(claims.estimatedValue), same backfill rule
  - hauling savings = lbs x campuses.haulingUsdPerLb   (default $0.09/lb)
  - CO2e avoided = lbs x campuses.kgCo2ePerLbFood / 1000
  - HIDDEN posts excluded from every metric; hour-of-day uses campus timezone

Demographics are aggregated with per-campus `minCellSize` suppression and never
expose an individual student (no uid/email/displayName leaves this module).

`build_snapshot()` returns a dict with the same keys the mock snapshot exposes so
overview/posts/staff/impact stay identical, or None when Firestore is unavailable.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9
    ZoneInfo = None  # type: ignore

from app.services.firestore_client import canonical_campus
from app.services.metrics_cache import metrics_cache

logger = logging.getLogger(__name__)

_MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_HOUR_LABELS = ["6a", "8a", "10a", "12p", "2p", "4p", "6p", "8p"]

# Used only when a campus doc is missing or a factor is unset (contract §6).
_FALLBACK_CONFIG = {
    "minCellSize": 5,
    "kgCo2ePerLbFood": 1.16,
    "haulingUsdPerLb": 0.09,
    "dollarsPerMealDefault": 10,
    "lbsPerPortionDefault": 0.9,
    "timezone": "America/Los_Angeles",
}

# Portion value/weight heuristic, ported verbatim from generate-dataset.js /
# DATA_CONTRACT.md §4. Only used to backfill legacy claims that predate value
# stamping — the app-stamped values are authoritative and must not be recomputed.
_VALUE_RULES: list[tuple[list[str], float, float]] = [
    (["sushi", "poke"], 13, 0.8),
    (["pizza"], 5, 0.6),
    (["taco", "quesadilla"], 4, 0.4),
    (["sandwich", "sub", "wrap", "burger", "torta", "panini"], 9, 0.7),
    (["salad"], 10, 0.7),
    (["soup", "ramen", "pho"], 8, 1.0),
    (["breakfast", "pancake", "waffle", "omelet", "omelette"], 9, 0.8),
    (["bagel", "donut", "doughnut", "muffin", "pastry", "croissant", "scone"], 3.5, 0.25),
    (["cookie", "brownie", "cupcake", "dessert", "cake", "pie"], 3, 0.25),
    (["fruit", "produce", "vegetable", "veggies"], 3, 0.5),
    (["snack", "chips", "granola", "popcorn"], 2.5, 0.2),
    (["coffee", "latte", "boba", "tea", "smoothie", "juice", "drink", "soda"], 3.5, 0.9),
    (["grocery", "groceries", "pantry"], 15, 4.0),
    (
        ["burrito", "bowl", "plate", "entree", "pasta", "curry", "bbq",
         "catering", "catered", "tray", "buffet", "dinner", "lunch", "meal"],
        12,
        1.0,
    ),
]


def _match_rule(post: dict[str, Any]) -> tuple[float, float] | None:
    haystack = " ".join(
        str(part) for part in [post.get("title"), post.get("description"), *(post.get("tags") or [])] if part
    ).lower()
    for keywords, value, weight in _VALUE_RULES:
        for kw in keywords:
            # word-boundary-ish prefix match, first rule wins (matches JS \bkw)
            idx = haystack.find(kw)
            if idx != -1 and (idx == 0 or not haystack[idx - 1].isalnum()):
                return value, weight
    return None


def _portion_value(post: dict[str, Any], default: float) -> float:
    rule = _match_rule(post)
    if rule is None:
        return default
    return min(20.0, max(2.0, round(rule[0], 2)))


def _portion_weight(post: dict[str, Any], default: float) -> float:
    rule = _match_rule(post)
    return rule[1] if rule else default


def _to_dt(value: Any) -> datetime | None:
    """Coerce a Firestore Timestamp / datetime to an aware UTC datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    to_date = getattr(value, "to_datetime", None) or getattr(value, "ToDatetime", None)
    if callable(to_date):
        dt = to_date()
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return None


def _campus_config(campuses: list[dict[str, Any]], campus: str) -> dict[str, Any]:
    cfg = dict(_FALLBACK_CONFIG)
    doc = next((c for c in campuses if c.get("id") == campus), None)
    if doc:
        for key in _FALLBACK_CONFIG:
            if doc.get(key) is not None:
                cfg[key] = doc[key]
    return cfg


def _campus_tzinfo(cfg: dict[str, Any]):
    if ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(str(cfg.get("timezone") or "America/Los_Angeles"))
    except Exception:
        return timezone.utc


def _period_range(period: str | None, month: int | None, year: int | None, week_start: str | None, tz):
    """Return (start, end) aware datetimes for the filter, or (None, None) for all-time."""
    key = (period or "year").lower()
    if key == "year":
        start_year = year if year is not None else 2025
        if start_year == 2026:
            start_year = 2025
        # Academic year Aug(start) .. Jul(start+1); end is exclusive Aug(start+1).
        return (
            datetime(start_year, 8, 1, tzinfo=tz),
            datetime(start_year + 1, 8, 1, tzinfo=tz),
        )
    if key == "month":
        m = month if month and 1 <= month <= 12 else 6
        y = year if year else 2026
        start = datetime(y, m, 1, tzinfo=tz)
        end = datetime(y + 1, 1, 1, tzinfo=tz) if m == 12 else datetime(y, m + 1, 1, tzinfo=tz)
        return start, end
    if key == "week":
        try:
            parsed = datetime.fromisoformat(week_start).date() if week_start else None
        except ValueError:
            parsed = None
        if parsed is None:
            from datetime import date

            parsed = date(2026, 6, 8)
        monday = parsed.fromordinal(parsed.toordinal() - parsed.weekday())
        start = datetime(monday.year, monday.month, monday.day, tzinfo=tz)
        from datetime import timedelta

        return start, start + timedelta(days=7)
    return None, None


def _in_range(dt: datetime | None, start: datetime | None, end: datetime | None) -> bool:
    if start is None or end is None:
        return True
    if dt is None:
        return False
    return start <= dt < end


def _range_label(period: str | None, month: int | None, year: int | None, start: datetime | None, tz) -> str:
    key = (period or "year").lower()
    if key == "month" and start is not None:
        return f"{_MONTH_ABBR[start.month - 1]} {start.year}"
    if key == "week" and start is not None:
        from datetime import timedelta

        end = start + timedelta(days=6)
        return f"{_MONTH_ABBR[start.month - 1]} {start.day}–{end.day}, {end.year}"
    start_year = year if year is not None else 2025
    if start_year == 2026:
        start_year = 2025
    return f"Aug {start_year} – Jun {start_year + 1}"


def _scope_documents(cols: dict[str, list[dict[str, Any]]], campus: str):
    """Return (active_posts, claims, campus_config) scoped to one canonical campus."""
    campus_posts_all = [p for p in cols["posts"] if canonical_campus(p.get("campusId")) == campus]
    hidden_ids = {p["id"] for p in campus_posts_all if p.get("status") == "HIDDEN"}
    post_ids_all = {p["id"] for p in campus_posts_all}
    posts = [p for p in campus_posts_all if p.get("status") != "HIDDEN"]

    claims = []
    for c in cols["claims"]:
        cc = canonical_campus(c.get("campusId"))
        belongs = cc == campus or (cc is None and c.get("postId") in post_ids_all)
        if belongs and c.get("postId") not in hidden_ids:
            claims.append(c)
    return posts, claims


def build_snapshot(
    university_id: str | None = None,
    period: str | None = "year",
    month: int | None = None,
    year: int | None = None,
    week_start: str | None = None,
) -> dict[str, Any] | None:
    cols = metrics_cache.get_collections()
    if cols is None:
        return None
    try:
        return _compute_snapshot(cols, university_id, period, month, year, week_start)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Firestore metric computation failed, falling back: %s", exc)
        return None


def available_periods(university_id: str | None = None) -> dict[str, Any] | None:
    """List week / month / academic-year keys that have posts or claims.

    Returns None when Firestore is unavailable or the campus has no mirrored
    posts (caller should fall back to mock). Empty campus activity yields empty
    lists so the UI can hide all period options.
    """
    cols = metrics_cache.get_collections()
    if cols is None:
        return None
    try:
        return _compute_available_periods(cols, university_id)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Firestore available-periods failed, falling back: %s", exc)
        return None


def _compute_available_periods(cols, university_id: str | None) -> dict[str, Any] | None:
    from datetime import timedelta

    campus = canonical_campus(university_id or "sdsu")
    cfg = _campus_config(cols["campuses"], campus)
    tz = _campus_tzinfo(cfg)
    posts, claims = _scope_documents(cols, campus)
    if not posts:
        # Campus not mirrored in Firestore (e.g. csulb) — signal mock fallback.
        return None

    month_keys: set[tuple[int, int]] = set()
    week_keys: set[str] = set()
    academic_years: set[int] = set()

    def absorb(dt: datetime | None) -> None:
        if dt is None:
            return
        local = dt.astimezone(tz)
        month_keys.add((local.year, local.month))
        local_day = local.date()
        monday = local_day - timedelta(days=local_day.weekday())
        week_keys.add(monday.isoformat())
        ay = local.year if local.month >= 8 else local.year - 1
        academic_years.add(ay)

    for p in posts:
        absorb(_to_dt(p.get("createdAt")))
    for c in claims:
        absorb(_to_dt(c.get("createdAt")))

    months = [{"year": y, "month": m} for y, m in sorted(month_keys)]
    weeks = sorted(week_keys)
    ay_list = sorted(academic_years)

    periods: list[str] = []
    if weeks:
        periods.append("week")
    if months:
        periods.append("month")
    if ay_list:
        periods.append("year")

    return {
        "months": months,
        "weeks": weeks,
        "academic_years": ay_list,
        "periods": periods,
    }


def _compute_snapshot(cols, university_id, period, month, year, week_start) -> dict[str, Any] | None:
    campus = canonical_campus(university_id or "sdsu")
    cfg = _campus_config(cols["campuses"], campus)
    tz = _campus_tzinfo(cfg)
    start, end = _period_range(period, month, year, week_start, tz)

    posts, claims = _scope_documents(cols, campus)
    if not posts:
        # Campus not mirrored in Firestore (e.g. csulb) — signal mock fallback.
        return None
    post_by_id = {p["id"]: p for p in posts}

    posts_in = [p for p in posts if _in_range(_to_dt(p.get("createdAt")), start, end)]
    claims_in = [c for c in claims if _in_range(_to_dt(c.get("createdAt")), start, end)]
    post_in_ids = {p["id"] for p in posts_in}

    default_value = float(cfg["dollarsPerMealDefault"])
    default_weight = float(cfg["lbsPerPortionDefault"])

    def claim_value(c: dict[str, Any]) -> float:
        v = c.get("estimatedValue")
        if isinstance(v, (int, float)):
            return float(v)
        p = post_by_id.get(c.get("postId"))
        return _portion_value(p, default_value) if p else default_value

    def claim_weight(c: dict[str, Any]) -> float:
        w = c.get("estimatedWeightLbs")
        if isinstance(w, (int, float)):
            return float(w)
        p = post_by_id.get(c.get("postId"))
        return _portion_weight(p, default_weight) if p else default_weight

    total_views = sum(int(p.get("viewCount") or 0) for p in posts_in)
    total_claims = len(claims_in)
    total_posts = len(posts_in)
    lbs = sum(claim_weight(c) for c in claims_in)
    meal_value = sum(claim_value(c) for c in claims_in)
    claim_rate = round(total_claims / total_views * 100) if total_views else 0

    # Time to first claim (min claimDelaySeconds per post, mean across posts).
    first_by_post: dict[str, float] = {}
    for c in claims_in:
        delay = c.get("claimDelaySeconds")
        if not isinstance(delay, (int, float)):
            continue
        pid = c.get("postId")
        if pid not in first_by_post or delay < first_by_post[pid]:
            first_by_post[pid] = float(delay)
    first_mins = [s / 60 for s in first_by_post.values()]
    avg_first = round(sum(first_mins) / len(first_mins), 1) if first_mins else 0.0

    hauling = round(lbs * float(cfg["haulingUsdPerLb"]))
    tco2e = round(lbs * float(cfg["kgCo2ePerLbFood"]) / 1000, 2)

    # Per-post claim/weight aggregates for the Posts tab.
    claims_by_post: dict[str, int] = {}
    lbs_by_post: dict[str, float] = {}
    for c in claims_in:
        pid = c.get("postId")
        if pid not in post_in_ids:
            continue
        claims_by_post[pid] = claims_by_post.get(pid, 0) + 1
        lbs_by_post[pid] = lbs_by_post.get(pid, 0.0) + claim_weight(c)

    months, posts_by_month, claims_by_month = _series_by_month(posts_in, claims_in, tz)
    claims_by_hour = _series_by_hour(claims_in, tz)
    locations = _locations(posts_in, claims_in, post_by_id)
    post_records = _post_records(posts_in, claims_by_post, lbs_by_post, first_by_post, tz)
    users_by_id = {u["id"]: u for u in cols.get("users") or [] if u.get("id")}
    staff = _staff_records(posts_in, first_by_post, users_by_id, tz)
    waste_months, waste_lbs, climate_tco2 = _waste_series(claims_in, claim_weight, cfg, tz)

    summary = {
        "total_posts": total_posts,
        "total_claims": total_claims,
        "claim_rate": claim_rate,
        "avg_first_claim_min": avg_first,
        "lbs_diverted": round(lbs),
        "tco2e": tco2e,
        "hauling_savings": hauling,
        "meal_value": round(meal_value),
    }

    return {
        "date_range": _range_label(period, month, year, start, tz),
        "summary": summary,
        "months": months,
        "posts_by_month": posts_by_month,
        "claims_by_month": claims_by_month,
        "hours": _HOUR_LABELS,
        "claims_by_hour": claims_by_hour,
        "locations": locations,
        "posts": post_records,
        "staff": staff,
        "waste_months": waste_months,
        "waste_lbs": waste_lbs,
        "climate_months": waste_months,
        "climate_tco2": climate_tco2,
    }


def _series_by_month(posts_in, claims_in, tz):
    buckets: dict[str, dict[str, int]] = {}
    for p in posts_in:
        dt = _to_dt(p.get("createdAt"))
        if dt is None:
            continue
        key = dt.astimezone(tz).strftime("%Y-%m")
        buckets.setdefault(key, {"posts": 0, "claims": 0})["posts"] += 1
    for c in claims_in:
        dt = _to_dt(c.get("createdAt"))
        if dt is None:
            continue
        key = dt.astimezone(tz).strftime("%Y-%m")
        buckets.setdefault(key, {"posts": 0, "claims": 0})["claims"] += 1
    keys = sorted(buckets)
    months = [_MONTH_ABBR[int(k[5:7]) - 1] for k in keys]
    return months, [buckets[k]["posts"] for k in keys], [buckets[k]["claims"] for k in keys]


def _series_by_hour(claims_in, tz):
    counts = [0] * len(_HOUR_LABELS)
    for c in claims_in:
        dt = _to_dt(c.get("createdAt"))
        if dt is None:
            continue
        hour = dt.astimezone(tz).hour
        idx = (hour - 6) // 2
        idx = max(0, min(len(_HOUR_LABELS) - 1, idx))
        counts[idx] += 1
    return counts


def _locations(posts_in, claims_in, post_by_id):
    by_loc: dict[str, dict[str, int]] = {}
    for p in posts_in:
        name = (p.get("location") or {}).get("placeName") if isinstance(p.get("location"), dict) else None
        if not name or name == "Selected Location":
            continue
        entry = by_loc.setdefault(name, {"posts": 0, "claims": 0, "views": 0})
        entry["posts"] += 1
        entry["views"] += int(p.get("viewCount") or 0)
    for c in claims_in:
        p = post_by_id.get(c.get("postId"))
        name = (p.get("location") or {}).get("placeName") if p and isinstance(p.get("location"), dict) else None
        if name and name in by_loc:
            by_loc[name]["claims"] += 1
    rows = []
    for name, e in sorted(by_loc.items(), key=lambda kv: -kv[1]["posts"]):
        rate = round(e["claims"] / e["views"] * 100) if e["views"] else 0
        rows.append({"name": name, "posts": e["posts"], "claim_rate": rate})
    return rows[:8]


def _post_records(posts_in, claims_by_post, lbs_by_post, first_by_post, tz):
    records = []
    ordered = sorted(posts_in, key=lambda p: _to_dt(p.get("createdAt")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    for p in ordered:
        pid = p["id"]
        dt = _to_dt(p.get("createdAt"))
        local = dt.astimezone(tz) if dt else None
        posted = _human_time(local) if local else "—"
        posted_at = local.strftime("%Y-%m-%dT%H:%M") if local else ""
        views = int(p.get("viewCount") or 0)
        claims = claims_by_post.get(pid, 0)
        loc = (p.get("location") or {}).get("placeName") if isinstance(p.get("location"), dict) else None
        place = loc or (p.get("buildingRoom") or "—")
        if place == "Selected Location":
            place = "—"
        records.append(
            {
                "id": pid,
                "title": _pretty_title(p, place, local),
                "staff": p.get("posterName") or "Unknown organizer",
                "location": place,
                "posted": posted,
                "posted_at": posted_at,
                "claims": claims,
                "views": views,
                "claim_rate": round(claims / views * 100) if views else 0,
                "first_claim_min": round(first_by_post.get(pid, 0.0) / 60, 1),
                "allergens": p.get("allergenDietaryInfo") or "None listed",
                "description": p.get("description") or "",
                "lbs_diverted": round(lbs_by_post.get(pid, 0.0)),
            }
        )
    return records


# Display roles for known posting units (sandbox orgType is often wrong).
_DEPT_ROLE_BY_NAME = {
    "veterans center": "University Dept",
    "campus dining": "University Dept",
    "student health services": "University Dept",
    "pride center": "University Dept",
    "grad student association": "University Dept",
    "graduate student association": "University Dept",
    "computer science society": "Student Club",
    "residential education": "University Dept",
    "associated students": "University Dept",
}

_ORGTYPE_DISPLAY = {
    "student club": "Student Club",
    "greek life": "Greek Life",
    "cultural org": "Cultural Org",
    "athletics": "Athletics",
    "academic dept": "Academic Dept",
    "university dept / dining": "University Dept",
    "university dept": "University Dept",
    "other": "Other",
}


def _department_role(name: str, org_type: Any) -> str:
    mapped = _DEPT_ROLE_BY_NAME.get((name or "").strip().lower())
    if mapped:
        return mapped
    if isinstance(org_type, str) and org_type.strip():
        return _ORGTYPE_DISPLAY.get(org_type.strip().lower(), org_type.strip())
    return "Organizer"


def _staff_records(posts_in, first_by_post, users_by_id, tz):
    """Top organizers: group posts by posterId (DATA_CONTRACT.md §5)."""
    groups: dict[str, dict[str, Any]] = {}
    for p in posts_in:
        uid = p.get("posterId") or p.get("posterName") or "unknown"
        name = p.get("posterName") or "Unknown organizer"
        dt = _to_dt(p.get("createdAt"))
        g = groups.setdefault(uid, {"name": name, "posts": 0, "last_dt": None, "firsts": []})
        g["posts"] += 1
        if name and name != "Unknown organizer":
            g["name"] = name
        if dt is not None and (g["last_dt"] is None or dt > g["last_dt"]):
            g["last_dt"] = dt
        post_id = p.get("id")
        if post_id in first_by_post:
            g["firsts"].append(first_by_post[post_id] / 60)

    latest = max((g["last_dt"] for g in groups.values() if g["last_dt"]), default=None)
    ref = latest or datetime.now(timezone.utc)

    rows = []
    for uid, g in groups.items():
        user = users_by_id.get(uid) or {}
        last_dt = g["last_dt"]
        avg = round(sum(g["firsts"]) / len(g["firsts"]), 1) if g["firsts"] else 0.0
        rows.append(
            {
                "name": g["name"],
                "role": _department_role(g["name"], user.get("orgType")),
                "posts": g["posts"],
                "last_post": _relative_last_post(last_dt, ref, tz) if last_dt else "—",
                "avg_claim_min": avg,
                "utilization": _staff_utilization(last_dt, ref),
            }
        )
    rows.sort(key=lambda r: (-r["posts"], r["name"]))
    return rows


def _staff_utilization(last_dt: datetime | None, ref: datetime) -> str:
    if last_dt is None:
        return "low"
    days = (ref.astimezone(timezone.utc) - last_dt.astimezone(timezone.utc)).days
    if days <= 7:
        return "high"
    if days <= 21:
        return "medium"
    return "low"


def _relative_last_post(last_dt: datetime, ref: datetime, tz) -> str:
    local = last_dt.astimezone(tz)
    ref_local = ref.astimezone(tz)
    days = (ref_local.date() - local.date()).days
    if days <= 0:
        return f"Today, {_clock(local)}"
    if days == 1:
        return f"Yesterday, {_clock(local)}"
    if days < 14:
        return f"{days} days ago"
    return _human_time(local)


def _clock(local: datetime) -> str:
    hour12 = ((local.hour + 11) % 12) + 1
    ampm = "a" if local.hour < 12 else "p"
    return f"{hour12}:{local.minute:02d}{ampm}"


def _human_time(local: datetime) -> str:
    hour12 = ((local.hour + 11) % 12) + 1
    ampm = "a" if local.hour < 12 else "p"
    return f"{_MONTH_ABBR[local.month - 1]} {local.day}, {hour12}:{local.minute:02d}{ampm}"


_GENERATED_TITLE = re.compile(
    r"^(untitled(\s+post)?|none|n/?a|null|test|asdf|"
    r"post[_-]?[a-z0-9]+|p-\d+)$",
    re.IGNORECASE,
)
_UUIDISH = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _looks_like_generated_title(title: str) -> bool:
    """True for auto IDs like post_00430kise, UUIDs, or empty/untitled labels."""
    text = (title or "").strip()
    if not text:
        return True
    if _GENERATED_TITLE.match(text) or _UUIDISH.match(text):
        return True
    compact = re.sub(r"[\s_-]+", "", text)
    if " " not in text and text.lower().startswith("post") and compact.isalnum() and len(text) <= 40:
        return True
    return False


def _meal_window(local: datetime | None) -> str | None:
    if local is None:
        return None
    hour = local.hour
    if 6 <= hour < 11:
        return "Breakfast"
    if 11 <= hour < 15:
        return "Lunch"
    if 15 <= hour < 17:
        return "Afternoon"
    if 17 <= hour < 21:
        return "Dinner"
    return "Evening"


def _food_phrase(haystack: str) -> str | None:
    hay = haystack.lower()
    for keywords, _value, _weight in _VALUE_RULES:
        for kw in keywords:
            idx = hay.find(kw)
            if idx != -1 and (idx == 0 or not hay[idx - 1].isalnum()):
                if kw == "bbq":
                    return "BBQ"
                return kw.capitalize()
    return None


def _cleanup_human_title(title: str) -> str:
    cleaned = re.sub(r"[_-]+", " ", title).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _pretty_title(post: dict[str, Any], place: str, local: datetime | None) -> str:
    """Replace generated IDs with a readable leftover-food label."""
    raw = str(post.get("title") or "").strip()
    desc = str(post.get("description") or "").strip()
    tags = [str(t) for t in (post.get("tags") or []) if t]
    haystack = " ".join(part for part in [raw, desc, *tags] if part)

    if not _looks_like_generated_title(raw):
        return _cleanup_human_title(raw)

    if desc:
        sentence = re.split(r"[.!?\n]", desc, maxsplit=1)[0].strip()
        if sentence and not _looks_like_generated_title(sentence) and 8 <= len(sentence) <= 90:
            return sentence[0].upper() + sentence[1:]

    food = _food_phrase(haystack)
    meal = _meal_window(local)
    loc = place if place and place != "—" else None

    if food and loc:
        return f"{food} leftovers · {loc}"
    if food and meal:
        return f"{meal} {food.lower()}"
    if food:
        return f"{food} leftovers"
    if meal and loc:
        return f"{meal} leftovers · {loc}"
    if loc:
        return f"Leftover food · {loc}"
    if meal:
        return f"{meal} leftover food"
    return "Campus leftover food"


def _waste_series(claims_in, claim_weight, cfg, tz):
    lbs_by_month: dict[str, float] = {}
    for c in claims_in:
        dt = _to_dt(c.get("createdAt"))
        if dt is None:
            continue
        key = dt.astimezone(tz).strftime("%Y-%m")
        lbs_by_month[key] = lbs_by_month.get(key, 0.0) + claim_weight(c)
    keys = sorted(lbs_by_month)
    months = [_MONTH_ABBR[int(k[5:7]) - 1] for k in keys]
    waste_lbs = [round(lbs_by_month[k]) for k in keys]
    factor = float(cfg["kgCo2ePerLbFood"])
    climate = [round(lbs_by_month[k] * factor / 1000, 3) for k in keys]
    return months, waste_lbs, climate


def build_demographics(university_id: str | None = None) -> dict[str, Any] | None:
    """Aggregate students' demographics for one campus with small-cell suppression.

    Returns only bucket counts — never uid/email/displayName or an individual's
    answers. Buckets below the campus `minCellSize` are dropped (k-anonymity).
    Any demographics key present in the data is included automatically, so new
    signup questions surface without a code change.
    """
    cols = metrics_cache.get_collections()
    if cols is None:
        return None
    try:
        campus = canonical_campus(university_id or "sdsu")
        cfg = _campus_config(cols["campuses"], campus)
        min_cell = int(cfg.get("minCellSize") or 5)

        users = [u for u in cols["users"] if canonical_campus(u.get("campusId")) == campus]
        surveyed = [u for u in users if isinstance(u.get("demographics"), dict) and u["demographics"]]

        fields: dict[str, dict[str, int]] = {}
        for u in surveyed:
            for key, val in u["demographics"].items():
                counts = fields.setdefault(key, {})
                for item in (val if isinstance(val, list) else [val]):
                    if item is None or item == "":
                        continue
                    label = str(item)
                    counts[label] = counts.get(label, 0) + 1

        result_fields: dict[str, list[dict[str, Any]]] = {}
        suppressed = False
        for key, counts in fields.items():
            buckets = []
            for label, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
                if n < min_cell:
                    suppressed = True
                    continue
                buckets.append({"label": label, "count": n})
            if buckets:
                result_fields[key] = buckets

        return {
            "respondentCount": len(surveyed),
            "userCount": len(users),
            "minCellSize": min_cell,
            "suppressed": suppressed,
            "fields": result_fields,
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Firestore demographics computation failed: %s", exc)
        return None
