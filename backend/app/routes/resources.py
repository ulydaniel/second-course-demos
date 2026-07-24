"""Campus Resources endpoints (pantries, calendar events, bulletin board).

Reads are public so the student Web/Mobile app can render without auth. Writes
require an approved editor or administrator, mirroring the frontend
`canEditResources` gate. Backed by the process-local `resources_store`.
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import require_resource_editor
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
def read_resources() -> ResourcesSnapshot:
    return resources_store.snapshot()


# --- Pantries ---


@router.post(
    "/pantries",
    response_model=PantryOut,
    status_code=201,
    dependencies=[Depends(require_resource_editor)],
)
def create_pantry(payload: PantryIn) -> PantryOut:
    return resources_store.add_pantry(payload)


@router.patch(
    "/pantries/{pantry_id}",
    response_model=PantryOut,
    dependencies=[Depends(require_resource_editor)],
)
def update_pantry(pantry_id: str, payload: PantryIn) -> PantryOut:
    pantry = resources_store.update_pantry(pantry_id, payload)
    if pantry is None:
        raise_api_error(404, "not_found", "Pantry not found.")
    return pantry


@router.delete(
    "/pantries/{pantry_id}",
    status_code=204,
    dependencies=[Depends(require_resource_editor)],
)
def delete_pantry(pantry_id: str) -> None:
    if not resources_store.delete_pantry(pantry_id):
        raise_api_error(404, "not_found", "Pantry not found.")


# --- Calendar events ---


@router.post(
    "/events",
    response_model=SpecialEventOut,
    status_code=201,
    dependencies=[Depends(require_resource_editor)],
)
def create_event(payload: SpecialEventIn) -> SpecialEventOut:
    return resources_store.add_event(payload)


@router.patch(
    "/events/{event_id}",
    response_model=SpecialEventOut,
    dependencies=[Depends(require_resource_editor)],
)
def update_event(event_id: str, payload: SpecialEventIn) -> SpecialEventOut:
    event = resources_store.update_event(event_id, payload)
    if event is None:
        raise_api_error(404, "not_found", "Event not found.")
    return event


@router.delete(
    "/events/{event_id}",
    status_code=204,
    dependencies=[Depends(require_resource_editor)],
)
def delete_event(event_id: str) -> None:
    if not resources_store.delete_event(event_id):
        raise_api_error(404, "not_found", "Event not found.")


# --- Bulletin board ---


@router.post(
    "/bulletin",
    response_model=BulletinItemOut,
    status_code=201,
    dependencies=[Depends(require_resource_editor)],
)
def create_bulletin(payload: BulletinItemIn) -> BulletinItemOut:
    return resources_store.add_bulletin(payload)


@router.patch(
    "/bulletin/{item_id}",
    response_model=BulletinItemOut,
    dependencies=[Depends(require_resource_editor)],
)
def update_bulletin(item_id: str, payload: BulletinItemIn) -> BulletinItemOut:
    item = resources_store.update_bulletin(item_id, payload)
    if item is None:
        raise_api_error(404, "not_found", "Bulletin item not found.")
    return item


@router.delete(
    "/bulletin/{item_id}",
    status_code=204,
    dependencies=[Depends(require_resource_editor)],
)
def delete_bulletin(item_id: str) -> None:
    if not resources_store.delete_bulletin(item_id):
        raise_api_error(404, "not_found", "Bulletin item not found.")
