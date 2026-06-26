import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { login as loginRequest, verifyOtp } from "../../lib/api/auth";

const QUOTES = [
  {
    text: "Practice makes perfect. AI makes practice limitless.",
    cite: "SalesPilot AI",
  },
  {
    text: "Train against every objection before it costs you a real deal.",
    cite: "Sales Wisdom",
  },
  {
    text: "The best closers are made in practice rooms, not boardrooms.",
    cite: "SalesPilot AI",
  },
  {
    text: "Real pressure, real personas, real growth — without real risk.",
    cite: "SalesPilot AI",
  },
  {
    text: "Every session is a rehearsal for the conversation that matters.",
    cite: "Sales Wisdom",
  },
];

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
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingAction, setLoadingAction] = useState<"login" | "verify" | null>(null);
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setQuoteIndex((prev) => (prev + 1) % QUOTES.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setErrorMessage("");
    setLoadingAction("login");

    try {
      const response = await loginRequest({
        email,
        password,
      });
      setMessage(response.message);
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

          <div className={`auth-banner${otpRequested ? " auth-banner-success" : ""}`}>
            {otpRequested ? (
              <>
                <strong>✉️ OTP sent to your inbox</strong>
                <span>Check <strong>{email}</strong> for the 6-digit code and enter it below to continue.</span>
              </>
            ) : (
              <>
                <strong>Email, password, and OTP access</strong>
                <span>Enter your email and password first. We will recognize your account role and send a real OTP to the same email.</span>
              </>
            )}
          </div>

          <form className="stack-form" onSubmit={handleLoginSubmit}>
            <label>
              <span>Email address</span>
              <input
                placeholder="Enter your email"
                readOnly={otpRequested}
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </label>
            <label>
              <span>Password</span>
              <input
                placeholder="Enter your password"
                readOnly={otpRequested}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {!otpRequested && errorMessage ? <div className="message error">{errorMessage}</div> : null}
            <button
              className="button button-primary button-block"
              disabled={loadingAction === "login"}
              type="submit"
            >
              {loadingAction === "login" ? "Sending OTP..." : otpRequested ? "Resend OTP" : "Send OTP"}
            </button>
          </form>

          {otpRequested && (
            <div className="otp-reveal">
              <div className="otp-reveal-hint">
                <span>Enter the code from your email</span>
                <button
                  className="otp-back-link"
                  onClick={() => {
                    setOtpRequested(false);
                    setOtp("");
                    setMessage("");
                    setErrorMessage("");
                  }}
                  type="button"
                >
                  Wrong email?
                </button>
              </div>
              <form className="stack-form" onSubmit={handleVerifyOtp}>
                {errorMessage ? <div className="message error">{errorMessage}</div> : null}
                <label>
                  <span>Email OTP</span>
                  <input
                    autoFocus
                    placeholder="Enter OTP received on email"
                    value={otp}
                    onChange={(event) => setOtp(event.target.value)}
                  />
                </label>
                <button
                  className="button button-secondary button-block"
                  disabled={!email.trim() || !otp.trim() || loadingAction === "verify"}
                  type="submit"
                >
                  {loadingAction === "verify" ? "Verifying..." : "Continue to workspace"}
                </button>
              </form>
            </div>
          )}
        </div>

        <aside className="auth-side-panel">
          <div className="auth-side-brand">SalesPilot AI</div>
          <h2>One login. Smart routing. Clean entry.</h2>

          {/* Rotating quote */}
          <div className="auth-side-quote">
            <blockquote key={quoteIndex}>
              <p>"{QUOTES[quoteIndex].text}"</p>
              <cite>— {QUOTES[quoteIndex].cite}</cite>
            </blockquote>
            <div className="auth-quote-dots">
              {QUOTES.map((_, i) => (
                <span
                  key={i}
                  className={`auth-quote-dot${i === quoteIndex ? " active" : ""}`}
                />
              ))}
            </div>
          </div>

          <div className="auth-side-board">
            <div className="auth-side-row">
              <strong>One secure login</strong>
              <span>Sign in once and get taken straight to your workspace — no extra steps.</span>
            </div>
            <div className="auth-side-row">
              <strong>Your role, your workspace</strong>
              <span>Admins land on the management dashboard. Salespeople go straight to training.</span>
            </div>
            <div className="auth-side-row">
              <strong>AI-powered practice</strong>
              <span>Train against realistic personas — Ideal, Rude, Busy, and Confused — before every real call.</span>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}


