import { useState, type FormEvent } from "react";

import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { EmptyState } from "../../components/ui/empty-state";
import { Input } from "../../components/ui/input";
import { MetricCard } from "../../components/ui/metric-card";
import { NoticeBanner } from "../../components/ui/notice-banner";
import { StatusPill } from "../../components/ui/status-pill";
import { useAuthSession } from "../../hooks/use-auth-session";
import { salesPilotApi } from "../../lib/api/salespilot-api";

export function AdminWorkspacePage() {
  const auth = useAuthSession();
  const [adminLogin, setAdminLogin] = useState({ phone_number: "", password: "" });
  const [inviteState, setInviteState] = useState({
    email: "",
    first_name: "",
    last_name: "",
  });
  const [loading, setLoading] = useState<string | null>(null);
  const [feedback, setFeedback] = useState(
    "Sign in, invite your team, and get new reps ready for stronger practice calls.",
  );
  const adminUiUnlocked = auth.user?.role === "ADMIN" && Boolean(auth.accessToken);

  const handleAdminLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading("login");

    try {
      const response = await salesPilotApi.adminLogin(adminLogin);
      auth.applyLogin(response);
      setFeedback(
        `Welcome ${response.user.first_name}. You're ready to invite salespeople into practice.`,
      );
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Admin login failed.");
    } finally {
      setLoading(null);
    }
  };

  const handleInvite = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!auth.accessToken) {
      setFeedback("Admin login is required before sending an invitation.");
      return;
    }

    setLoading("invite");
    try {
      const response = await salesPilotApi.sendInvitation(inviteState, auth.accessToken);
      setFeedback(
        `Invitation created for ${response.email}. Status: ${response.status}. Expires at ${new Date(
          response.expires_at,
        ).toLocaleString()}.`,
      );
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Invitation failed.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <Card style={{ display: "grid", gap: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap" }}>
          <div style={{ display: "grid", gap: 8 }}>
            <span className="section-label">Admin Flow</span>
            <h1 style={{ margin: 0 }}>Admin logs in directly, then invites the salesperson</h1>
            <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
              Keep team setup simple. Sign in, invite the right salesperson, and help them begin practice without extra friction.
            </p>
          </div>
          <StatusPill
            label={adminUiUnlocked ? "Ready to invite" : "Sign in to continue"}
            tone={adminUiUnlocked ? "success" : "warning"}
          />
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 14,
          }}
        >
          <MetricCard
            label="Sign-in style"
            value="Simple"
            helper="A quick phone-and-password sign-in keeps setup fast for admins."
          />
          <MetricCard
            label="Invite method"
            value="Email"
            helper="Each invite goes to the salesperson’s real email address."
          />
          <MetricCard
            label="Team flow"
            value="Ready"
            helper="Sign in, invite, and help the team reach practice faster."
          />
        </div>
      </Card>

      <NoticeBanner
        title="Set your team up for success"
        description="Use this page to open access for each salesperson, so they can move straight into guided practice and live call rehearsal."
        tone="info"
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 20,
        }}
      >
        <Card style={{ display: "grid", gap: 18 }}>
          <strong>1. Direct admin login</strong>
          <form
            onSubmit={handleAdminLogin}
            autoComplete="off"
            style={{ display: "grid", gap: 16 }}
          >
            <Input
              label="Phone number"
              name="admin_phone_number"
              autoComplete="off"
              value={adminLogin.phone_number}
              onChange={(event) =>
                setAdminLogin((current) => ({ ...current, phone_number: event.target.value }))
              }
              placeholder="Enter admin phone number"
              required
            />
            <Input
              label="Password"
              name="admin_password"
              type="password"
              autoComplete="off"
              value={adminLogin.password}
              onChange={(event) =>
                setAdminLogin((current) => ({ ...current, password: event.target.value }))
              }
              placeholder="Enter admin password"
              required
            />
            <Button type="submit" disabled={loading === "login"}>
              {loading === "login" ? "Signing in..." : "Log in as admin"}
            </Button>
          </form>
        </Card>

        <Card style={{ display: "grid", gap: 18 }}>
          <strong>2. What happens next</strong>
          <NoticeBanner
            title="Invite once, practice anytime"
            description="Once a salesperson is invited, they can enter through their email and move into a guided sign-in experience built for quick access."
            tone={adminUiUnlocked ? "success" : "info"}
          />
          <div
            style={{
              padding: 18,
              borderRadius: 18,
              background: "rgba(6, 16, 30, 0.62)",
              border: "1px solid rgba(123, 163, 255, 0.14)",
              display: "grid",
              gap: 10,
            }}
          >
            <strong>Why this matters</strong>
            <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
              Invitations keep access controlled without making the process feel heavy. The result is a smoother path from invite to first practice call.
            </p>
          </div>
        </Card>
      </div>

      <Card style={{ display: "grid", gap: 18 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
          <strong>3. Send salesperson invitation</strong>
          {adminUiUnlocked ? (
            <StatusPill label="Invite ready" tone="success" />
          ) : (
            <StatusPill label="Sign in first" tone="warning" />
          )}
        </div>

        {adminUiUnlocked ? (
          <form
            onSubmit={handleInvite}
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 16,
              alignItems: "end",
            }}
          >
            <Input
              label="First name"
              name="salesperson_first_name"
              autoComplete="given-name"
              value={inviteState.first_name}
              onChange={(event) =>
                setInviteState((current) => ({ ...current, first_name: event.target.value }))
              }
              required
            />
            <Input
              label="Last name"
              name="salesperson_last_name"
              autoComplete="family-name"
              value={inviteState.last_name}
              onChange={(event) =>
                setInviteState((current) => ({ ...current, last_name: event.target.value }))
              }
              required
            />
            <Input
              label="Salesperson email"
              name="salesperson_email"
              type="email"
              autoComplete="email"
              value={inviteState.email}
              onChange={(event) =>
                setInviteState((current) => ({ ...current, email: event.target.value }))
              }
              placeholder="Enter the real salesperson email"
              required
            />
            <Button type="submit" disabled={loading === "invite"} style={{ minWidth: 180 }}>
              {loading === "invite" ? "Sending..." : "Send invitation"}
            </Button>
            <Button type="button" variant="ghost" onClick={auth.clearSession}>
              Sign out admin
            </Button>
          </form>
        ) : (
          <EmptyState
            title="Sign in to invite a salesperson"
            description="Once you’re signed in, this area becomes your quick path to bringing another rep into practice."
          />
        )}
      </Card>

      <Card style={{ display: "grid", gap: 12 }}>
        <strong>Activity update</strong>
        <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>{feedback}</p>
      </Card>
    </div>
  );
}
