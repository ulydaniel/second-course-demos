from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_optional
from app.errors import raise_api_error
from app.schemas.auth import (
    DashboardUserOut,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from app.services.auth import login, register_account, token_for
from app.services.user_store import DashboardUser, serialize_user, user_store

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login_user(payload: LoginRequest) -> LoginResponse:
    user = login(payload.email, payload.password)
    if user is None:
        # Distinguish unknown email vs bad password for clearer portal UX.
        if user_store.get_by_email(payload.email) is None:
            raise_api_error(
                404,
                "not_registered",
                "That email has not requested access yet.",
            )
        raise_api_error(
            401,
            "invalid_credentials",
            "Incorrect email or password.",
        )
    return LoginResponse(token=token_for(user), status=user.status, user=serialize_user(user))


@router.post("/register", response_model=LoginResponse)
def register_user(payload: RegisterRequest) -> LoginResponse:
    if user_store.get_university(payload.university_id) is None:
        raise_api_error(400, "unknown_university", "Select a valid university.")

    user = register_account(
        email=payload.email,
        full_name=payload.full_name,
        job_title=payload.job_title,
        university_id=payload.university_id,
        password=payload.password,
    )
    return LoginResponse(token=token_for(user), status=user.status, user=serialize_user(user))


@router.post("/logout")
def logout_user() -> dict[str, str]:
    # Tokens are stateless; the client discards its stored session.
    return {"status": "ok"}


@router.get("/me", response_model=DashboardUserOut)
def read_me(user: DashboardUser | None = Depends(get_current_user_optional)) -> DashboardUserOut:
    if user is None:
        raise_api_error(401, "unauthorized", "No active session.")
    return serialize_user(user)
