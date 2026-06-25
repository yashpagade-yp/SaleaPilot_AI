import { ActiveSessionState, LoginResponse } from "../types/models";

const AUTH_KEY = "salespilot.auth";
const SESSION_KEY = "salespilot.active-session";

export function saveAuthSession(payload: LoginResponse) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(payload));
}

export function loadAuthSession(): LoginResponse | null {
  const raw = localStorage.getItem(AUTH_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as LoginResponse;
  } catch {
    return null;
  }
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_KEY);
}

export function saveActiveSession(session: ActiveSessionState) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function loadActiveSession(): ActiveSessionState | null {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as ActiveSessionState;
  } catch {
    return null;
  }
}

export function clearActiveSession() {
  sessionStorage.removeItem(SESSION_KEY);
}
