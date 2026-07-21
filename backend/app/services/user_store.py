"""In-memory allowlist store for dashboard users and universities.

This is the skeleton for the Firebase-backed allowlist described in the PRD
(university AllowList document -> approved dashboard_users). Routes depend only
on the `UserStore` protocol, so a FirebaseUserStore or SqlUserStore can drop in
later without any route changes.
"""

from dataclasses import dataclass
from itertools import count
from typing import Protocol

from app.config import settings
from app.schemas.auth import DashboardUserOut, UniversityOut


@dataclass
class University:
    id: str
    name: str
    slug: str


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


class UserStore(Protocol):
    def list_universities(self) -> list[University]: ...
    def get_university(self, university_id: str) -> University | None: ...
    def get_by_email(self, email: str) -> DashboardUser | None: ...
    def get_by_id(self, user_id: str) -> DashboardUser | None: ...
    def list_users(self, status: str | None = None) -> list[DashboardUser]: ...
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


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class InMemoryUserStore:
    """Process-local store, seeded on construction. Data resets on restart."""

    def __init__(self) -> None:
        self._universities: dict[str, University] = {}
        self._users: dict[str, DashboardUser] = {}
        self._ids = count(1)
        self._seed()

    def _next_id(self) -> str:
        return f"u{next(self._ids)}"

    def _seed(self) -> None:
        from app.services.identity import identity

        default = University(id="sdsu", name=settings.university_name, slug="sdsu")
        seeded = [
            default,
            University(id="ucsd", name="UC San Diego", slug="ucsd"),
            University(id="csulb", name="CSU Long Beach", slug="csulb"),
        ]
        for university in seeded:
            self._universities[university.id] = university

        for email in settings.dev_admin_email_list:
            uid = identity.create_account(email, settings.dev_admin_password)
            user = DashboardUser(
                id=self._next_id(),
                email=email,
                full_name="Second Course Developer",
                job_title="admin",
                dashboard_role="administrator",
                university_id=default.id,
                status="approved",
                identity_uid=uid,
            )
            self._users[user.id] = user

    def list_universities(self) -> list[University]:
        return list(self._universities.values())

    def get_university(self, university_id: str) -> University | None:
        return self._universities.get(university_id)

    def get_by_email(self, email: str) -> DashboardUser | None:
        target = _normalize_email(email)
        for user in self._users.values():
            if user.email == target:
                return user
        return None

    def get_by_id(self, user_id: str) -> DashboardUser | None:
        return self._users.get(user_id)

    def list_users(self, status: str | None = None) -> list[DashboardUser]:
        users = list(self._users.values())
        if status is not None:
            users = [user for user in users if user.status == status]
        return users

    def register(
        self,
        email: str,
        full_name: str,
        job_title: str,
        university_id: str,
        identity_uid: str | None = None,
    ) -> DashboardUser:
        user = DashboardUser(
            id=self._next_id(),
            email=_normalize_email(email),
            full_name=full_name,
            job_title=job_title,
            dashboard_role="viewer",
            university_id=university_id,
            status="pending",
            identity_uid=identity_uid,
        )
        self._users[user.id] = user
        return user

    def create_approved(
        self,
        email: str,
        full_name: str,
        job_title: str,
        dashboard_role: str,
        university_id: str,
    ) -> DashboardUser:
        user = DashboardUser(
            id=self._next_id(),
            email=_normalize_email(email),
            full_name=full_name,
            job_title=job_title,
            dashboard_role=dashboard_role,
            university_id=university_id,
            status="approved",
        )
        self._users[user.id] = user
        return user

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
        user = self._users.get(user_id)
        if user is None:
            return None
        if status is not None:
            user.status = status
        if dashboard_role is not None:
            user.dashboard_role = dashboard_role
        if university_id is not None:
            user.university_id = university_id
        if job_title is not None:
            user.job_title = job_title
        if full_name is not None:
            user.full_name = full_name
        return user


user_store: UserStore = InMemoryUserStore()


def serialize_university(university: University) -> UniversityOut:
    return UniversityOut(id=university.id, name=university.name, slug=university.slug)


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
