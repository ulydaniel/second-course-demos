"""Response shapes for the University Dashboard API.

These mirror the frontend types in src/data.ts and map to the metrics
spreadsheet (resources/Second Course Data Metrics - Sheet1.csv).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LocationMetric(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str
    posts: int
    claim_rate: int = Field(alias="claimRate")


class StaffMember(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str
    role: str
    posts: int
    last_post: str = Field(alias="lastPost")
    avg_claim_min: float = Field(alias="avgClaimMin")
    utilization: Literal["high", "medium", "low"]


class PostRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    title: str
    staff: str
    location: str
    posted: str
    posted_at: str = Field(alias="postedAt")
    claims: int
    views: int
    claim_rate: int = Field(alias="claimRate")
    first_claim_min: float = Field(alias="firstClaimMin")
    allergens: str
    description: str
    lbs_diverted: int = Field(alias="lbsDiverted")


class SummaryKpis(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    total_posts: int = Field(alias="totalPosts")
    total_claims: int = Field(alias="totalClaims")
    claim_rate: int = Field(alias="claimRate")
    avg_first_claim_min: float = Field(alias="avgFirstClaimMin")
    lbs_diverted: int = Field(alias="lbsDiverted")
    tco2e: float
    hauling_savings: int = Field(alias="haulingSavings")


class OverviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    university: str
    date_range: str = Field(alias="dateRange")
    summary: SummaryKpis
    months: list[str]
    posts_by_month: list[int] = Field(alias="postsByMonth")
    claims_by_month: list[int] = Field(alias="claimsByMonth")
    hours: list[str]
    claims_by_hour: list[int] = Field(alias="claimsByHour")
    locations: list[LocationMetric]


class DemandResponse(BaseModel):
    locations: list[str]
    times: list[str]
    grid: list[list[int]]


class ImpactResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    waste_months: list[str] = Field(alias="wasteMonths")
    waste_lbs: list[int] = Field(alias="wasteLbs")
    climate_months: list[str] = Field(alias="climateMonths")
    climate_tco2: list[float] = Field(alias="climateTco2")
    summary: SummaryKpis
