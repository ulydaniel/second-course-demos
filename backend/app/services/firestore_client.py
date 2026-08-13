"""Firestore access for analytics ingest (read-only mirror).

The dashboard reads the app's `posts`, `claims`, `post_views`, `users`, and
`campuses` collections with the Admin/Client SDK, which bypasses security rules
(the API is the tenant guard, per DATA_CONTRACT.md §1). This flow is strictly
one-way: we never write those collections back.

Two connection modes:
  - Emulator: `FIRESTORE_EMULATOR_HOST` set → AnonymousCredentials + project id.
  - Cloud: `FIREBASE_CREDENTIALS_PATH` / GOOGLE_APPLICATION_CREDENTIALS service
    account (falls back to application-default credentials).

`get_client()` returns a memoized client, or None when neither Firestore nor a
usable environment is configured — callers then fall back to mock_data.
"""

from __future__ import annotations

import logging
import os
import threading

from app.config import settings

logger = logging.getLogger(__name__)

# Retired campusId values that still appear on migrated documents, mapped to the
# campus they belong to. Normalise these before every tenant filter/grouping or
# the affected rows silently vanish from their tenant (DATA_CONTRACT.md §1, §8).
# The dashboard's Postgres tenant id for Southwestern is "southwestern"; the
# Firestore campus document id is "swccd", so this doubles as the id bridge.
CAMPUS_ALIASES = {"southwestern": "swccd"}

# Analytics collections we mirror. Never write to these.
ANALYTICS_COLLECTIONS = ("campuses", "posts", "claims", "post_views", "users")

_client = None
_client_lock = threading.Lock()
_init_failed = False


def canonical_campus(campus_id: str | None) -> str | None:
    """Map a retired campusId alias to its canonical Firestore id."""
    if campus_id is None:
        return None
    return CAMPUS_ALIASES.get(campus_id, campus_id)


def firestore_enabled() -> bool:
    """True when configuration allows a Firestore connection attempt."""
    if settings.metrics_source == "mock":
        return False
    host = settings.firestore_emulator_host or os.environ.get("FIRESTORE_EMULATOR_HOST")
    cred = settings.firebase_credentials_path or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if settings.metrics_source == "firestore":
        return True
    # auto: only when we have something to connect to.
    return bool(host or cred)


def get_client():
    """Return a memoized Firestore client, or None if unavailable."""
    global _client, _init_failed
    if _client is not None:
        return _client
    if _init_failed or not firestore_enabled():
        return None
    with _client_lock:
        if _client is not None:
            return _client
        if _init_failed:
            return None
        try:
            _client = _build_client()
        except Exception as exc:  # pragma: no cover - depends on environment
            _init_failed = True
            logger.warning("Firestore client unavailable, using mock data: %s", exc)
            return None
    return _client


def _build_client():
    from google.cloud import firestore

    project = settings.firestore_project_id or os.environ.get(
        "FIRESTORE_PROJECT_ID", "demo-second-course"
    )
    host = settings.firestore_emulator_host or os.environ.get("FIRESTORE_EMULATOR_HOST")

    if host:
        # Emulator: no real credentials, and the SDK reads FIRESTORE_EMULATOR_HOST
        # from the environment, so make sure it is set for both this client and
        # any listener threads.
        os.environ["FIRESTORE_EMULATOR_HOST"] = host
        from google.auth.credentials import AnonymousCredentials

        logger.info("Connecting to Firestore emulator at %s (project=%s)", host, project)
        return firestore.Client(project=project, credentials=AnonymousCredentials())

    cred_path = settings.firebase_credentials_path or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS"
    )
    if cred_path and os.path.isfile(cred_path):
        logger.info("Connecting to Firestore with service account %s", cred_path)
        return firestore.Client.from_service_account_json(cred_path, project=project)

    # Application-default credentials (e.g. GCP runtime / gcloud auth).
    logger.info("Connecting to Firestore with application-default credentials")
    return firestore.Client(project=project)
