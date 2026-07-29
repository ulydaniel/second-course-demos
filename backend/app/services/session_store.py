"""Server-side revocation list for session tokens.

Logout records the token's `jti` here; `resolve_token` rejects any token whose
`jti` is present. Rows carry the token's original expiry so they can be purged
once they are no longer needed.
"""

import time

from app.db.session import SessionLocal
from app.models.revoked_session import RevokedSession


def revoke(jti: str, expires_at: int) -> None:
    with SessionLocal() as db:
        if db.get(RevokedSession, jti) is None:
            db.add(RevokedSession(jti=jti, expires_at=int(expires_at)))
            db.commit()


def is_revoked(jti: str) -> bool:
    with SessionLocal() as db:
        return db.get(RevokedSession, jti) is not None


def purge_expired(now: float | None = None) -> int:
    cutoff = int(now if now is not None else time.time())
    with SessionLocal() as db:
        deleted = (
            db.query(RevokedSession)
            .filter(RevokedSession.expires_at < cutoff)
            .delete()
        )
        db.commit()
        return deleted
