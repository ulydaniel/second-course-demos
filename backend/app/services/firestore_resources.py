"""Campus Resources authoring against the mobile app's Firestore collections.

The student app (DATA_CONTRACT.md §9) listens to:

  resources       — directory (pantries / programs / links)
  bulletins       — announcements
  resourceEvents  — food calendar

The dashboard API is the only writer. campusId is always taken from the
authenticated editor's tenant (via the route scope), never from the body.
Writes set `order` and real Firestore Timestamps so the app's queries can
see the documents.

Dashboard-only extras (`emoji`, `hoursSchedule`, `kind`, `blurb`, `tag`) are
stored alongside the contract fields so the portal can round-trip without
breaking the mobile schema.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, time, timezone
from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.query import Query

from app.schemas.resources import (
    BulletinItemIn,
    BulletinItemOut,
    PantryHour,
    PantryIn,
    PantryOut,
    ResourcesSnapshot,
    SpecialEventIn,
    SpecialEventOut,
)
from app.services.firestore_client import canonical_campus, get_client

logger = logging.getLogger(__name__)

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore

_CAMPUS_TZ_NAME = "America/Los_Angeles"
_CLOCK_RE = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*([ap])m?", re.I)


def _campus_tz():
    if ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(_CAMPUS_TZ_NAME)
    except Exception:
        return timezone.utc


def _campus_id(university_id: str) -> str:
    return canonical_campus(university_id) or university_id


def _hours_display(hours: list[PantryHour]) -> str:
    parts = [f"{h.day} {h.time}".strip() for h in hours if h.time]
    return "; ".join(parts)


def _hours_from_doc(data: dict[str, Any]) -> list[PantryHour]:
    schedule = data.get("hoursSchedule")
    if isinstance(schedule, list) and schedule:
        out: list[PantryHour] = []
        for row in schedule:
            if not isinstance(row, dict):
                continue
            out.append(
                PantryHour(
                    day=str(row.get("day") or ""),
                    weekday=int(row.get("weekday") or 0),
                    time=str(row.get("time") or ""),
                )
            )
        if out:
            return out
    hours = data.get("hours")
    if isinstance(hours, str) and hours.strip():
        return [PantryHour(day="", weekday=0, time=hours.strip())]
    return []


def _parse_clock(token: str) -> time:
    match = _CLOCK_RE.search(token.strip())
    if not match:
        return time(12, 0)
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3).lower()
    if meridiem == "p" and hour != 12:
        hour += 12
    if meridiem == "a" and hour == 12:
        hour = 0
    return time(min(hour, 23), min(minute, 59))


def _split_range(raw: str) -> tuple[str, str | None]:
    for sep in ("–", "—", "-", " to "):
        if sep in raw:
            left, right = raw.split(sep, 1)
            return left.strip(), right.strip()
    return raw.strip(), None


def _event_datetimes(payload: SpecialEventIn) -> tuple[datetime, datetime]:
    tz = _campus_tz()
    today = datetime.now(tz)
    year = payload.year or today.year
    month = payload.month or today.month
    start_token, end_token = _split_range(payload.time or "")
    start_clock = _parse_clock(start_token) if start_token else time(12, 0)
    end_clock = _parse_clock(end_token) if end_token else time(
        min(start_clock.hour + 2, 23), start_clock.minute
    )
    start = datetime(year, month, payload.day, start_clock.hour, start_clock.minute, tzinfo=tz)
    end = datetime(year, month, payload.day, end_clock.hour, end_clock.minute, tzinfo=tz)
    if end <= start:
        end = start.replace(hour=min(start.hour + 2, 23))
    return start, end


def _to_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    to_date = getattr(value, "to_datetime", None) or getattr(value, "ToDatetime", None)
    if callable(to_date):
        dt = to_date()
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return None


def _format_clock(dt: datetime) -> str:
    hour = dt.hour
    minute = dt.minute
    suffix = "a" if hour < 12 else "p"
    display = hour % 12 or 12
    if minute:
        return f"{display}:{minute:02d}{suffix}"
    return f"{display}{suffix}"


def _format_range(start: datetime, end: datetime | None) -> str:
    if end is None:
        return _format_clock(start)
    return f"{_format_clock(start)}–{_format_clock(end)}"


def _next_order(db, campus: str) -> int:
    docs = (
        db.collection("resources")
        .where(filter=FieldFilter("campusId", "==", campus))
        .stream()
    )
    highest = 0
    for doc in docs:
        data = doc.to_dict() or {}
        try:
            highest = max(highest, int(data.get("order") or 0))
        except (TypeError, ValueError):
            continue
    return highest + 10


def _pantry_from_doc(doc_id: str, data: dict[str, Any]) -> PantryOut:
    return PantryOut(
        id=doc_id,
        name=str(data.get("title") or ""),
        location=str(data.get("address") or ""),
        emoji=str(data.get("emoji") or "🥫"),
        note=str(data.get("description") or ""),
        hours=_hours_from_doc(data),
    )


def _event_from_doc(doc_id: str, data: dict[str, Any]) -> SpecialEventOut | None:
    start = _to_dt(data.get("startTime"))
    if start is None:
        return None
    tz = _campus_tz()
    local = start.astimezone(tz)
    end = _to_dt(data.get("endTime"))
    end_local = end.astimezone(tz) if end else None
    tag = data.get("tag")
    if tag not in ("food", "resource", "event"):
        tag = "food"
    return SpecialEventOut(
        id=doc_id,
        day=local.day,
        month=local.month,
        year=local.year,
        time=str(data.get("timeLabel") or _format_range(local, end_local)),
        title=str(data.get("title") or ""),
        tag=tag,
        note=str(data.get("location") or data.get("description") or "") or None,
    )


def _bulletin_from_doc(doc_id: str, data: dict[str, Any]) -> BulletinItemOut:
    kind = data.get("kind")
    if kind not in ("Article", "Recipe", "Tip"):
        kind = "Tip"
    body = str(data.get("body") or "")
    content = data.get("content")
    if not isinstance(content, list) or not content:
        content = [p for p in body.split("\n\n") if p] or ([body] if body else [])
    blurb = str(data.get("blurb") or "")
    if not blurb and content:
        blurb = str(content[0])[:160]
    return BulletinItemOut(
        id=doc_id,
        kind=kind,
        title=str(data.get("title") or ""),
        blurb=blurb,
        emoji=str(data.get("emoji") or "💡"),
        content=[str(p) for p in content],
    )


class FirestoreResourcesStore:
    """Read/write Resources against Firestore. Returns None from snapshot
    helpers only when the client cannot be built — callers fall back.
    """

    def snapshot(self, university_id: str) -> ResourcesSnapshot:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        campus = _campus_id(university_id)

        pantries: list[PantryOut] = []
        resources = (
            db.collection("resources")
            .where(filter=FieldFilter("campusId", "==", campus))
            .where(filter=FieldFilter("active", "==", True))
            .order_by("order")
            .stream()
        )
        for doc in resources:
            data = doc.to_dict() or {}
            if data.get("type") != "pantry":
                continue
            pantries.append(_pantry_from_doc(doc.id, data))

        events: dict[int, list[SpecialEventOut]] = {}
        far_past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        event_docs = (
            db.collection("resourceEvents")
            .where(filter=FieldFilter("campusId", "==", campus))
            .where(filter=FieldFilter("active", "==", True))
            .where(filter=FieldFilter("startTime", ">=", far_past))
            .order_by("startTime")
            .stream()
        )
        for doc in event_docs:
            mapped = _event_from_doc(doc.id, doc.to_dict() or {})
            if mapped is None:
                continue
            events.setdefault(mapped.day, []).append(mapped)

        bulletin: list[BulletinItemOut] = []
        bulletin_docs = (
            db.collection("bulletins")
            .where(filter=FieldFilter("campusId", "==", campus))
            .where(filter=FieldFilter("active", "==", True))
            .order_by("createdAt", direction=Query.DESCENDING)
            .limit(50)
            .stream()
        )
        for doc in bulletin_docs:
            bulletin.append(_bulletin_from_doc(doc.id, doc.to_dict() or {}))

        return ResourcesSnapshot(pantries=pantries, events=events, bulletin=bulletin)

    def add_pantry(self, university_id: str, payload: PantryIn) -> PantryOut:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        from google.cloud import firestore as fs

        campus = _campus_id(university_id)
        ref = db.collection("resources").document()
        hours = list(payload.hours)
        ref.set(
            {
                "campusId": campus,
                "type": "pantry",
                "title": payload.name.strip(),
                "description": payload.note,
                "address": payload.location,
                "hours": _hours_display(hours),
                "hoursSchedule": [h.model_dump() for h in hours],
                "emoji": payload.emoji,
                "order": _next_order(db, campus),
                "active": True,
                "updatedAt": fs.SERVER_TIMESTAMP,
            }
        )
        return PantryOut(id=ref.id, **payload.model_dump())

    def update_pantry(
        self, university_id: str, pantry_id: str, payload: PantryIn
    ) -> PantryOut | None:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        from google.cloud import firestore as fs

        campus = _campus_id(university_id)
        ref = db.collection("resources").document(pantry_id)
        snap = ref.get()
        if not snap.exists:
            return None
        existing = snap.to_dict() or {}
        if existing.get("campusId") != campus:
            return None
        hours = list(payload.hours)
        ref.update(
            {
                "title": payload.name.strip(),
                "description": payload.note,
                "address": payload.location,
                "hours": _hours_display(hours),
                "hoursSchedule": [h.model_dump() for h in hours],
                "emoji": payload.emoji,
                "active": True,
                "updatedAt": fs.SERVER_TIMESTAMP,
            }
        )
        return PantryOut(id=pantry_id, **payload.model_dump())

    def delete_pantry(self, university_id: str, pantry_id: str) -> bool:
        return self._soft_delete("resources", university_id, pantry_id)

    def add_event(self, university_id: str, payload: SpecialEventIn) -> SpecialEventOut:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        from google.cloud import firestore as fs

        campus = _campus_id(university_id)
        start, end = _event_datetimes(payload)
        ref = db.collection("resourceEvents").document()
        ref.set(
            {
                "campusId": campus,
                "title": payload.title.strip(),
                "description": payload.note or "",
                "location": payload.note or "",
                "startTime": start,
                "endTime": end,
                "active": True,
                "tag": payload.tag,
                "timeLabel": payload.time,
            }
        )
        return SpecialEventOut(
            id=ref.id,
            day=payload.day,
            month=start.month,
            year=start.year,
            time=payload.time,
            title=payload.title,
            tag=payload.tag,
            note=payload.note,
        )

    def update_event(
        self, university_id: str, event_id: str, payload: SpecialEventIn
    ) -> SpecialEventOut | None:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        campus = _campus_id(university_id)
        ref = db.collection("resourceEvents").document(event_id)
        snap = ref.get()
        if not snap.exists:
            return None
        existing = snap.to_dict() or {}
        if existing.get("campusId") != campus:
            return None
        start, end = _event_datetimes(payload)
        ref.update(
            {
                "title": payload.title.strip(),
                "description": payload.note or "",
                "location": payload.note or "",
                "startTime": start,
                "endTime": end,
                "active": True,
                "tag": payload.tag,
                "timeLabel": payload.time,
            }
        )
        return SpecialEventOut(
            id=event_id,
            day=payload.day,
            month=start.month,
            year=start.year,
            time=payload.time,
            title=payload.title,
            tag=payload.tag,
            note=payload.note,
        )

    def delete_event(self, university_id: str, event_id: str) -> bool:
        return self._soft_delete("resourceEvents", university_id, event_id)

    def add_bulletin(self, university_id: str, payload: BulletinItemIn) -> BulletinItemOut:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        from google.cloud import firestore as fs

        campus = _campus_id(university_id)
        body = "\n\n".join(payload.content) if payload.content else payload.blurb
        ref = db.collection("bulletins").document()
        ref.set(
            {
                "campusId": campus,
                "title": payload.title.strip(),
                "body": body,
                "active": True,
                "pinned": payload.kind == "Article",
                "createdAt": fs.SERVER_TIMESTAMP,
                "kind": payload.kind,
                "blurb": payload.blurb,
                "emoji": payload.emoji,
                "content": payload.content,
            }
        )
        return BulletinItemOut(id=ref.id, **payload.model_dump())

    def update_bulletin(
        self, university_id: str, item_id: str, payload: BulletinItemIn
    ) -> BulletinItemOut | None:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        campus = _campus_id(university_id)
        ref = db.collection("bulletins").document(item_id)
        snap = ref.get()
        if not snap.exists:
            return None
        existing = snap.to_dict() or {}
        if existing.get("campusId") != campus:
            return None
        body = "\n\n".join(payload.content) if payload.content else payload.blurb
        ref.update(
            {
                "title": payload.title.strip(),
                "body": body,
                "active": True,
                "pinned": payload.kind == "Article",
                "kind": payload.kind,
                "blurb": payload.blurb,
                "emoji": payload.emoji,
                "content": payload.content,
            }
        )
        return BulletinItemOut(id=item_id, **payload.model_dump())

    def delete_bulletin(self, university_id: str, item_id: str) -> bool:
        return self._soft_delete("bulletins", university_id, item_id)

    def _soft_delete(self, collection: str, university_id: str, doc_id: str) -> bool:
        db = get_client()
        if db is None:
            raise RuntimeError("Firestore client unavailable")
        campus = _campus_id(university_id)
        ref = db.collection(collection).document(doc_id)
        snap = ref.get()
        if not snap.exists:
            return False
        existing = snap.to_dict() or {}
        if existing.get("campusId") != campus:
            return False
        ref.update({"active": False})
        return True
