from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Sentinel that must never survive into a running deployment. If the configured
# secret is empty or still this value, the app refuses to boot (see validator).
PLACEHOLDER_SESSION_SECRET = "dev-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    port: int = 8000
    cors_origins: str = "http://localhost:5173"
    database_url: str = "sqlite:///./second_course.db"
    university_name: str = "San Diego State University"
    environment: str = "development"

    # Auth (local hashed passwords today; set AUTH_PROVIDER=firebase when ready)
    session_secret: str = PLACEHOLDER_SESSION_SECRET
    # Session tokens expire this many seconds after issue (default 8 hours).
    session_ttl_seconds: int = 28800
    auth_provider: str = "local"
    firebase_credentials_path: str | None = None
    dev_admin_emails: str = "dev@secondcourse.co"
    # Required from .env / environment — no default in source
    dev_admin_password: str
    # slowapi rate-limit string applied to the auth endpoints.
    rate_limit_auth: str = "10/minute"

    @model_validator(mode="after")
    def _reject_placeholder_secret(self) -> "Settings":
        secret = (self.session_secret or "").strip()
        if not secret or secret == PLACEHOLDER_SESSION_SECRET:
            raise ValueError(
                "SESSION_SECRET is unset or still the placeholder. Set SESSION_SECRET "
                "in backend/.env to a long random value (e.g. `python -c \"import secrets; "
                "print(secrets.token_hex(32))\"`) before starting the server."
            )
        if len(secret) < 32:
            raise ValueError(
                "SESSION_SECRET is too short. Use at least 32 characters of randomness."
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def dev_admin_email_list(self) -> list[str]:
        return [email.strip().lower() for email in self.dev_admin_emails.split(",") if email.strip()]


settings = Settings()
