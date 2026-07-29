"""SQLite-backed allowlist store for dashboard users and universities.

Durable replacement for the previous in-memory skeleton: users, credentials
(Fernet-wrapped hashes), and university tenants survive process restarts and are
shared across workers. Routes and serializers still receive the lightweight
`DashboardUser` / `University` dataclasses, so nothing downstream changed shape.
"""

from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from app.db.session import SessionLocal
from app.models.dashboard_user import DashboardUser as DashboardUserModel
from app.models.university import University as UniversityModel
from app.schemas.auth import DashboardUserOut, UniversityOut


@dataclass
class University:
    id: str
    name: str
    slug: str
    short_name: str | None = None
    primary_color: str | None = None
    accent_color: str | None = None
    logo_url: str | None = None


@dataclass
class DashboardUser:
    id: str
    email: str
    full_name: str
    job_title: str
    dashboard_role: str
    university_id: str | None
    status: str
    identity_uid: str | None = None
    is_platform_admin: bool = False


class UserStore(Protocol):
    def list_universities(self) -> list[University]: ...
    def get_university(self, university_id: str) -> University | None: ...
    def get_by_email(self, email: str) -> DashboardUser | None: ...
    def get_by_id(self, user_id: str) -> DashboardUser | None: ...
    def list_users(
        self, status: str | None = None, university_id: str | None = None
    ) -> list[DashboardUser]: ...
    def register(
        self,
        email: str,
        full_name: str,
        job_title: str,
        university_id: str,
        identity_uid: str | None = None,
    ) -> DashboardUser: ...
    def create_approved(
        self,
        email: str,
        full_name: str,
        job_title: str,
        dashboard_role: str,
        university_id: str,
        is_platform_admin: bool = False,
    ) -> DashboardUser: ...
    def update(
        self,
        user_id: str,
        *,
        status: str | None = None,
        dashboard_role: str | None = None,
        university_id: str | None = None,
        job_title: str | None = None,
        full_name: str | None = None,
    ) -> DashboardUser | None: ...
    def set_password_hash(self, email: str, password_hash: str) -> bool: ...
    def get_password_hash(self, email: str) -> str | None: ...


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _next_id() -> str:
    return f"u{uuid4().hex[:12]}"


def _to_university(row: UniversityModel) -> University:
    return University(
        id=row.id,
        name=row.name,
        slug=row.slug,
        short_name=row.short_name,
        primary_color=row.primary_color,
        accent_color=row.accent_color,
        logo_url=row.logo_url,
    )


def _to_user(row: DashboardUserModel) -> DashboardUser:
    return DashboardUser(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        job_title=row.job_title,
        dashboard_role=row.dashboard_role,
        university_id=row.university_id,
        status=row.status,
        identity_uid=row.identity_uid,
        is_platform_admin=bool(row.is_platform_admin),
    )


class SqlUserStore:
    """Repository over the SQLAlchemy session; one session per call."""

    def list_universities(self) -> list[University]:
        with SessionLocal() as db:
            rows = db.query(UniversityModel).all()
            return [_to_university(row) for row in rows]

    def get_university(self, university_id: str) -> University | None:
        with SessionLocal() as db:
            row = db.get(UniversityModel, university_id)
            return _to_university(row) if row else None

    def get_by_email(self, email: str) -> DashboardUser | None:
        target = _normalize_email(email)
        with SessionLocal() as db:
            row = (
                db.query(DashboardUserModel)
                .filter(DashboardUserModel.email == target)
                .first()
            )
            return _to_user(row) if row else None

    def get_by_id(self, user_id: str) -> DashboardUser | None:
        with SessionLocal() as db:
            row = db.get(DashboardUserModel, user_id)
            return _to_user(row) if row else None

    def list_users(
        self, status: str | None = None, university_id: str | None = None
    ) -> list[DashboardUser]:
        with SessionLocal() as db:
            query = db.query(DashboardUserModel)
            if status is not None:
                query = query.filter(DashboardUserModel.status == status)
            if university_id is not None:
                query = query.filter(DashboardUserModel.university_id == university_id)
            return [_to_user(row) for row in query.all()]

    def register(
        self,
        email: str,
        full_name: str,
        job_title: str,
        university_id: str,
        identity_uid: str | None = None,
    ) -> DashboardUser:
        with SessionLocal() as db:
            row = DashboardUserModel(
                id=_next_id(),
                email=_normalize_email(email),
                full_name=full_name,
                job_title=job_title,
                dashboard_role="viewer",
                university_id=university_id,
                status="pending",
                identity_uid=identity_uid,
                is_platform_admin=False,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return _to_user(row)

    def create_approved(
        self,
        email: str,
        full_name: str,
        job_title: str,
        dashboard_role: str,
        university_id: str,
        is_platform_admin: bool = False,
    ) -> DashboardUser:
        with SessionLocal() as db:
            row = DashboardUserModel(
                id=_next_id(),
                email=_normalize_email(email),
                full_name=full_name,
                job_title=job_title,
                dashboard_role=dashboard_role,
                university_id=university_id,
                status="approved",
                is_platform_admin=is_platform_admin,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return _to_user(row)

    def update(
        self,
        user_id: str,
        *,
        status: str | None = None,
        dashboard_role: str | None = None,
        university_id: str | None = None,
        job_title: str | None = None,
        full_name: str | None = None,
    ) -> DashboardUser | None:
        with SessionLocal() as db:
            row = db.get(DashboardUserModel, user_id)
            if row is None:
                return None
            if status is not None:
                row.status = status
            if dashboard_role is not None:
                row.dashboard_role = dashboard_role
            if university_id is not None:
                row.university_id = university_id
            if job_title is not None:
                row.job_title = job_title
            if full_name is not None:
                row.full_name = full_name
            db.commit()
            db.refresh(row)
            return _to_user(row)

    def set_password_hash(self, email: str, password_hash: str) -> bool:
        target = _normalize_email(email)
        with SessionLocal() as db:
            row = (
                db.query(DashboardUserModel)
                .filter(DashboardUserModel.email == target)
                .first()
            )
            if row is None:
                return False
            row.password_hash = password_hash
            db.commit()
            return True

    def get_password_hash(self, email: str) -> str | None:
        target = _normalize_email(email)
        with SessionLocal() as db:
            row = (
                db.query(DashboardUserModel)
                .filter(DashboardUserModel.email == target)
                .first()
            )
            return row.password_hash if row else None


user_store: UserStore = SqlUserStore()


def serialize_university(university: University) -> UniversityOut:
    return UniversityOut(
        id=university.id,
        name=university.name,
        slug=university.slug,
        short_name=university.short_name,
        primary_color=university.primary_color,
        accent_color=university.accent_color,
        logo_url=university.logo_url,
    )


def serialize_user(user: DashboardUser) -> DashboardUserOut:
    university = (
        user_store.get_university(user.university_id) if user.university_id else None
    )
    return DashboardUserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        job_title=user.job_title,
        dashboard_role=user.dashboard_role,
        status=user.status,
        university=serialize_university(university) if university else None,
    )
