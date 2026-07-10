import type { PostRecord, StaffMember } from "./data";

export type SummaryKpis = {
  totalPosts: number;
  totalClaims: number;
  claimRate: number;
  avgFirstClaimMin: number;
  lbsDiverted: number;
  tco2e: number;
  haulingSavings: number;
};

export type LocationMetric = {
  name: string;
  posts: number;
  claimRate: number;
};

export type OverviewResponse = {
  university: string;
  dateRange: string;
  summary: SummaryKpis;
  months: string[];
  postsByMonth: number[];
  claimsByMonth: number[];
  hours: string[];
  claimsByHour: number[];
  locations: LocationMetric[];
};

export type DemandResponse = {
  locations: string[];
  times: string[];
  grid: number[][];
};

export type ImpactResponse = {
  wasteMonths: string[];
  wasteLbs: number[];
  climateMonths: string[];
  climateTco2: number[];
  summary: SummaryKpis;
};

export type DashboardData = {
  university: string;
  dateRange: string;
  summary: SummaryKpis;
  months: string[];
  postsByMonth: number[];
  claimsByMonth: number[];
  hours: string[];
  claimsByHour: number[];
  locations: LocationMetric[];
  posts: PostRecord[];
  demandGrid: number[][];
  demandLocations: string[];
  demandTimes: string[];
  staff: StaffMember[];
  wasteMonths: string[];
  wasteLbs: number[];
  climateMonths: string[];
  climateTco2: number[];
};

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchDashboardData(): Promise<DashboardData> {
  const [overview, posts, demand, staff, impact] = await Promise.all([
    fetchJson<OverviewResponse>("/api/overview"),
    fetchJson<PostRecord[]>("/api/posts"),
    fetchJson<DemandResponse>("/api/demand"),
    fetchJson<StaffMember[]>("/api/staff"),
    fetchJson<ImpactResponse>("/api/impact"),
  ]);

  return {
    university: overview.university,
    dateRange: overview.dateRange,
    summary: overview.summary,
    months: overview.months,
    postsByMonth: overview.postsByMonth,
    claimsByMonth: overview.claimsByMonth,
    hours: overview.hours,
    claimsByHour: overview.claimsByHour,
    locations: overview.locations,
    posts,
    demandGrid: demand.grid,
    demandLocations: demand.locations,
    demandTimes: demand.times,
    staff,
    wasteMonths: impact.wasteMonths,
    wasteLbs: impact.wasteLbs,
    climateMonths: impact.climateMonths,
    climateTco2: impact.climateTco2,
  };
}
