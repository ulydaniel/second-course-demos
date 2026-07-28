"""SQLAlchemy model for universities (client tenants).

Each row is a client campus. Branding columns let the frontend theme itself per
tenant, and metrics/resources are scoped by `university_id` elsewhere.
"""

from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    # Branding for per-tenant white-labeling (nullable — falls back to defaults).
    short_name: Mapped[str | None] = mapped_column(nullable=True)
    primary_color: Mapped[str | None] = mapped_column(nullable=True)
    accent_color: Mapped[str | None] = mapped_column(nullable=True)
    logo_url: Mapped[str | None] = mapped_column(nullable=True)
