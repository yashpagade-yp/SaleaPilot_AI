import { NavLink, Outlet } from "react-router-dom";

interface AppShellLayoutProps {
  mode: "admin" | "sales";
}

const linksByMode = {
  admin: [
    { to: "/", label: "Landing" },
    { to: "/admin", label: "Admin Hub" },
  ],
  sales: [
    { to: "/", label: "Landing" },
    { to: "/workspace", label: "Workspace" },
    { to: "/admin", label: "Admin" },
  ],
};

export function AppShellLayout({ mode }: AppShellLayoutProps) {
  return (
    <div style={{ minHeight: "100vh", padding: "20px 0 40px" }}>
      <div className="page-shell app-shell-grid">
        <aside
          className="panel grid-glow"
          style={{
            padding: 24,
            position: "sticky",
            top: 20,
            height: "fit-content",
          }}
        >
          <div style={{ display: "grid", gap: 10, marginBottom: 28 }}>
            <span className="section-label">
              {mode === "admin" ? "Admin Flow" : "Sales Flow"}
            </span>
            <h1 style={{ margin: 0, fontSize: "1.5rem" }}>SalesPilot AI</h1>
            <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.6 }}>
              Sharper sales conversations through realistic practice, guided access, and performance review.
            </p>
          </div>
          <nav style={{ display: "grid", gap: 10 }}>
            {linksByMode[mode].map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                style={({ isActive }) => ({
                  display: "block",
                  padding: "14px 16px",
                  borderRadius: 16,
                  border: isActive
                    ? "1px solid rgba(104, 213, 255, 0.28)"
                    : "1px solid transparent",
                  background: isActive
                    ? "rgba(104, 213, 255, 0.08)"
                    : "transparent",
                  color: isActive ? "#eff4ff" : "#9eb0cf",
                  fontWeight: 600,
                })}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <main>
          <div
            className="panel"
            style={{
              marginBottom: 20,
              padding: "16px 20px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 16,
              flexWrap: "wrap",
            }}
          >
            <div style={{ display: "grid", gap: 6 }}>
              <strong>{mode === "admin" ? "Team setup" : "Sales practice hub"}</strong>
              <span style={{ color: "#9eb0cf" }}>
                {mode === "admin"
                  ? "Invite your team and open the door to better practice calls."
                  : "Practice real conversations, review what happened, and improve faster."}
              </span>
            </div>
            <span className="section-label">
              {mode === "admin" ? "Team access" : "Practice + coaching"}
            </span>
          </div>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
