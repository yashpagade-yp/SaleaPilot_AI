import { FormEvent, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { acceptInvitation } from "../../lib/api/auth";

function getInvitationSeed(searchParams: URLSearchParams) {
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

export function AcceptInvitationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const seed = useMemo(() => getInvitationSeed(searchParams), [searchParams]);
  const [email] = useState(seed.email);
  const [token, setToken] = useState(seed.token);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setStatusMessage("");
    setIsSubmitting(true);

    try {
      const response = await acceptInvitation(token);
      setStatusMessage(response.message);

      const nextParams = new URLSearchParams();
      if (response.email || email) {
        nextParams.set("email", response.email || email);
      }
      nextParams.set("invitation_token", token);

      setTimeout(() => {
        navigate(`/complete-profile?${nextParams.toString()}`);
      }, 700);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to verify invitation.");
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
            <span className="eyebrow">Invitation access</span>
            <h1>Accept invitation</h1>
            <p>Validate the invitation code first, then continue into profile creation and OTP verification.</p>
          </div>
          <form className="stack-form" onSubmit={handleSubmit}>
            <label>
              <span>Email ID</span>
              <input value={email} readOnly placeholder="Invited email address" />
            </label>
            <label>
              <span>Invitation code</span>
              <input
                value={token}
                onChange={(event) => setToken(event.target.value)}
                placeholder="Paste the invite code"
              />
            </label>
            {statusMessage ? <div className="message success">{statusMessage}</div> : null}
            {errorMessage ? <div className="message error">{errorMessage}</div> : null}
            <button className="button button-primary button-block" disabled={isSubmitting} type="submit">
              {isSubmitting ? "Validating..." : "Accept invitation"}
            </button>
          </form>
        </div>
        <aside className="auth-side-panel">
          <div className="auth-side-brand">SalesPilot AI</div>
          <h2>Sales reps get a sharper second take.</h2>
          <div className="auth-side-board">
            <div className="auth-side-row">
              <strong>Invite accepted</strong>
              <span>OTP verification and profile setup continue next.</span>
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
            <p>
              The salesperson completes onboarding first, then enters a secure workspace built around AI
              agents, conversations, and post-session feedback.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}
