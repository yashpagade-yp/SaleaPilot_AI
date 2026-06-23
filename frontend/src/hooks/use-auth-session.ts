import { useState } from "react";

import { useLocalStorage } from "./use-local-storage";
import type { LoginResponse, UserProfile } from "../types/api";

const AUTH_STORAGE_KEY = "salespilot-auth-session";

interface AuthSessionState {
  accessToken: string | null;
  user: UserProfile | null;
}

const initialAuthState: AuthSessionState = {
  accessToken: null,
  user: null,
};

export function useAuthSession() {
  const [authState, setAuthState] = useLocalStorage<AuthSessionState>(
    AUTH_STORAGE_KEY,
    initialAuthState,
  );
  const [activeRole, setActiveRole] = useState<"admin" | "sales">("sales");

  const applyLogin = (response: LoginResponse) => {
    setAuthState({
      accessToken: response.access_token,
      user: response.user,
    });
    setActiveRole(response.user.role === "ADMIN" ? "admin" : "sales");
  };

  const clearSession = () => {
    setAuthState(initialAuthState);
  };

  return {
    accessToken: authState.accessToken,
    user: authState.user,
    activeRole,
    setActiveRole,
    applyLogin,
    clearSession,
    isAuthenticated: Boolean(authState.accessToken && authState.user),
  };
}
