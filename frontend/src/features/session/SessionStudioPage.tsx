import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { generateFeedback, syncConversation } from "../../lib/api/sales";
import { clearActiveSession, loadActiveSession } from "../../lib/storage";

type StudioMode = "voice" | "review";
type ConversationState = "ready" | "active" | "paused";

function scenarioLabel(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
}

export function SessionStudioPage() {
  const { token } = useAuth();
  const [activeSession, setActiveSession] = useState(() => loadActiveSession());
  const [mode, setMode] = useState<StudioMode>("voice");
  const [conversationState, setConversationState] = useState<ConversationState>("ready");
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [busyAction, setBusyAction] = useState("");

  async function handleSync() {
    if (!token || !activeSession) {
      return;
    }

    setBusyAction("sync");
    setMessage("");
    setErrorMessage("");

    try {
      await syncConversation(token, activeSession.session.session_id);
      setMessage("Transcript synced. You can review it in Conversations.");
      setMode("review");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to sync conversation.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleFeedback() {
    if (!token || !activeSession) {
      return;
    }

    setBusyAction("feedback");
    setMessage("");
    setErrorMessage("");

    try {
      await generateFeedback(token, activeSession.session.session_id);
      setMessage("Feedback generated. Open the Feedback section to review it.");
      setMode("review");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to generate feedback.");
    } finally {
      setBusyAction("");
    }
  }

  function handleStartConversation() {
    setConversationState("active");
    setMode("voice");
    setMessage("Conversation surface is active. Stay inside the studio and continue the practice flow here.");
    setErrorMessage("");
  }

  function handlePauseConversation() {
    setConversationState("paused");
    setMessage("Conversation paused. You can resume when you are ready.");
    setErrorMessage("");
  }

  if (!activeSession) {
    return (
      <main className="session-root">
        <div className="panel empty-state wide">
          No active session is staged right now. Start from <Link to="/workspace/agents">Agents</Link>.
        </div>
      </main>
    );
  }

  const isActive = conversationState === "active";

  return (
    <main className="session-root">
      <section className="session-stage">
        <div className="session-header">
          <div>
            <span className="eyebrow">AI practice studio</span>
            <h1>{activeSession.scenarioTitle}</h1>
            <p>
              This is the direct SalesPilot conversation surface. No meeting room, no exposed call grid, just the active persona and the actions around your practice flow.
            </p>
          </div>
          <Link className="button button-secondary" to="/workspace/agents">
            Back to agents
          </Link>
        </div>

        {message ? <div className="message success">{message}</div> : null}
        {errorMessage ? <div className="message error">{errorMessage}</div> : null}

        <div className="session-grid">
          <article className="panel session-orb-panel refined">
            <div className="session-copy centered">
              <strong>Talk directly with the active persona.</strong>
              <span>
                The orb is now the live face of the session. It should feel like the agent is present inside SalesPilot, not inside a meeting tool.
              </span>
            </div>

            <div className={`voice-orb-shell stage live ${isActive ? "is-speaking" : "is-idle"}`}>
              <div className="voice-orb-ring ring-one" />
              <div className="voice-orb-ring ring-two" />
              <div className="voice-orb" />
              <div className="voice-core detailed">
                <strong>{isActive ? "Listening" : conversationState === "paused" ? "Paused" : "Ready"}</strong>
                <span>{mode === "voice" ? "Voice" : "Review"}</span>
              </div>
            </div>

            <div className="toggle-row">
              <button
                className={mode === "voice" ? "toggle-pill active" : "toggle-pill"}
                onClick={() => setMode("voice")}
                type="button"
              >
                Voice
              </button>
              <button
                className={mode === "review" ? "toggle-pill active" : "toggle-pill"}
                onClick={() => setMode("review")}
                type="button"
              >
                Review
              </button>
            </div>

            <div className="session-state-strip">
              <div className="state-chip">
                <span>Persona</span>
                <strong>{scenarioLabel(activeSession.scenarioKey)}</strong>
              </div>
              <div className="state-chip">
                <span>Status</span>
                <strong>{isActive ? "Live" : conversationState === "paused" ? "Paused" : "Ready"}</strong>
              </div>
              <div className="state-chip">
                <span>Focus</span>
                <strong>{mode === "voice" ? "Conversation" : "Review"}</strong>
              </div>
            </div>
          </article>

          <article className="panel session-side-panel refined">
            <div className="detail-stack soft">
              <div className="detail-item">
                <strong>Current scenario</strong>
                <span>{activeSession.scenarioTitle}</span>
              </div>
              <div className="detail-item">
                <strong>Session mode</strong>
                <span>{mode === "voice" ? "Live AI practice" : "Transcript and coaching actions"}</span>
              </div>
              <div className="detail-item">
                <strong>Experience style</strong>
                <span>Native SalesPilot conversation surface</span>
              </div>
            </div>

            <div className="action-column">
              <button
                className="button button-primary button-block"
                onClick={handleStartConversation}
                type="button"
              >
                {isActive ? "Conversation in progress" : "Start conversation"}
              </button>
              <button
                className="button button-secondary button-block"
                disabled={!isActive}
                onClick={handlePauseConversation}
                type="button"
              >
                Pause conversation
              </button>
              <button
                className="button button-secondary button-block"
                disabled={busyAction === "sync"}
                onClick={() => void handleSync()}
                type="button"
              >
                {busyAction === "sync" ? "Syncing..." : "Sync transcript"}
              </button>
              <button
                className="button button-secondary button-block"
                disabled={busyAction === "feedback"}
                onClick={() => void handleFeedback()}
                type="button"
              >
                {busyAction === "feedback" ? "Generating..." : "Generate feedback"}
              </button>
              <button
                className="button button-secondary button-block"
                onClick={() => {
                  clearActiveSession();
                  setActiveSession(null);
                  setMessage("Session cleared from the studio.");
                  setConversationState("ready");
                }}
                type="button"
              >
                Clear staged session
              </button>
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
