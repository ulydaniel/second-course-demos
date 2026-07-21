"""Auth and allowlist response shapes.

These back the /portal sign-in flow and the developer approvals UI. Field
aliases keep the JSON camelCase to match the frontend types in src/api/auth.ts,
following the same pattern as schemas/dashboard.py.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

DashboardRole = Literal["administrator", "editor", "viewer"]
JobTitle = Literal["faculty", "representative", "admin", "dean", "staff", "other"]
UserStatus = Literal["pending", "approved", "rejected"]


class UniversityOut(BaseModel):
    id: str
    name: str
    slug: str


class DashboardUserOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    email: str
    full_name: str = Field(alias="fullName")
    job_title: JobTitle = Field(alias="jobTitle")
    dashboard_role: DashboardRole = Field(alias="dashboardRole")
    status: UserStatus
    university: UniversityOut | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(min_length=3)
    full_name: str = Field(alias="fullName", min_length=1)
    job_title: JobTitle = Field(alias="jobTitle")
    university_id: str = Field(alias="universityId")
    password: str = Field(min_length=8)
    confirm_password: str = Field(alias="confirmPassword", min_length=8)

    @model_validator(mode="after")
    def passwords_must_match_and_be_strong(self) -> Self:
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match. Check for typos and try again.")
        has_letter = any(char.isalpha() for char in self.password)
        has_digit = any(char.isdigit() for char in self.password)
        if not (has_letter and has_digit):
            raise ValueError("Password must include at least one letter and one number.")
        return self


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    token: str | None
    status: UserStatus
    user: DashboardUserOut


class CreateUserRequest(BaseModel):
    """Developer pre-approves an email before the user registers."""

    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(min_length=3)
    full_name: str = Field(alias="fullName", default="")
    job_title: JobTitle = Field(alias="jobTitle", default="staff")
    dashboard_role: DashboardRole = Field(alias="dashboardRole", default="viewer")
    university_id: str = Field(alias="universityId")


class UpdateUserRequest(BaseModel):
    """Developer approves/rejects and assigns role + university."""

    model_config = ConfigDict(populate_by_name=True)

    status: UserStatus
    dashboard_role: DashboardRole | None = Field(alias="dashboardRole", default=None)
    university_id: str | None = Field(alias="universityId", default=None)
    job_title: JobTitle | None = Field(alias="jobTitle", default=None)
    full_name: str | None = Field(alias="fullName", default=None)
