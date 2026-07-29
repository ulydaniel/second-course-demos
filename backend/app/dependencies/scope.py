"""Tenant-scope dependency for dashboard routes.

Resolves which university's data an authenticated user may read. Campus users
are pinned to their own `university_id`; platform admins may target any campus
via `?universityId=`. Cross-tenant access by non-platform users is rejected.
"""

from fastapi import Depends, Query

from app.dependencies.auth import require_approved_user, require_resource_editor
from app.errors import raise_api_error
from app.services.user_store import DashboardUser, user_store


def dashboard_scope(
    user: DashboardUser = Depends(require_approved_user),
    university_id: str | None = Query(default=None, alias="universityId"),
) -> str:
    if user.is_platform_admin:
        target = university_id or user.university_id
        if target is None:
            raise_api_error(400, "university_required", "Select a university to view.")
    else:
        if university_id is not None and university_id != user.university_id:
            raise_api_error(403, "forbidden", "You cannot view another campus's data.")
        target = user.university_id
        if target is None:
            raise_api_error(403, "forbidden", "Your account is not assigned to a campus.")

    if user_store.get_university(target) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")
    return target


def resource_write_scope(
    user: DashboardUser = Depends(require_resource_editor),
    university_id: str | None = Query(default=None, alias="universityId"),
) -> str:
    """Resolve which campus an editor may mutate resources for.

    Campus editors are pinned to their own campus; platform admins may target any
    campus via `?universityId=`.
    """
    if user.is_platform_admin:
        target = university_id or user.university_id
        if target is None:
            raise_api_error(400, "university_required", "Select a university to edit.")
    else:
        if university_id is not None and university_id != user.university_id:
            raise_api_error(403, "forbidden", "You cannot edit another campus's resources.")
        target = user.university_id
        if target is None:
            raise_api_error(403, "forbidden", "Your account is not assigned to a campus.")

    if user_store.get_university(target) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")
    return target


def public_resource_scope(
    university_id: str | None = Query(default=None, alias="universityId"),
) -> str:
    """Validate the `universityId` for public resource reads (no auth)."""
    if not university_id:
        raise_api_error(400, "university_required", "A universityId is required.")
    if user_store.get_university(university_id) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")
    return university_id
