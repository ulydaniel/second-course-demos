"""Idempotent startup seeding: create tables, tenants, and platform admins.

Called from the app lifespan (main.py) after the engine is ready. Safe to run on
every boot — universities are upserted and admin credentials are (re)ensured.
"""

import logging

from app.config import settings
from app.db.session import Base, SessionLocal, engine
from app.models.university import University as UniversityModel

logger = logging.getLogger(__name__)

# Client tenants shipped with the demo, including per-campus branding used for
# white-labeling. `name` for sdsu falls back to the configured UNIVERSITY_NAME.
UNIVERSITY_SEEDS: list[dict[str, str | None]] = [
    {
        "id": "sdsu",
        "name": settings.university_name,
        "slug": "sdsu",
        "short_name": "SDSU",
        "primary_color": "#A6192E",
        "accent_color": "#000000",
        "logo_url": None,
    },
    {
        "id": "ucsd",
        "name": "UC San Diego",
        "slug": "ucsd",
        "short_name": "UCSD",
        "primary_color": "#182B49",
        "accent_color": "#FFCD00",
        "logo_url": None,
    },
    {
        "id": "csulb",
        "name": "CSU Long Beach",
        "slug": "csulb",
        "short_name": "CSULB",
        "primary_color": "#000000",
        "accent_color": "#FFC72C",
        "logo_url": None,
    },
    {
        "id": "southwestern",
        "name": "Southwestern College",
        "slug": "southwestern",
        "short_name": "SWC",
        "primary_color": "#C8102E",
        "accent_color": "#111111",
        "logo_url": None,
    },
]


def create_tables() -> None:
    # Importing the package registers every model on Base.metadata.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def seed_universities() -> None:
    with SessionLocal() as db:
        for spec in UNIVERSITY_SEEDS:
            row = db.get(UniversityModel, spec["id"])
            if row is None:
                db.add(UniversityModel(**spec))
            else:
                row.name = spec["name"]
                row.slug = spec["slug"]
                row.short_name = spec["short_name"]
                row.primary_color = spec["primary_color"]
                row.accent_color = spec["accent_color"]
                row.logo_url = spec["logo_url"]
        db.commit()


def seed_admins() -> None:
    # Import here so identity/user_store bind to the ready engine.
    from app.services.identity import identity
    from app.services.user_store import user_store

    for email in settings.dev_admin_email_list:
        existing = user_store.get_by_email(email)
        if existing is None:
            user_store.create_approved(
                email=email,
                full_name="Second Course Developer",
                job_title="admin",
                dashboard_role="administrator",
                university_id="sdsu",
                is_platform_admin=True,
            )
        # Ensure a credential exists (and matches the configured password).
        identity.create_account(email, settings.dev_admin_password)


def seed_all() -> None:
    create_tables()
    seed_universities()
    seed_admins()
    logger.info("Database seeded: %d universities, admins ensured.", len(UNIVERSITY_SEEDS))
