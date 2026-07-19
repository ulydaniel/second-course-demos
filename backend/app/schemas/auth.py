"""Auth and allowlist response shapes.

These back the /portal sign-in flow and the developer approvals UI. Field
aliases keep the JSON camelCase to match the frontend types in src/api/auth.ts,
following the same pattern as schemas/dashboard.py.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
    email: str = Field(min_length=3)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(min_length=3)
    full_name: str = Field(alias="fullName", min_length=1)
    job_title: JobTitle = Field(alias="jobTitle")
    university_id: str = Field(alias="universityId")


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
