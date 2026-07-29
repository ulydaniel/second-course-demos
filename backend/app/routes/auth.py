from fastapi import APIRouter, Depends, Request

from app.config import settings
from app.dependencies.auth import get_bearer_token, get_current_user_optional
from app.errors import raise_api_error
from app.rate_limit import limiter
from app.schemas.auth import (
    DashboardUserOut,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from app.services.auth import login, register_account, revoke_token, token_for
from app.services.user_store import DashboardUser, serialize_user, user_store

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def login_user(request: Request, payload: LoginRequest) -> LoginResponse:
    user = login(payload.email, payload.password)
    if user is None:
        # Uniform response for unknown email and bad password (no enumeration).
        raise_api_error(401, "invalid_credentials", "Incorrect email or password.")
    return LoginResponse(token=token_for(user), status=user.status, user=serialize_user(user))


@router.post("/register", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def register_user(request: Request, payload: RegisterRequest) -> LoginResponse:
    if user_store.get_university(payload.university_id) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")
    if user_store.get_by_email(payload.email) is not None:
        # Never overwrite an existing account's credentials via registration.
        raise_api_error(
            409,
            "email_taken",
            "That email is already registered. Sign in instead, or contact an administrator.",
        )

    user = register_account(
        email=payload.email,
        full_name=payload.full_name,
        job_title=payload.job_title,
        university_id=payload.university_id,
        password=payload.password,
    )
    return LoginResponse(token=token_for(user), status=user.status, user=serialize_user(user))


@router.post("/logout")
def logout_user(token: str | None = Depends(get_bearer_token)) -> dict[str, str]:
    # Revoke server-side so the token cannot be replayed after logout.
    if token:
        revoke_token(token)
    return {"status": "ok"}


@router.get("/me", response_model=DashboardUserOut)
def read_me(user: DashboardUser | None = Depends(get_current_user_optional)) -> DashboardUserOut:
    if user is None:
        raise_api_error(401, "unauthorized", "No active session.")
    return serialize_user(user)
