"""SQLAlchemy model for revoked session tokens.

Logout (and forced revocation) inserts the token's `jti` here. `resolve_token`
rejects any token whose `jti` is present, giving stateless HMAC tokens a
server-side kill switch. `expires_at` lets a periodic cleanup drop rows once the
underlying token would have expired anyway.
"""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RevokedSession(Base):
    __tablename__ = "revoked_sessions"

    jti: Mapped[str] = mapped_column(primary_key=True)
    # Unix timestamp (seconds) of the token's original expiry.
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)
