"""Campus Resources endpoints (pantries, calendar events, bulletin board).

Reads are public so the student Web/Mobile app can render without auth, but must
name a campus via `?universityId=` so each tenant only sees its own resources.
Writes require an approved editor or administrator and are scoped to that
editor's campus. Backed by Firestore (`resources` / `bulletins` /
`resourceEvents`) when configured, so the mobile app sees the same documents.
"""

from fastapi import APIRouter, Depends

from app.dependencies.scope import public_resource_scope, resource_write_scope
from app.errors import raise_api_error
from app.schemas.resources import (
    BulletinItemIn,
    BulletinItemOut,
    PantryIn,
    PantryOut,
    ResourcesSnapshot,
    SpecialEventIn,
    SpecialEventOut,
)
from app.services.resources_store import resources_store

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=ResourcesSnapshot)
def read_resources(university_id: str = Depends(public_resource_scope)) -> ResourcesSnapshot:
    return resources_store.snapshot(university_id)


# --- Pantries ---


@router.post("/pantries", response_model=PantryOut, status_code=201)
def create_pantry(
    payload: PantryIn,
    university_id: str = Depends(resource_write_scope),
) -> PantryOut:
    return resources_store.add_pantry(university_id, payload)


@router.patch("/pantries/{pantry_id}", response_model=PantryOut)
def update_pantry(
    pantry_id: str,
    payload: PantryIn,
    university_id: str = Depends(resource_write_scope),
) -> PantryOut:
    pantry = resources_store.update_pantry(university_id, pantry_id, payload)
    if pantry is None:
        raise_api_error(404, "not_found", "Pantry not found.")
    return pantry


@router.delete("/pantries/{pantry_id}", status_code=204)
def delete_pantry(
    pantry_id: str,
    university_id: str = Depends(resource_write_scope),
) -> None:
    if not resources_store.delete_pantry(university_id, pantry_id):
        raise_api_error(404, "not_found", "Pantry not found.")


# --- Calendar events ---


@router.post("/events", response_model=SpecialEventOut, status_code=201)
def create_event(
    payload: SpecialEventIn,
    university_id: str = Depends(resource_write_scope),
) -> SpecialEventOut:
    return resources_store.add_event(university_id, payload)


@router.patch("/events/{event_id}", response_model=SpecialEventOut)
def update_event(
    event_id: str,
    payload: SpecialEventIn,
    university_id: str = Depends(resource_write_scope),
) -> SpecialEventOut:
    event = resources_store.update_event(university_id, event_id, payload)
    if event is None:
        raise_api_error(404, "not_found", "Event not found.")
    return event


@router.delete("/events/{event_id}", status_code=204)
def delete_event(
    event_id: str,
    university_id: str = Depends(resource_write_scope),
) -> None:
    if not resources_store.delete_event(university_id, event_id):
        raise_api_error(404, "not_found", "Event not found.")


# --- Bulletin board ---


@router.post("/bulletin", response_model=BulletinItemOut, status_code=201)
def create_bulletin(
    payload: BulletinItemIn,
    university_id: str = Depends(resource_write_scope),
) -> BulletinItemOut:
    return resources_store.add_bulletin(university_id, payload)


@router.patch("/bulletin/{item_id}", response_model=BulletinItemOut)
def update_bulletin(
    item_id: str,
    payload: BulletinItemIn,
    university_id: str = Depends(resource_write_scope),
) -> BulletinItemOut:
    item = resources_store.update_bulletin(university_id, item_id, payload)
    if item is None:
        raise_api_error(404, "not_found", "Bulletin item not found.")
    return item


@router.delete("/bulletin/{item_id}", status_code=204)
def delete_bulletin(
    item_id: str,
    university_id: str = Depends(resource_write_scope),
) -> None:
    if not resources_store.delete_bulletin(university_id, item_id):
        raise_api_error(404, "not_found", "Bulletin item not found.")
