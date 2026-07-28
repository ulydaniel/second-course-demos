"""Session token issuing/verification and the login/register flows.

Tokens are HMAC-signed over a base64 payload carrying `sub`, `iat`, `exp`, and a
random `jti`. `resolve_token` enforces expiry and checks the `jti` against the
server-side revocation list (services/session_store.py), so logout truly kills a
token. When Firebase client ID tokens land, replace create/resolve here and keep
the same call sites.
"""

import base64
import hashlib
import hmac
import json
import time
import uuid

from app.config import settings
from app.services import session_store
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
    now = int(time.time())
    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + settings.session_ttl_seconds,
        "jti": uuid.uuid4().hex,
    }
    payload = _b64encode(json.dumps(claims).encode())
    return f"{payload}.{_sign(payload)}"


def _decode_token(token: str) -> dict | None:
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
    return data if isinstance(data, dict) else None


def resolve_token(token: str) -> DashboardUser | None:
    data = _decode_token(token)
    if data is None:
        return None
    exp = data.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return None
    jti = data.get("jti")
    if isinstance(jti, str) and session_store.is_revoked(jti):
        return None
    user_id = data.get("sub")
    if not isinstance(user_id, str):
        return None
    return user_store.get_by_id(user_id)


def revoke_token(token: str) -> bool:
    """Add a token's jti to the revocation list. Returns False if unparseable."""
    data = _decode_token(token)
    if data is None:
        return False
    jti = data.get("jti")
    if not isinstance(jti, str):
        return False
    exp = data.get("exp")
    expires_at = exp if isinstance(exp, int) else int(time.time()) + settings.session_ttl_seconds
    session_store.revoke(jti, expires_at)
    return True


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
    """Create the allowlist row (pending) then set its credentials.

    Callers must first ensure the email is not already registered — re-using an
    existing email is rejected upstream (409) so a registration can never
    overwrite an existing account's password.
    """
    user = user_store.register(
        email=email,
        full_name=full_name,
        job_title=job_title,
        university_id=university_id,
    )
    identity.create_account(email, password)
    return user


def token_for(user: DashboardUser) -> str | None:
    """Only approved users receive a usable session token."""
    return create_session_token(user.id) if user.status == "approved" else None
