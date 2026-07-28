from fastapi import APIRouter, Depends

from app.dependencies.auth import require_administrator
from app.errors import raise_api_error
from app.schemas.auth import (
    CreateUserRequest,
    DashboardUserOut,
    UpdateUserRequest,
    UserStatus,
)
from app.services.identity import identity
from app.services.user_store import DashboardUser, serialize_user, user_store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[DashboardUserOut])
def list_users(
    status: UserStatus | None = None,
    admin: DashboardUser = Depends(require_administrator),
) -> list[DashboardUserOut]:
    # Campus admins only see their own tenant; platform admins see everyone.
    scope = None if admin.is_platform_admin else admin.university_id
    return [serialize_user(user) for user in user_store.list_users(status, university_id=scope)]


@router.post("/users", response_model=DashboardUserOut, status_code=201)
def create_user(
    payload: CreateUserRequest,
    admin: DashboardUser = Depends(require_administrator),
) -> DashboardUserOut:
    if user_store.get_university(payload.university_id) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")
    if not admin.is_platform_admin and payload.university_id != admin.university_id:
        raise_api_error(403, "forbidden", "You can only add users to your own campus.")
    if user_store.get_by_email(payload.email) is not None:
        raise_api_error(409, "already_exists", "A user with that email already exists.")

    user = user_store.create_approved(
        email=payload.email,
        full_name=payload.full_name,
        job_title=payload.job_title,
        dashboard_role=payload.dashboard_role,
        university_id=payload.university_id,
    )
    # Set credentials immediately so the account is usable without registration.
    identity.create_account(payload.email, payload.password)
    return serialize_user(user)


@router.patch("/users/{user_id}", response_model=DashboardUserOut)
def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    admin: DashboardUser = Depends(require_administrator),
) -> DashboardUserOut:
    target = user_store.get_by_id(user_id)
    if target is None:
        raise_api_error(404, "not_found", "User not found.")

    if not admin.is_platform_admin:
        if target.university_id != admin.university_id:
            raise_api_error(403, "forbidden", "You can only manage users on your own campus.")
        if payload.university_id is not None and payload.university_id != admin.university_id:
            raise_api_error(403, "forbidden", "You cannot move a user to another campus.")

    if payload.university_id is not None and user_store.get_university(payload.university_id) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")

    user: DashboardUser | None = user_store.update(
        user_id,
        status=payload.status,
        dashboard_role=payload.dashboard_role,
        university_id=payload.university_id,
        job_title=payload.job_title,
        full_name=payload.full_name,
    )
    if user is None:
        raise_api_error(404, "not_found", "User not found.")
    return serialize_user(user)
