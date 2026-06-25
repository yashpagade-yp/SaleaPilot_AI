import {
  PropsWithChildren,
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { LoginResponse, UserProfile, UserRole } from "../types/models";
import {
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
} from "../lib/storage";

interface AuthContextValue {
  token: string | null;
  user: UserProfile | null;
  role: UserRole | null;
  isHydrated: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginResponse) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function normalizeRole(role: string | undefined): UserRole | null {
  if (!role) {
    return null;
  }

  const upper = role.toUpperCase();
  if (upper === "ADMIN" || upper === "SALESPERSON") {
    return upper;
  }

  return null;
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<LoginResponse | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setSession(loadAuthSession());
    setIsHydrated(true);
  }, []);

  const value = useMemo<AuthContextValue>(() => {
    const role = normalizeRole(session?.user.role);

    return {
      token: session?.access_token ?? null,
      user: session?.user ?? null,
      role,
      isHydrated,
      isAuthenticated: Boolean(session?.access_token && role),
      login: (payload) => {
        saveAuthSession(payload);
        setSession(payload);
        setIsHydrated(true);
      },
      logout: () => {
        clearAuthSession();
        setSession(null);
      },
    };
  }, [isHydrated, session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
