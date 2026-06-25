import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { login as loginRequest, verifyOtp } from "../../lib/api/auth";

export function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const redirectTarget = searchParams.get("redirect");
  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [message, setMessage] = useState("");
  const [devOtpPreview, setDevOtpPreview] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingAction, setLoadingAction] = useState<"login" | "verify" | null>(null);

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setDevOtpPreview("");
    setErrorMessage("");
    setLoadingAction("login");

    try {
      const response = await loginRequest({
        email,
        password,
      });
      setMessage(response.message);
      setDevOtpPreview(response.dev_otp || "");
      setOtpRequested(true);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to sign in.");
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
      const response = await verifyOtp({
        email,
        otp,
      });
      login(response);
      const resolvedRole = response.user.role?.toString().toUpperCase();
      if (resolvedRole === "ADMIN") {
        navigate(redirectTarget || "/admin");
        return;
      }

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
            <p>Use one secure login. Your account role decides whether the admin dashboard or salesperson workspace opens next.</p>
          </div>

          <div className="auth-banner">
            <strong>Email, password, and OTP access</strong>
            <span>
              Enter your email and password first. We will recognize your account role and send a real OTP to the same email.
            </span>
          </div>

          <form className="stack-form" onSubmit={handleLoginSubmit}>
            <label>
              <span>Email address</span>
              <input
                placeholder="Enter your email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label>
              <span>Password</span>
              <input
                placeholder="Enter your password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {message ? <div className="message success">{message}</div> : null}
            {devOtpPreview ? (
              <div className="message success">
                Development OTP preview: <strong>{devOtpPreview}</strong>
              </div>
            ) : null}
            {errorMessage ? <div className="message error">{errorMessage}</div> : null}
            <button
              className="button button-primary button-block"
              disabled={loadingAction === "login"}
              type="submit"
            >
              {loadingAction === "login" ? "Sending OTP..." : "Send OTP"}
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
              disabled={!otpRequested || !email.trim() || !otp.trim() || loadingAction === "verify"}
              type="submit"
            >
              {loadingAction === "verify" ? "Verifying..." : "Continue to workspace"}
            </button>
          </form>

          <Link className="button button-secondary button-block" to="/accept-invitation">
            First time here? Accept invitation
          </Link>
        </div>

        <aside className="auth-side-panel">
          <div className="auth-side-brand">SalesPilot AI</div>
          <h2>One login. Smart routing. Clean entry.</h2>
          <div className="auth-side-board">
            <div className="auth-side-row">
              <strong>Shared sign-in</strong>
              <span>Admins and salespeople use the same login form with email, password, and OTP.</span>
            </div>
            <div className="auth-side-row">
              <strong>Automatic routing</strong>
              <span>The backend reads the user role and opens the correct dashboard after verification.</span>
            </div>
            <div className="auth-side-row">
              <strong>Separate onboarding</strong>
              <span>First-time salespeople still accept the invitation, complete their profile, and create a password before using the shared login.</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
