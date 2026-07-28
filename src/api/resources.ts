import { ApiError, type ApiErrorBody, type ApiErrorKind } from "../api";
import type { BulletinItem, Pantry, SpecialEvent } from "../appData";
import { getToken } from "./session";

export type ResourcesSnapshot = {
  pantries: Pantry[];
  events: Record<number, SpecialEvent[]>;
  bulletin: BulletinItem[];
};

export type PantryInput = Omit<Pantry, "id">;
export type BulletinInput = Omit<BulletinItem, "id">;
export type EventInput = Omit<SpecialEvent, "id"> & { day: number };

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

// Reads are public but campus-scoped; the SDSU demo apps default to "sdsu".
export async function fetchResources(universityId = "sdsu"): Promise<ResourcesSnapshot> {
  return request<ResourcesSnapshot>(
    `/api/resources?universityId=${encodeURIComponent(universityId)}`,
  );
}

export async function createPantry(body: PantryInput): Promise<Pantry> {
  return request<Pantry>("/api/resources/pantries", { method: "POST", body });
}

export async function updatePantry(id: string, body: PantryInput): Promise<Pantry> {
  return request<Pantry>(`/api/resources/pantries/${id}`, { method: "PATCH", body });
}

export async function deletePantry(id: string): Promise<void> {
  await request<void>(`/api/resources/pantries/${id}`, { method: "DELETE" });
}

export async function createEvent(body: EventInput): Promise<SpecialEvent> {
  return request<SpecialEvent>("/api/resources/events", { method: "POST", body });
}

export async function updateEvent(id: string, body: EventInput): Promise<SpecialEvent> {
  return request<SpecialEvent>(`/api/resources/events/${id}`, { method: "PATCH", body });
}

export async function deleteEvent(id: string): Promise<void> {
  await request<void>(`/api/resources/events/${id}`, { method: "DELETE" });
}

export async function createBulletin(body: BulletinInput): Promise<BulletinItem> {
  return request<BulletinItem>("/api/resources/bulletin", { method: "POST", body });
}

export async function updateBulletin(id: string, body: BulletinInput): Promise<BulletinItem> {
  return request<BulletinItem>(`/api/resources/bulletin/${id}`, { method: "PATCH", body });
}

export async function deleteBulletin(id: string): Promise<void> {
  await request<void>(`/api/resources/bulletin/${id}`, { method: "DELETE" });
}
