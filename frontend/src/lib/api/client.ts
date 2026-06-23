import type { ApiErrorShape } from "../../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface RequestOptions extends RequestInit {
  token?: string | null;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers ?? {});
  headers.set("Content-Type", "application/json");

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = (await tryParseJson(response)) as ApiErrorShape | null;
    const message =
      payload?.detail || payload?.message || "Something went wrong. Please try again.";
    throw new ApiError(message, response.status);
  }

  return (await response.json()) as T;
}

async function tryParseJson(response: Response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export { API_BASE_URL };
