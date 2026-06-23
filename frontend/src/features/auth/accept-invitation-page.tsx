import { Link, useSearchParams } from "react-router-dom";

import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { NoticeBanner } from "../../components/ui/notice-banner";
import { salesPilotApi } from "../../lib/api/salespilot-api";
import { useEffect, useState } from "react";

export function AcceptInvitationPage() {
  const [searchParams] = useSearchParams();
  const invitationToken = searchParams.get("token") ?? "";
  const [status, setStatus] = useState(
    "Your invitation is ready. The next step is a quick email sign-in so you can begin practice.",
  );

  useEffect(() => {
    if (!invitationToken) {
      return;
    }

    void (async () => {
      try {
        const response = await salesPilotApi.acceptInvitation({ token: invitationToken });
        setStatus(`${response.message} ${response.next_step}`);
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Unable to validate invitation token.");
      }
    })();
  }, [invitationToken]);

  return (
    <div className="page-shell" style={{ padding: "48px 0 72px" }}>
      <Card style={{ maxWidth: 760, margin: "0 auto", display: "grid", gap: 24 }}>
        <div style={{ display: "grid", gap: 10 }}>
          <span className="section-label">Invitation Received</span>
          <h1 style={{ margin: 0 }}>Your invitation is recognized</h1>
          <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
            You’re only a few steps away from practice. Sign in with the invited email address, enter the code sent to your inbox, and step into your training space.
          </p>
        </div>

        <NoticeBanner
          title="Next step"
          description="Head to the salesperson sign-in page, enter your invited email address, and use the sign-in code from your inbox to continue."
          tone="info"
        />

        <div
          style={{
            display: "grid",
            gap: 12,
            padding: 18,
            borderRadius: 18,
            background: "rgba(6, 16, 30, 0.62)",
            border: "1px solid rgba(123, 163, 255, 0.14)",
          }}
        >
          <strong>Invitation token</strong>
          <div
            style={{
              padding: "14px 16px",
              borderRadius: 16,
              background: "rgba(5, 13, 24, 0.9)",
              border: "1px solid rgba(123, 163, 255, 0.12)",
              color: invitationToken ? "#eff4ff" : "#73839d",
              wordBreak: "break-all",
            }}
          >
            {invitationToken || "No token found in the URL."}
          </div>
        </div>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Button to="/workspace">Continue to sign in</Button>
          <Button variant="secondary" to="/admin">
            Back to team setup
          </Button>
        </div>

        <p style={{ margin: 0, color: "#73839d", lineHeight: 1.7 }}>
          {status}
        </p>
      </Card>
    </div>
  );
}
