"""FastAPI auth dependencies for the dashboard and admin routes."""

from fastapi import Depends, Header

from app.errors import raise_api_error
from app.services.auth import resolve_token
from app.services.user_store import DashboardUser


def _token_from_header(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_current_user_optional(
    authorization: str | None = Header(default=None),
) -> DashboardUser | None:
    token = _token_from_header(authorization)
    if token is None:
        return None
    return resolve_token(token)


def require_approved_user(
    user: DashboardUser | None = Depends(get_current_user_optional),
) -> DashboardUser:
    if user is None:
        raise_api_error(401, "unauthorized", "Sign in to access the dashboard.")
    if user.status != "approved":
        raise_api_error(403, "not_approved", "Your account is awaiting approval.")
    return user


def require_administrator(
    user: DashboardUser = Depends(require_approved_user),
) -> DashboardUser:
    if user.dashboard_role != "administrator":
        raise_api_error(403, "forbidden", "Administrator access is required.")
    return user
