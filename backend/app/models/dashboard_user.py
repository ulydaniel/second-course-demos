"""SQLAlchemy stub for dashboard users — future migration target.

Mirrors the in-memory DashboardUser in services/user_store.py and the PRD
`dashboard_users` table (email, role, university_id) sourced from the university
AllowList. Not wired to any route yet.
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


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
