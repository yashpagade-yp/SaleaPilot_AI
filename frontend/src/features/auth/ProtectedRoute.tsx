import { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { UserRole } from "../../types/models";

interface ProtectedRouteProps extends PropsWithChildren {
  role: UserRole;
}

export function ProtectedRoute({ children, role }: ProtectedRouteProps) {
  const { isAuthenticated, isHydrated, role: currentRole } = useAuth();
  const location = useLocation();

  if (!isHydrated) {
    return <main className="auth-shell"><div className="auth-card">Checking your session...</div></main>;
  }

  if (!isAuthenticated || !currentRole) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  if (currentRole !== role) {
    return <Navigate to={currentRole === "ADMIN" ? "/admin" : "/workspace"} replace />;
  }

  return <>{children}</>;
}
