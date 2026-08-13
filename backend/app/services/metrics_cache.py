"""In-memory cache of the mirrored Firestore analytics collections.

Reading five collections on every dashboard request would be wasteful, so we
snapshot them into memory and reuse the snapshot for a short TTL. To pick up new
posts, claims, and demographics without a redeploy (the "search Firestore for
new data on changes" requirement), we also attach `on_snapshot` listeners that
mark the cache dirty the moment any document changes — the next request then
refetches. Listeners run on background threads managed by the SDK; if they can't
be attached (older SDK, restricted env) we simply fall back to the TTL poll.

Only raw documents are cached here. Aggregation and privacy suppression happen
in firestore_metrics.py on top of this cache; no per-student data is persisted.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from app.config import settings
from app.services.firestore_client import ANALYTICS_COLLECTIONS, get_client

logger = logging.getLogger(__name__)


class MetricsCache:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: dict[str, list[dict[str, Any]]] = {}
        self._loaded_at = 0.0
        self._dirty = True
        self._listeners_attached = False
        self._watches: list[Any] = []

    def get_collections(self) -> dict[str, list[dict[str, Any]]] | None:
        """Return the cached collections, refreshing if stale/dirty.

        Returns None when Firestore is unavailable so callers fall back to mock.
        """
        client = get_client()
        if client is None:
            return None

        ttl = settings.firestore_cache_ttl_seconds
        with self._lock:
            fresh = (
                self._data
                and not self._dirty
                and (time.monotonic() - self._loaded_at) < ttl
            )
            if fresh:
                return self._data
            try:
                self._data = _fetch_all(client)
                self._loaded_at = time.monotonic()
                self._dirty = False
            except Exception as exc:
                logger.warning("Firestore fetch failed, using stale/mock: %s", exc)
                return self._data or None
            self._attach_listeners(client)
            return self._data

    def _attach_listeners(self, client) -> None:
        """Attach on_snapshot watchers once so changes invalidate the cache."""
        if self._listeners_attached:
            return
        self._listeners_attached = True  # only try once
        for name in ("posts", "claims", "users"):
            try:
                watch = client.collection(name).on_snapshot(self._make_callback(name))
                self._watches.append(watch)
            except Exception as exc:  # pragma: no cover - depends on SDK/env
                logger.info("on_snapshot unavailable for %s (TTL poll only): %s", name, exc)

    def _make_callback(self, name: str):
        def _on_snapshot(_col_snapshot, _changes, _read_time) -> None:
            with self._lock:
                self._dirty = True
            logger.debug("Firestore %s changed — metrics cache invalidated", name)

        return _on_snapshot


def _fetch_all(client) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for name in ANALYTICS_COLLECTIONS:
        docs = client.collection(name).stream()
        out[name] = [{"id": d.id, **(d.to_dict() or {})} for d in docs]
    return out


metrics_cache = MetricsCache()
