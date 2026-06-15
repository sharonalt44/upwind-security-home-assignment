/**
 * Centralized API module for the FastAPI backend.
 * Dynamically resolves target environment variables to prevent production environment breakage.
 */
import type { UserCreatePayload, UserUpdatePayload } from "./types";

// 🌐 Production Hardening: Resolve dynamic host addresses via environment setups
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/** Normalizes FastAPI error payloads (string or validation array) into a readable message. */
export function parseApiError(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (typeof entry === "object" && entry !== null && "msg" in entry) {
          const loc = "loc" in entry && Array.isArray(entry.loc) ? entry.loc.join(".") : "";
          return loc ? `${loc}: ${entry.msg}` : String(entry.msg);
        }
        return String(entry);
      })
      .join("; ");
  }
  return fallback;
}

async function readApiError(res: Response, fallback: string): Promise<string> {
  const errorData = await res.json().catch(() => ({}));
  return parseApiError(errorData.detail, fallback);
}

/** * ⏳ Centralized Session Guardrail: Monitors responses for 401 Unauthorized codes.
 * Intercepts stale or missing tokens instantly and forces clean UI context redirection.
 */
function handleAuthInterception(res: Response): void {
  if (res.status === 401) {
    // Prevent localized loops if already trying to resolve session identity checks
    if (!res.url.includes("/auth/me") && !res.url.includes("/auth/login")) {
      console.warn("Session trace expired. Executing dynamic boundary relocation...");
      // Wipe stale localized parameters and break execution back to auth routing
      window.location.href = "/login?expired=true";
    }
  }
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Login failed"));
  }

  return res.json();
}

/** * GET /events — Fetches telemetry chunks dynamically.
 * Fully integrates client UI metrics alongside production database pagination loops.
 */
export async function getEvents(skip: number = 0, limit: number = 10) {
  const res = await fetch(`${API_URL}/events?skip=${skip}&limit=${limit}`, {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error("Failed to fetch events");
  }

  return res.json();
}

export async function getCurrentUser() {
  const res = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error("Not authenticated");
  }

  return res.json();
}

export async function updateEvent(id: string, payload: Record<string, unknown>) {
  const res = await fetch(`${API_URL}/events/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to update event"));
  }

  return res.json();
}

export async function deleteEvent(id: string) {
  const res = await fetch(`${API_URL}/events/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to delete event"));
  }

  return res.json();
}

/** GET /users — list all non-deleted accounts (admin only). */
export async function getUsers() {
  const res = await fetch(`${API_URL}/users`, {
    method: "GET",
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to fetch users"));
  }

  return res.json();
}

/** POST /users — create a new account (admin only). */
export async function createUser(payload: UserCreatePayload) {
  const res = await fetch(`${API_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to create user"));
  }

  return res.json();
}

/** PATCH /users/{id} — update role and/or status (admin only). */
export async function updateUser(id: string, payload: UserUpdatePayload) {
  const res = await fetch(`${API_URL}/users/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to update user"));
  }

  return res.json();
}

/** DELETE /users/{id} — permanently remove an account (admin only). */
export async function deleteUser(id: string) {
  const res = await fetch(`${API_URL}/users/${id}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!res.ok) {
    handleAuthInterception(res);
    throw new Error(await readApiError(res, "Failed to delete user"));
  }

  return res.json();
}

export async function logout() {
  const res = await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  return res.ok;
}