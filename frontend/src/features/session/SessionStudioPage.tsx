import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { generateFeedback, syncConversation } from "../../lib/api/sales";
import { clearActiveSession, loadActiveSession } from "../../lib/storage";

function buildDailyLaunchUrl(
  dailyRoom: string | null,
  dailyToken: string | null,
): string | null {
  if (!dailyRoom) {
    return null;
  }

  if (!dailyToken) {
    return dailyRoom;
  }

  const separator = dailyRoom.includes("?") ? "&" : "?";
  return `${dailyRoom}${separator}t=${encodeURIComponent(dailyToken)}`;
}

export function SessionStudioPage() {
  const { token } = useAuth();
  const [activeSession, setActiveSession] = useState(() => loadActiveSession());
  const [showEmbeddedRoom, setShowEmbeddedRoom] = useState(false);
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const launchUrl = activeSession
    ? buildDailyLaunchUrl(
        activeSession.session.daily_room,
        activeSession.session.daily_token,
      )
    : null;

  async function handleSync() {
    if (!token || !activeSession) {
      return;
    }

    setBusyAction("sync");
    setMessage("");
    setErrorMessage("");

    try {
      await syncConversation(token, activeSession.session.session_id);
      setMessage("Conversation sync completed. You can review it in Conversations.");
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
      setMessage("Feedback generated. Review it in the Feedback section.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to generate feedback.");
    } finally {
      setBusyAction("");
    }
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

  return (
    <main className="session-root">
      <section className="session-stage">
        <div className="session-header">
          <div>
            <span className="eyebrow">Voice practice studio</span>
            <h1>{activeSession.scenarioTitle}</h1>
            <p>
              This session surface is intentionally product-native and voice-first. It should feel
              like a rehearsal tool, not a meeting grid.
            </p>
          </div>
          <Link className="button button-secondary" to="/workspace/agents">
            Back to agents
          </Link>
        </div>

        {message ? <div className="message success">{message}</div> : null}
        {errorMessage ? <div className="message error">{errorMessage}</div> : null}

        <div className="session-grid">
          <article className="panel session-orb-panel">
            <div className="session-copy">
              <strong>Meet the active persona where the conversation starts.</strong>
              <span>
                The voice room stays behind a secure launch step, while the surrounding interface
                keeps the user inside the SalesPilot AI product experience.
              </span>
            </div>
            <div className="voice-orb-shell stage">
              <div className="voice-orb" />
              <div className="voice-core">Voice</div>
            </div>
            <div className="toggle-row">
              <span className="toggle-pill active">Voice</span>
              <span className="toggle-pill">Review</span>
            </div>
          </article>

          <article className="panel session-side-panel">
            <div className="detail-stack">
              <div className="detail-item"><strong>Scenario key</strong><span>{activeSession.scenarioKey}</span></div>
              <div className="detail-item"><strong>Training session</strong><span>{activeSession.session.session_id}</span></div>
              <div className="detail-item"><strong>Conversation id</strong><span>{activeSession.session.conversation_id || "Will appear after launch"}</span></div>
            </div>
            <div className="action-column">
              {launchUrl ? (
                <>
                  <button
                    className="button button-primary button-block"
                    onClick={() => setShowEmbeddedRoom((current) => !current)}
                    type="button"
                  >
                    {showEmbeddedRoom ? "Hide embedded room" : "Launch inside workspace"}
                  </button>
                  <a
                    className="button button-secondary button-block"
                    href={launchUrl}
                    rel="noreferrer"
                    target="_blank"
                  >
                    Open secure room in new tab
                  </a>
                </>
              ) : (
                <div className="empty-state">
                  Daily room URL is not available yet for this session payload.
                </div>
              )}
              <button className="button button-secondary button-block" disabled={busyAction === "sync"} onClick={() => void handleSync()} type="button">
                {busyAction === "sync" ? "Syncing..." : "Sync transcript"}
              </button>
              <button className="button button-secondary button-block" disabled={busyAction === "feedback"} onClick={() => void handleFeedback()} type="button">
                {busyAction === "feedback" ? "Generating..." : "Generate feedback"}
              </button>
              <button
                className="button button-secondary button-block"
                onClick={() => {
                  clearActiveSession();
                  setActiveSession(null);
                  setShowEmbeddedRoom(false);
                  setMessage("Staged session cleared.");
                }}
                type="button"
              >
                Clear staged session
              </button>
            </div>
          </article>
        </div>

        {showEmbeddedRoom && launchUrl ? (
          <section className="panel embedded-room-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Live room</span>
                <h2>Stay inside the SalesPilot AI shell</h2>
              </div>
            </div>
            <div className="room-frame-shell">
              <iframe
                allow="autoplay; camera; microphone; fullscreen; speaker-selection"
                src={launchUrl}
                title="SalesPilot AI voice room"
              />
            </div>
          </section>
        ) : null}
      </section>
    </main>
  );
}
