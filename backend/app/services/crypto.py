"""At-rest encryption + password hashing helpers.

Passwords are first hashed with PBKDF2-SHA256, then the encoded hash is wrapped
with Fernet (AES-128-CBC + HMAC) using a key derived from SESSION_SECRET. Storing
the *encrypted* hash means a leaked database file alone is not enough to run an
offline dictionary attack — the attacker also needs the runtime secret.

Routes never touch this module directly; identity.py calls hash_and_encrypt /
verify_encrypted, mirroring the previous local-hash provider surface.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

_PBKDF2_ITERATIONS = 120_000


def _fernet() -> Fernet:
    """Derive a stable 32-byte Fernet key from the session secret."""
    digest = hashlib.sha256(settings.session_secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def hash_password(password: str, salt: str | None = None) -> str:
    """PBKDF2-SHA256 hash. Format: pbkdf2_sha256$iterations$salt$digest."""
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        _PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt_value}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_s, salt, digest = encoded.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    try:
        iterations = int(iterations_s)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return hmac.compare_digest(candidate, digest)


def hash_and_encrypt(password: str) -> str:
    """Return a Fernet-encrypted PBKDF2 hash suitable for at-rest storage."""
    encoded = hash_password(password)
    return _fernet().encrypt(encoded.encode("utf-8")).decode("utf-8")


def verify_encrypted(password: str, stored: str) -> bool:
    """Verify a password against a Fernet-wrapped PBKDF2 hash."""
    if not stored:
        return False
    try:
        encoded = _fernet().decrypt(stored.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return False
    return verify_password(password, encoded)
