"""Request/response shapes for the campus Resources feature.

These mirror the frontend types in src/appData.ts (Pantry, SpecialEvent,
BulletinItem). Field names are already camelCase-friendly, following the same
ConfigDict pattern as schemas/dashboard.py so a future SQL/Firebase store can
drop in without changing the JSON contract.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EventTag = Literal["food", "resource", "event"]
BulletinKind = Literal["Article", "Recipe", "Tip"]


class PantryHour(BaseModel):
    day: str
    weekday: int
    time: str


class PantryIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    location: str = ""
    emoji: str = "🥫"
    note: str = ""
    hours: list[PantryHour] = Field(default_factory=list)


class PantryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    name: str
    location: str
    emoji: str
    note: str
    hours: list[PantryHour]


class SpecialEventIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    day: int = Field(ge=1, le=31)
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000, le=2100)
    time: str = ""
    title: str = Field(min_length=1)
    tag: EventTag = "food"
    note: str | None = None


class SpecialEventOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    day: int
    month: int | None = None
    year: int | None = None
    time: str
    title: str
    tag: EventTag
    note: str | None = None


class BulletinItemIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    kind: BulletinKind = "Tip"
    title: str = Field(min_length=1)
    blurb: str = ""
    emoji: str = "💡"
    content: list[str] = Field(default_factory=list)


class BulletinItemOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    kind: BulletinKind
    title: str
    blurb: str
    emoji: str
    content: list[str]


class ResourcesSnapshot(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    pantries: list[PantryOut]
    events: dict[int, list[SpecialEventOut]]
    bulletin: list[BulletinItemOut]
