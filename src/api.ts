import type { PostRecord, StaffMember } from "./data";
import { getToken } from "./api/session";

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

export type ApiErrorBody = {
  code: string;
  message: string;
  detail?: string | null;
};

export type ApiErrorKind = "network" | "client" | "server";

export class ApiError extends Error {
  readonly code: string;
  readonly status: number | null;
  readonly kind: ApiErrorKind;
  readonly detail: string | null;

  constructor(params: {
    message: string;
    code: string;
    status: number | null;
    kind: ApiErrorKind;
    detail?: string | null;
  }) {
    super(params.message);
    this.name = "ApiError";
    this.code = params.code;
    this.status = params.status;
    this.kind = params.kind;
    this.detail = params.detail ?? null;
  }

  get userMessage(): string {
    if (this.kind === "network") {
      return "Cannot reach the API server. Start the backend with uvicorn in the backend/ folder (port 8000).";
    }

    switch (this.code) {
      case "service_unavailable":
        return this.message;
      case "internal_error":
        return "The server encountered an unexpected error. Check the backend terminal for details.";
      case "not_found":
        return "An API endpoint was not found. The frontend and backend versions may be out of sync.";
      case "validation_error":
        return this.message !== "Request validation failed"
          ? this.message
          : "The request was invalid. Refresh the page and try again.";
      case "invalid_credentials":
        return this.message;
      case "not_registered":
        return this.message;
      default:
        return this.message;
    }
  }
}

function errorKindFromStatus(status: number): ApiErrorKind {
  if (status >= 500) return "server";
  return "client";
}

async function parseErrorBody(response: Response): Promise<ApiErrorBody | null> {
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object") {
      const record = body as Record<string, unknown>;
      if (typeof record.code === "string" && typeof record.message === "string") {
        return {
          code: record.code,
          message: record.message,
          detail: typeof record.detail === "string" ? record.detail : null,
        };
      }
      if (typeof record.detail === "string") {
        return {
          code: errorKindFromStatus(response.status) === "server" ? "internal_error" : "http_error",
          message: record.detail,
        };
      }
    }
  } catch {
    return null;
  }
  return null;
}

function toApiError(error: unknown, path: string): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof TypeError) {
    return new ApiError({
      message: `Network error while requesting ${path}`,
      code: "network_error",
      status: null,
      kind: "network",
      detail: error.message,
    });
  }

  if (error instanceof Error) {
    return new ApiError({
      message: error.message,
      code: "unknown_error",
      status: null,
      kind: "network",
      detail: error.message,
    });
  }

  return new ApiError({
    message: `Request failed for ${path}`,
    code: "unknown_error",
    status: null,
    kind: "network",
  });
}

async function fetchJson<T>(path: string): Promise<T> {
  try {
    const token = getToken();
    const response = await fetch(path, token ? { headers: { Authorization: `Bearer ${token}` } } : undefined);
    if (!response.ok) {
      const body = await parseErrorBody(response);
      throw new ApiError({
        message: body?.message ?? `API request failed (${response.status} ${response.statusText})`,
        code: body?.code ?? (response.status >= 500 ? "internal_error" : "http_error"),
        status: response.status,
        kind: errorKindFromStatus(response.status),
        detail: body?.detail ?? null,
      });
    }

    return (await response.json()) as T;
  } catch (error) {
    throw toApiError(error, path);
  }
}

function aggregateApiErrors(failures: { label: string; error: ApiError }[]): ApiError {
  const labels = failures.map((failure) => failure.label).join(", ");
  const primary =
    failures.find((failure) => failure.error.kind === "server")?.error ??
    failures.find((failure) => failure.error.kind === "network")?.error ??
    failures[0].error;

  return new ApiError({
    message: `Could not load dashboard data (${labels}).`,
    code: primary.code,
    status: primary.status,
    kind: primary.kind,
    detail: failures.map((failure) => `${failure.label}: ${failure.error.userMessage}`).join(" "),
  });
}

export type DashboardPeriod = "week" | "month" | "year";

export type DashboardFilters = {
  period: DashboardPeriod;
  /** Calendar month 1–12 — used when period is "month" */
  month: number;
  /** Calendar year, or academic-year August start when period is "year" */
  year: number;
};

export async function fetchDashboardData(filters: DashboardFilters): Promise<DashboardData> {
  const params = new URLSearchParams({ period: filters.period });
  if (filters.period === "month") {
    params.set("month", String(filters.month));
    params.set("year", String(filters.year));
  } else if (filters.period === "year") {
    params.set("year", String(filters.year));
  }
  const qs = `?${params.toString()}`;
  const requests = [
    { label: "overview", promise: fetchJson<OverviewResponse>(`/api/overview${qs}`) },
    { label: "posts", promise: fetchJson<PostRecord[]>(`/api/posts${qs}`) },
    { label: "demand", promise: fetchJson<DemandResponse>(`/api/demand${qs}`) },
    { label: "staff", promise: fetchJson<StaffMember[]>(`/api/staff${qs}`) },
    { label: "impact", promise: fetchJson<ImpactResponse>(`/api/impact${qs}`) },
  ] as const;

  const results = await Promise.allSettled(requests.map((request) => request.promise));
  const failures: { label: string; error: ApiError }[] = [];

  results.forEach((result, index) => {
    if (result.status === "rejected") {
      failures.push({
        label: requests[index].label,
        error: toApiError(result.reason, `/api/${requests[index].label}`),
      });
    }
  });

  if (failures.length > 0) {
    throw aggregateApiErrors(failures);
  }

  const [overview, posts, demand, staff, impact] = results.map(
    (result) => (result as PromiseFulfilledResult<unknown>).value,
  ) as [OverviewResponse, PostRecord[], DemandResponse, StaffMember[], ImpactResponse];

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

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.userMessage;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Failed to load dashboard data";
}

export function getApiErrorKind(error: unknown): ApiErrorKind | null {
  return error instanceof ApiError ? error.kind : null;
}

export function getApiErrorCode(error: unknown): string | null {
  return error instanceof ApiError ? error.code : null;
}
