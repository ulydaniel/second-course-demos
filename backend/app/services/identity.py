"""Identity provider for dashboard user passwords.

Local mode now persists credentials in SQLite: `create_account` stores a
Fernet-wrapped PBKDF2 hash on the user's row (services/crypto.py), and `verify`
reads it back. This survives restarts and is shared across workers, unlike the
old in-process dict. Firebase mode creates the Auth user via the Admin SDK when
credentials exist and otherwise falls back to the durable local store.

Routes call `identity.create_account` / `identity.verify` only — swapping
providers does not change Portal or allowlist APIs.
"""

from __future__ import annotations

import os
from typing import Protocol

from app.config import settings
from app.services import crypto
from app.services.crypto import hash_password, verify_password  # re-exported
from app.services.user_store import user_store

__all__ = [
    "identity",
    "IdentityProvider",
    "LocalIdentityProvider",
    "FirebaseIdentityProvider",
    "build_identity_provider",
    "hash_password",
    "verify_password",
    "validate_password_pair",
]


class IdentityProvider(Protocol):
    def create_account(self, email: str, password: str) -> str:
        """Create credentials for email/password. Returns provider user id."""
        ...

    def verify(self, email: str, password: str) -> bool:
        """Return True when email/password are valid."""
        ...

    def has_credentials(self, email: str) -> bool:
        ...


def _normalize(email: str) -> str:
    return email.strip().lower()


class LocalIdentityProvider:
    """Persists Fernet-wrapped PBKDF2 hashes on the dashboard_users row."""

    def create_account(self, email: str, password: str) -> str:
        key = _normalize(email)
        wrapped = crypto.hash_and_encrypt(password)
        user_store.set_password_hash(key, wrapped)
        return f"local:{key}"

    def verify(self, email: str, password: str) -> bool:
        stored = user_store.get_password_hash(_normalize(email))
        if not stored:
            return False
        return crypto.verify_encrypted(password, stored)

    def has_credentials(self, email: str) -> bool:
        return user_store.get_password_hash(_normalize(email)) is not None

    def seed(self, email: str, password: str) -> None:
        self.create_account(email, password)


class FirebaseIdentityProvider:
    """Create/verify users in Firebase Auth when Admin credentials are present.

    Until `FIREBASE_CREDENTIALS_PATH` (or GOOGLE_APPLICATION_CREDENTIALS) is set,
    create_account falls back to the durable local store so the API keeps working.
    """

    def __init__(self) -> None:
        self._app = None
        self._local_fallback = LocalIdentityProvider()
        self._init_firebase()

    def _init_firebase(self) -> None:
        cred_path = settings.firebase_credentials_path or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS", ""
        )
        if not cred_path or not os.path.isfile(cred_path):
            return
        try:
            import firebase_admin
            from firebase_admin import credentials
        except ImportError:
            return
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        self._app = firebase_admin.get_app()

    @property
    def ready(self) -> bool:
        return self._app is not None

    def create_account(self, email: str, password: str) -> str:
        if not self.ready:
            return self._local_fallback.create_account(email, password)
        from firebase_admin import auth

        record = auth.create_user(email=_normalize(email), password=password)
        return record.uid

    def verify(self, email: str, password: str) -> bool:
        """Server-side password check.

        Firebase Admin cannot verify a password directly; production sign-in
        should use the Firebase client SDK (ID token) on the frontend. Until
        that lands, fall back to the durable local hash used at create time.
        """
        if self._local_fallback.has_credentials(email):
            return self._local_fallback.verify(email, password)
        return False

    def has_credentials(self, email: str) -> bool:
        if self._local_fallback.has_credentials(email):
            return True
        if not self.ready:
            return False
        from firebase_admin import auth

        try:
            auth.get_user_by_email(_normalize(email))
            return True
        except Exception:
            return False


def build_identity_provider() -> IdentityProvider:
    if settings.auth_provider == "firebase":
        return FirebaseIdentityProvider()
    return LocalIdentityProvider()


identity: IdentityProvider = build_identity_provider()


def validate_password_pair(password: str, confirm_password: str) -> str | None:
    """Return an error message if the password pair is invalid, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if password != confirm_password:
        return "Passwords do not match. Check for typos and try again."
    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    if not (has_letter and has_digit):
        return "Password must include at least one letter and one number."
    return None
