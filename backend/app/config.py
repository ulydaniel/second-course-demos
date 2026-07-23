from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    port: int = 8000
    cors_origins: str = "http://localhost:5173"
    database_url: str = "sqlite:///./second_course.db"
    university_name: str = "San Diego State University"

    # Auth (local hashed passwords today; set AUTH_PROVIDER=firebase when ready)
    session_secret: str = "dev-change-me"
    auth_provider: str = "local"
    dev_admin_emails: str = "dev@secondcourse.co"
    # Required from .env / environment — no default in source
    dev_admin_password: str

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def dev_admin_email_list(self) -> list[str]:
        return [email.strip().lower() for email in self.dev_admin_emails.split(",") if email.strip()]


settings = Settings()
