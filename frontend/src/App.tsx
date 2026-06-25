import { Navigate, Route, Routes } from "react-router-dom";
import { AcceptInvitationPage } from "./features/auth/AcceptInvitationPage";
import { AuthPage } from "./features/auth/AuthPage";
import { CompleteProfilePage } from "./features/auth/CompleteProfilePage";
import { ProtectedRoute } from "./features/auth/ProtectedRoute";
import { LandingPage } from "./features/landing/LandingPage";
import { AdminWorkspacePage } from "./features/admin/AdminWorkspacePage";
import { SalesWorkspacePage } from "./features/workspace/SalesWorkspacePage";
import { SessionStudioPage } from "./features/session/SessionStudioPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<AuthPage />} />
      <Route path="/accept-invitation" element={<AcceptInvitationPage />} />
      <Route path="/complete-profile" element={<CompleteProfilePage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute role="ADMIN">
            <AdminWorkspacePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspace"
        element={
          <ProtectedRoute role="SALESPERSON">
            <SalesWorkspacePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspace/agents"
        element={
          <ProtectedRoute role="SALESPERSON">
            <SalesWorkspacePage view="agents" />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspace/conversations"
        element={
          <ProtectedRoute role="SALESPERSON">
            <SalesWorkspacePage view="conversations" />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspace/feedback"
        element={
          <ProtectedRoute role="SALESPERSON">
            <SalesWorkspacePage view="feedback" />
          </ProtectedRoute>
        }
      />
      <Route
        path="/workspace/session"
        element={
          <ProtectedRoute role="SALESPERSON">
            <SessionStudioPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
