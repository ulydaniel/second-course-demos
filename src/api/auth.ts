import { ApiError, type ApiErrorBody, type ApiErrorKind } from "../api";
import { getToken, setToken } from "./session";

export { getToken, setToken } from "./session";

export type DashboardRole = "administrator" | "editor" | "viewer";
export type JobTitle = "faculty" | "representative" | "admin" | "dean" | "staff" | "other";
export type UserStatus = "pending" | "approved" | "rejected";

export type University = {
  id: string;
  name: string;
  slug: string;
};

export type DashboardUser = {
  id: string;
  email: string;
  fullName: string;
  jobTitle: JobTitle;
  dashboardRole: DashboardRole;
  status: UserStatus;
  university: University | null;
};

export type LoginResponse = {
  token: string | null;
  status: UserStatus;
  user: DashboardUser;
};

export type RegisterPayload = {
  email: string;
  fullName: string;
  jobTitle: JobTitle;
  universityId: string;
  password: string;
  confirmPassword: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type ApprovePayload = {
  status: UserStatus;
  dashboardRole?: DashboardRole;
  universityId?: string;
  jobTitle?: JobTitle;
  fullName?: string;
};

export type CreateUserPayload = {
  email: string;
  fullName?: string;
  jobTitle?: JobTitle;
  dashboardRole?: DashboardRole;
  universityId: string;
};

function errorKindFromStatus(status: number): ApiErrorKind {
  return status >= 500 ? "server" : "client";
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
    }
  } catch {
    return null;
  }
  return null;
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(path, {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch (error) {
    throw new ApiError({
      message: `Cannot reach the API server for ${path}.`,
      code: "network_error",
      status: null,
      kind: "network",
      detail: error instanceof Error ? error.message : null,
    });
  }

  if (!response.ok) {
    const body = await parseErrorBody(response);
    throw new ApiError({
      message: body?.message ?? `Request failed (${response.status} ${response.statusText}).`,
      code: body?.code ?? (response.status >= 500 ? "internal_error" : "http_error"),
      status: response.status,
      kind: errorKindFromStatus(response.status),
      detail: body?.detail ?? null,
    });
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const result = await request<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: payload,
  });
  setToken(result.token);
  return result;
}

export async function register(payload: RegisterPayload): Promise<LoginResponse> {
  const result = await request<LoginResponse>("/api/auth/register", {
    method: "POST",
    body: payload,
  });
  setToken(result.token);
  return result;
}

export async function logout(): Promise<void> {
  try {
    await request<{ status: string }>("/api/auth/logout", { method: "POST" });
  } finally {
    setToken(null);
  }
}

export async function fetchMe(): Promise<DashboardUser> {
  return request<DashboardUser>("/api/auth/me");
}

export async function listUniversities(): Promise<University[]> {
  return request<University[]>("/api/universities");
}

export async function listUsers(status?: UserStatus): Promise<DashboardUser[]> {
  const query = status ? `?status=${status}` : "";
  return request<DashboardUser[]>(`/api/admin/users${query}`);
}

export async function approveUser(id: string, payload: ApprovePayload): Promise<DashboardUser> {
  return request<DashboardUser>(`/api/admin/users/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export async function createUser(payload: CreateUserPayload): Promise<DashboardUser> {
  return request<DashboardUser>("/api/admin/users", {
    method: "POST",
    body: payload,
  });
}
