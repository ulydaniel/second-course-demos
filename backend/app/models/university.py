"""SQLAlchemy stub for universities — future migration target.

Mirrors the in-memory University in services/user_store.py. Not wired to any
route yet; kept here so the eventual SQL migration has a defined table shape.
"""

from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
