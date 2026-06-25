import { FormEvent, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { adminLogin, requestSalespersonOtp, verifySalespersonOtp } from "../../lib/api/auth";
import { AuthTab } from "../../types/models";

function normalizeTab(searchParams: URLSearchParams): AuthTab {
  return searchParams.get("role") === "salesperson" ? "salesperson" : "admin";
}

export function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const redirectTarget = searchParams.get("redirect");
  const [tab, setTab] = useState<AuthTab>(() => normalizeTab(searchParams));
  const [adminPhone, setAdminPhone] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [inviteToken, setInviteToken] = useState(
    searchParams.get("invitation_token") || searchParams.get("token") || "",
  );
  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(searchParams.get("accepted") === "true");
  const [message, setMessage] = useState("");
  const [devOtpPreview, setDevOtpPreview] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingAction, setLoadingAction] = useState<"admin" | "otp" | "verify" | null>(null);

  function switchTab(nextTab: AuthTab) {
    setTab(nextTab);
    setMessage("");
    setDevOtpPreview("");
    setErrorMessage("");
    setLoadingAction(null);
  }

  const headerText = useMemo(
    () =>
      tab === "admin"
        ? "Direct admin sign-in"
        : "Salesperson invitation and OTP access",
    [tab],
  );

  async function handleAdminSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setErrorMessage("");
    setLoadingAction("admin");

    try {
      const response = await adminLogin({
        phone_number: adminPhone,
        password: adminPassword,
      });
      login(response);
      navigate(redirectTarget || "/admin");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to log in as admin.");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleRequestOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setDevOtpPreview("");
    setErrorMessage("");
    setLoadingAction("otp");

    try {
      const response = await requestSalespersonOtp({
        invitation_token: inviteToken,
        email,
      });
      setMessage(response.message);
      setDevOtpPreview(response.dev_otp || "");
      setOtpRequested(true);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to request OTP.");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleVerifyOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setDevOtpPreview("");
    setErrorMessage("");
    setLoadingAction("verify");

    try {
      const response = await verifySalespersonOtp({ email, otp });
      login(response);
      navigate(redirectTarget || "/workspace");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to verify OTP.");
    } finally {
      setLoadingAction(null);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-stage">
        <div className="auth-card">
          <div className="card-heading">
            <span className="eyebrow">Unified access</span>
            <h1>Enter SalesPilot AI</h1>
            <p>One product entry. Role-based routing after identity and access are confirmed.</p>
          </div>

          <div className="auth-switch">
            <button
              className={tab === "admin" ? "switch-pill active" : "switch-pill"}
              onClick={() => switchTab("admin")}
              type="button"
            >
              Admin
            </button>
            <button
              className={tab === "salesperson" ? "switch-pill active" : "switch-pill"}
              onClick={() => switchTab("salesperson")}
              type="button"
            >
              Salesperson
            </button>
          </div>

          <div className="auth-banner">
            <strong>{headerText}</strong>
            <span>
              {tab === "admin"
                ? "Admins use phone number and password only."
                : "Returning salespeople use invitation code, invited email, and real OTP to sign in."}
            </span>
          </div>

          {tab === "admin" ? (
            <form className="stack-form" onSubmit={handleAdminSubmit}>
              <label>
                <span>Phone number</span>
                <input
                  placeholder="Enter admin phone number"
                  value={adminPhone}
                  onChange={(event) => setAdminPhone(event.target.value)}
                />
              </label>
              <label>
                <span>Password</span>
                <input
                  placeholder="Enter password"
                  type="password"
                  value={adminPassword}
                  onChange={(event) => setAdminPassword(event.target.value)}
                />
              </label>
              {errorMessage ? <div className="message error">{errorMessage}</div> : null}
              <button className="button button-primary button-block" disabled={loadingAction === "admin"} type="submit">
                {loadingAction === "admin" ? "Signing in..." : "Enter admin workspace"}
              </button>
            </form>
          ) : (
            <>
              <form className="stack-form" onSubmit={handleRequestOtp}>
                <label>
                  <span>Invitation code</span>
                  <input
                    placeholder="Paste invitation code"
                    value={inviteToken}
                    onChange={(event) => setInviteToken(event.target.value)}
                  />
                </label>
                <label>
                  <span>Invited email address</span>
                  <input
                    placeholder="Enter invited email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                  />
                </label>
                {message ? <div className="message success">{message}</div> : null}
                {devOtpPreview ? (
                  <div className="message success">
                    Development OTP preview: <strong>{devOtpPreview}</strong>
                  </div>
                ) : null}
                {errorMessage ? <div className="message error">{errorMessage}</div> : null}
                <button className="button button-primary button-block" disabled={loadingAction === "otp"} type="submit">
                  {loadingAction === "otp" ? "Sending OTP..." : "Request OTP"}
                </button>
              </form>

              <form className="stack-form stacked-divider" onSubmit={handleVerifyOtp}>
                <label>
                  <span>Email OTP</span>
                  <input
                    placeholder="Enter OTP received on email"
                    value={otp}
                    onChange={(event) => setOtp(event.target.value)}
                  />
                </label>
                <button
                  className="button button-secondary button-block"
                  disabled={!otpRequested || loadingAction === "verify"}
                  type="submit"
                >
                  {loadingAction === "verify" ? "Verifying..." : "Complete salesperson access"}
                </button>
              </form>
            </>
          )}
        </div>

        <aside className="auth-side-panel">
          <div className="auth-side-brand">SalesPilot AI</div>
          <h2>From invite to AI practice in one clean flow.</h2>
          <div className="auth-side-board">
            <div className="auth-side-row">
              <strong>Admin control</strong>
              <span>Invite once, manage access, review the team workspace.</span>
            </div>
            <div className="auth-side-row">
              <strong>Salesperson path</strong>
              <span>Accept invite, verify by email OTP, and move straight into AI training.</span>
            </div>
            <div className="auth-side-row">
              <strong>Workspace value</strong>
              <span>Agents, conversations, and feedback stay connected around improvement.</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
