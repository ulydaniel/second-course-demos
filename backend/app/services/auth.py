"""Session token issuing/verification and the login-or-register flow.

Tokens are signed with an HMAC over a base64 payload — enough for the skeleton.
When Firebase client ID tokens land, replace `create_session_token` /
`resolve_token` with Firebase verification and keep the same call sites.
"""

import base64
import hashlib
import hmac
import json
import time

from app.config import settings
from app.services.identity import identity
from app.services.user_store import DashboardUser, user_store


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(payload: str) -> str:
    signature = hmac.new(
        settings.session_secret.encode(), payload.encode(), hashlib.sha256
    ).digest()
    return _b64encode(signature)


def create_session_token(user_id: str) -> str:
    payload = _b64encode(json.dumps({"sub": user_id, "iat": int(time.time())}).encode())
    return f"{payload}.{_sign(payload)}"


def resolve_token(token: str) -> DashboardUser | None:
    parts = token.split(".")
    if len(parts) != 2:
        return None
    payload, signature = parts
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    try:
        data = json.loads(_b64decode(payload))
    except (ValueError, json.JSONDecodeError):
        return None
    user_id = data.get("sub")
    if not isinstance(user_id, str):
        return None
    return user_store.get_by_id(user_id)


def login(email: str, password: str) -> DashboardUser | None:
    """Return the allowlisted user when email exists and password verifies."""
    user = user_store.get_by_email(email)
    if user is None:
        return None
    if not identity.verify(email, password):
        return None
    return user


def register_account(
    *,
    email: str,
    full_name: str,
    job_title: str,
    university_id: str,
    password: str,
) -> DashboardUser:
    """Create identity credentials (local hash or Firebase) then allowlist row."""
    existing = user_store.get_by_email(email)
    if existing is not None:
        # Re-request: refresh password credentials if they register again.
        identity.create_account(email, password)
        return existing

    identity_uid = identity.create_account(email, password)
    return user_store.register(
        email=email,
        full_name=full_name,
        job_title=job_title,
        university_id=university_id,
        identity_uid=identity_uid,
    )


def token_for(user: DashboardUser) -> str | None:
    """Only approved users receive a usable session token."""
    return create_session_token(user.id) if user.status == "approved" else None
