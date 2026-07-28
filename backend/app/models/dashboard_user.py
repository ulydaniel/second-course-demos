"""SQLAlchemy model for dashboard users (the university AllowList).

Credentials live here as `password_hash`: a PBKDF2 digest that is additionally
Fernet-encrypted at rest (see services/crypto.py), so a leaked DB file cannot be
used to offline-verify passwords without the SESSION_SECRET-derived key.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DashboardUser(Base):
    __tablename__ = "dashboard_users"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(default="")
    job_title: Mapped[str] = mapped_column(default="staff")
    dashboard_role: Mapped[str] = mapped_column(default="viewer")
    status: Mapped[str] = mapped_column(default="pending")
    university_id: Mapped[str | None] = mapped_column(
        ForeignKey("universities.id"), nullable=True
    )
    # Fernet-wrapped PBKDF2 hash. Null until credentials are set.
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    identity_uid: Mapped[str | None] = mapped_column(nullable=True)
    # Platform admins manage every tenant; campus admins are scoped to their own.
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )
