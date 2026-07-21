"""Identity provider for dashboard user passwords.

Local mode hashes passwords in-process (demo until Firebase is configured).
Firebase mode creates the Auth user via the Admin SDK when credentials exist.

Routes call `identity.create_account` / `identity.verify` only — swapping
providers does not change Portal or allowlist APIs.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Protocol

from app.config import settings


class IdentityProvider(Protocol):
    def create_account(self, email: str, password: str) -> str:
        """Create credentials for email/password. Returns provider user id."""
        ...

    def verify(self, email: str, password: str) -> bool:
        """Return True when email/password are valid."""
        ...

    def has_credentials(self, email: str) -> bool:
        ...


def hash_password(password: str, salt: str | None = None) -> str:
    """PBKDF2-SHA256 hash. Format: pbkdf2_sha256$iterations$salt$digest."""
    iterations = 120_000
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt_value}${digest}"


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


class LocalIdentityProvider:
    """In-memory email → password hash map (resets with the process)."""

    def __init__(self) -> None:
        self._hashes: dict[str, str] = {}

    def create_account(self, email: str, password: str) -> str:
        key = email.strip().lower()
        self._hashes[key] = hash_password(password)
        return f"local:{key}"

    def verify(self, email: str, password: str) -> bool:
        key = email.strip().lower()
        encoded = self._hashes.get(key)
        if encoded is None:
            return False
        return verify_password(password, encoded)

    def has_credentials(self, email: str) -> bool:
        return email.strip().lower() in self._hashes

    def seed(self, email: str, password: str) -> None:
        self.create_account(email, password)


class FirebaseIdentityProvider:
    """Create/verify users in Firebase Auth when Admin credentials are present.

    Until `FIREBASE_CREDENTIALS_PATH` (or GOOGLE_APPLICATION_CREDENTIALS) is set,
    create_account raises so the API can fall back or return a clear error.
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
            # Demo path: keep local hash until Firebase credentials are configured.
            return self._local_fallback.create_account(email, password)
        from firebase_admin import auth

        record = auth.create_user(email=email.strip().lower(), password=password)
        return record.uid

    def verify(self, email: str, password: str) -> bool:
        """Server-side password check.

        Firebase Admin cannot verify a password directly; production sign-in
        should use the Firebase client SDK (ID token) on the frontend.
        Until that lands, fall back to the local hash store used at create time.
        """
        if self._local_fallback.has_credentials(email):
            return self._local_fallback.verify(email, password)
        if not self.ready:
            return False
        # Firebase-only accounts: accept presence + rely on client ID tokens later.
        from firebase_admin import auth

        try:
            auth.get_user_by_email(email.strip().lower())
        except Exception:
            return False
        return False

    def has_credentials(self, email: str) -> bool:
        if self._local_fallback.has_credentials(email):
            return True
        if not self.ready:
            return False
        from firebase_admin import auth

        try:
            auth.get_user_by_email(email.strip().lower())
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
