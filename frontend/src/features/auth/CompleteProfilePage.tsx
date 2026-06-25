import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { completeSalespersonProfile, requestSalespersonOtp } from "../../lib/api/auth";

function getProfileSeed(searchParams: URLSearchParams) {
  return {
    email:
      searchParams.get("email") ||
      searchParams.get("invited_email") ||
      searchParams.get("mail") ||
      "",
    token:
      searchParams.get("token") ||
      searchParams.get("invitation_token") ||
      searchParams.get("invitation_code") ||
      searchParams.get("code") ||
      "",
  };
}

export function CompleteProfilePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const seed = useMemo(() => getProfileSeed(searchParams), [searchParams]);
  const [email] = useState(seed.email);
  const [invitationToken] = useState(seed.token);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [devOtpPreview, setDevOtpPreview] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [requestingOtp, setRequestingOtp] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!email || !invitationToken || otpRequested || requestingOtp) {
      return;
    }

    void handleRequestOtp();
  }, [email, invitationToken, otpRequested, requestingOtp]);

  async function handleRequestOtp() {
    if (!email || !invitationToken) {
      setErrorMessage("Invitation details are missing. Go back and accept the invitation again.");
      return;
    }

    setErrorMessage("");
    setMessage("");
    setDevOtpPreview("");
    setRequestingOtp(true);

    try {
      const response = await requestSalespersonOtp({
        invitation_token: invitationToken,
        email,
      });
      setMessage(response.message);
      setDevOtpPreview(response.dev_otp || "");
      setOtpRequested(true);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to send OTP.");
    } finally {
      setRequestingOtp(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setMessage("");
    setDevOtpPreview("");
    setIsSubmitting(true);

    try {
      const response = await completeSalespersonProfile({
        invitation_token: invitationToken,
        email,
        first_name: firstName,
        last_name: lastName,
        otp,
        password,
      });
      login(response);
      navigate("/workspace");
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to complete salesperson profile.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-stage">
        <div className="auth-card invitation-card">
          <Link className="back-link" to="/">
            Home
          </Link>
          <div className="card-heading">
            <span className="eyebrow">Invitation accepted</span>
            <h1>Complete profile</h1>
            <p>Enter the OTP sent to your email, add your profile details, and create your password.</p>
          </div>

          <div className="auth-banner">
            <strong>Invitation accepted for {email || "your invited email"}.</strong>
            <span>Finish your profile here before entering the salesperson workspace.</span>
          </div>

          <form className="stack-form" onSubmit={handleSubmit}>
            <button
              className="button button-secondary"
              disabled={requestingOtp || !email || !invitationToken}
              onClick={() => void handleRequestOtp()}
              type="button"
            >
              {requestingOtp ? "Sending OTP..." : "Resend OTP"}
            </button>

            <div className="two-column-grid">
              <label>
                <span>First name</span>
                <input
                  placeholder="Enter first name"
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                />
              </label>
              <label>
                <span>Last name</span>
                <input
                  placeholder="Enter last name"
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                />
              </label>
            </div>

            <label>
              <span>Email address</span>
              <input value={email} readOnly placeholder="Invited email address" />
            </label>

            <label>
              <span>Email OTP</span>
              <input
                placeholder="Enter OTP received on email"
                value={otp}
                onChange={(event) => setOtp(event.target.value)}
              />
            </label>

            <label>
              <span>Password</span>
              <input
                placeholder="Create password"
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
              disabled={isSubmitting || !otpRequested}
              type="submit"
            >
              {isSubmitting ? "Creating account..." : "Create password and continue"}
            </button>

            <Link
              className="button button-secondary button-block"
              to={`/accept-invitation?email=${encodeURIComponent(email)}&invitation_token=${encodeURIComponent(invitationToken)}`}
            >
              Back to invitation step
            </Link>
          </form>
        </div>

        <aside className="auth-side-panel">
          <div className="auth-side-brand">SalesPilot AI</div>
          <h2>Sales reps get a sharper second take.</h2>
          <div className="auth-side-board">
            <div className="auth-side-row">
              <strong>Demo call analysis</strong>
              <span>78% ready</span>
            </div>
            <div className="auth-side-cards">
              <div>
                <span>Clarity</span>
                <strong>82</strong>
              </div>
              <div>
                <span>Pacing</span>
                <strong>71</strong>
              </div>
              <div>
                <span>Close</span>
                <strong>64</strong>
              </div>
            </div>
            <div className="list-card">
              <span>AI note</span>
              <p>Lead with the buyer pain before the feature list. Ask one more discovery question before quoting price.</p>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
