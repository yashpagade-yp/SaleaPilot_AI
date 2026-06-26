import DailyIframe, { DailyCall } from "@daily-co/daily-js";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { generateFeedback, syncConversation } from "../../lib/api/sales";
import { clearActiveSession, loadActiveSession } from "../../lib/storage";

type StudioMode = "voice" | "review";
type CallState = "idle" | "joining" | "joined" | "left" | "error";
type OrbState = "idle" | "listening" | "speaking";

function scenarioLabel(value: string) {
  return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
}

function callStateLabel(state: CallState): string {
  switch (state) {
    case "idle":
      return "Ready";
    case "joining":
      return "Connecting...";
    case "joined":
      return "Live";
    case "left":
      return "Call ended";
    case "error":
      return "Error";
  }
}

function getOrbClass(state: CallState, orb: OrbState): string {
  if (state === "joining") return "is-joining";
  if (state !== "joined") return "is-idle";
  if (orb === "listening") return "is-listening";
  return "is-speaking";
}

export function SessionStudioPage() {
  const { token } = useAuth();
  const [activeSession, setActiveSession] = useState(() => loadActiveSession());
  const [mode, setMode] = useState<StudioMode>("voice");
  const [callState, setCallState] = useState<CallState>("idle");
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const [orbState, setOrbState] = useState<OrbState>("idle");
  const callRef = useRef<DailyCall | null>(null);
  // Track every remote audio element so we can stop and remove them on cleanup
  const audioElementsRef = useRef<HTMLAudioElement[]>([]);
  // Debounce timer — resets orb to "speaking" after salesperson stops talking
  const orbTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function cleanupAudioElements() {
    audioElementsRef.current.forEach((el) => {
      el.pause();
      el.srcObject = null;
    });
    audioElementsRef.current = [];
  }

  // Cleanup on unmount — leave call and destroy the object if still active
  useEffect(() => {
    return () => {
      if (orbTimerRef.current) clearTimeout(orbTimerRef.current);
      cleanupAudioElements();
      if (callRef.current) {
        void callRef.current.leave().catch(() => null);
        callRef.current.destroy();
        callRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleStartCall() {
    if (!activeSession?.session.daily_room || !activeSession?.session.daily_token) {
      setErrorMessage(
        "No Daily room or token found for this session. The backend may not have returned call details.",
      );
      return;
    }

    // If already in a call, do nothing
    if (callRef.current && callState === "joined") {
      return;
    }

    setErrorMessage("");
    setMessage("");
    setCallState("joining");

    try {
      // Create call object if not already created
      if (!callRef.current) {
        callRef.current = DailyIframe.createCallObject({
          // Audio-only — no camera for a voice training experience
          videoSource: false,
          audioSource: true,
        });

        // Wire Daily events to React state
        callRef.current.on("joining-meeting", () => {
          setCallState("joining");
          setMessage("Connecting to your AI practice session...");
        });

        callRef.current.on("joined-meeting", () => {
          setCallState("joined");
          setOrbState("speaking"); // AI typically greets first
          setMessage("You are now live with the AI persona. Start speaking.");
          setMode("voice");
          // Start observing local mic audio level (fires every ~100ms)
          try { callRef.current?.startLocalAudioLevelObserver(100); } catch { /* ignore */ }
        });

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        callRef.current.on("local-audio-level" as any, (event: any) => {
          if ((event as { audioLevel?: number }).audioLevel ?? 0 > 0.015) {
            setOrbState("listening"); // salesperson is speaking — orb listens
            if (orbTimerRef.current) clearTimeout(orbTimerRef.current);
            // After 700 ms of silence assume it's the AI's turn again
            orbTimerRef.current = setTimeout(() => setOrbState("speaking"), 700);
          }
        });

        callRef.current.on("left-meeting", () => {
          setCallState("left");
          setOrbState("idle");
          if (orbTimerRef.current) clearTimeout(orbTimerRef.current);
          setMessage("Call ended. You can sync the transcript and generate feedback now.");
          setMode("review");
          cleanupAudioElements();
          callRef.current?.destroy();
          callRef.current = null;
        });

        callRef.current.on("error", (event) => {
          const detail = (event as { errorMsg?: string }).errorMsg ?? "An unexpected call error occurred.";
          setCallState("error");
          setErrorMessage(`Call error: ${detail}`);
          cleanupAudioElements();
          callRef.current?.destroy();
          callRef.current = null;
        });

        // KEY FIX: createCallObject() is headless — remote audio tracks are NOT
        // automatically rendered. We must manually create an <audio> element for
        // every incoming remote track (the Eigi bot) so the user can hear it.
        callRef.current.on("track-started", (event) => {
          if (!event.participant || event.participant.local) return;
          const track = event.track;
          if (track.kind !== "audio") return;

          const audioEl = new Audio();
          audioEl.autoplay = true;
          audioEl.srcObject = new MediaStream([track]);
          audioEl.play().catch(() => {
            // Autoplay may be blocked; retry on next user gesture
          });
          audioElementsRef.current.push(audioEl);
        });

        // Clean up individual audio elements when a remote track stops
        callRef.current.on("track-stopped", (event) => {
          if (!event.participant || event.participant.local) return;
          const stoppedTrack = event.track;
          audioElementsRef.current = audioElementsRef.current.filter((el) => {
            const stream = el.srcObject as MediaStream | null;
            if (!stream) return false;
            const hasTrack = stream.getTracks().some((t) => t.id === stoppedTrack.id);
            if (hasTrack) {
              el.pause();
              el.srcObject = null;
              return false;
            }
            return true;
          });
        });
      }

      await callRef.current.join({
        url: activeSession.session.daily_room,
        token: activeSession.session.daily_token,
        // Keep camera off — voice training only
        startVideoOff: true,
        startAudioOff: false,
      });
    } catch (error) {
      setCallState("error");
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to join the Daily call room.",
      );
      if (callRef.current) {
        callRef.current.destroy();
        callRef.current = null;
      }
    }
  }

  async function handleEndCall() {
    if (!callRef.current) {
      return;
    }

    try {
      await callRef.current.leave();
      // left-meeting event fires and handles state cleanup
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to leave the call cleanly.",
      );
    }
  }

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

  if (!activeSession) {
    return (
      <main className="session-root">
        <div className="panel empty-state wide">
          No active session is staged right now. Start from{" "}
          <Link to="/workspace/agents">Agents</Link>.
        </div>
      </main>
    );
  }

  const isJoined = callState === "joined";
  const isJoining = callState === "joining";
  const hasRoom =
    Boolean(activeSession.session.daily_room) &&
    Boolean(activeSession.session.daily_token);

  return (
    <main className="session-root">
      <section className="session-stage">
        <div className="session-header">
          <div>
            <span className="eyebrow">AI practice studio</span>
            <h1>{activeSession.scenarioTitle}</h1>
            <p>
              This is the direct SalesPilot conversation surface. No meeting
              room, no exposed call grid — just the active persona and a
              voice-first AI practice flow.
            </p>
          </div>
          <Link className="button button-secondary" to="/workspace/agents">
            Back to agents
          </Link>
        </div>

        {message ? <div className="message success">{message}</div> : null}
        {errorMessage ? (
          <div className="message error">{errorMessage}</div>
        ) : null}

        {!hasRoom ? (
          <div className="message error">
            This session does not have a Daily room attached. The Eigi call
            creation may have failed on the backend. Go back to Agents and
            start a new session.
          </div>
        ) : null}

        <div className="session-grid">
          {/* ── Orb panel ─────────────────────────────────────────── */}
          <article className="panel session-orb-panel refined">
            <div className="session-copy centered">
              <strong>Talk directly with the active persona.</strong>
              <span>
                Speak naturally — the AI will respond in real time.
                Your session is private and voice-only.
              </span>
            </div>

            <div
              className={`voice-orb-shell stage live ${getOrbClass(callState, orbState)}`}
            >
              <div className="voice-orb-ring ring-one" />
              <div className="voice-orb-ring ring-two" />
              <div className="voice-orb" />
              <div className="voice-core detailed">
                <strong>{callStateLabel(callState)}</strong>
                <span>
                  {callState === "joined"
                    ? orbState === "listening" ? "Listening" : "Speaking"
                    : mode === "voice" ? "Voice" : "Review"}
                </span>
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
                className={
                  mode === "review" ? "toggle-pill active" : "toggle-pill"
                }
                onClick={() => setMode("review")}
                type="button"
              >
                Review
              </button>
            </div>

            <div className="session-state-strip">
              <div className="state-chip">
                <span>Persona</span>
                <strong>{activeSession.scenarioTitle}</strong>
              </div>
              <div className="state-chip">
                <span>Call</span>
                <strong>{callStateLabel(callState)}</strong>
              </div>
              <div className="state-chip">
                <span>Focus</span>
                <strong>
                  {mode === "voice" ? "Conversation" : "Review"}
                </strong>
              </div>
            </div>
          </article>

          {/* ── Side action panel ─────────────────────────────────── */}
          <article className="panel session-side-panel refined">
            <div className="detail-stack soft">
              <div className="detail-item">
                <strong>Current scenario</strong>
                <span>{activeSession.scenarioTitle}</span>
              </div>
              <div className="detail-item">
                <strong>Session mode</strong>
                <span>
                  {mode === "voice"
                    ? "Live AI practice"
                    : "Transcript and coaching actions"}
                </span>
              </div>
              <div className="detail-item">
                <strong>Call room</strong>
                <span className="room-status-pill">
                  {hasRoom ? (
                    <><span className="room-status-dot ready" />Room ready</>
                  ) : (
                    <><span className="room-status-dot error" />Not available</>
                  )}
                </span>
              </div>
            </div>

            <div className="action-column">
              {/* ── Primary call control ──────────────────────────── */}
              {!isJoined && callState !== "left" ? (
                <button
                  className="button button-primary button-block"
                  disabled={isJoining || !hasRoom}
                  onClick={() => void handleStartCall()}
                  type="button"
                >
                  {isJoining ? "Connecting..." : "Start conversation"}
                </button>
              ) : null}

              {isJoined ? (
                <button
                  className="button button-primary button-block"
                  onClick={() => void handleEndCall()}
                  type="button"
                >
                  End call
                </button>
              ) : null}

              {callState === "left" ? (
                <button
                  className="button button-secondary button-block"
                  disabled={!hasRoom}
                  onClick={() => {
                    setCallState("idle");
                    setMessage("");
                  }}
                  type="button"
                >
                  Start a new call
                </button>
              ) : null}

              {/* ── Post-session actions ──────────────────────────── */}
              <button
                className="button button-secondary button-block"
                disabled={busyAction === "sync" || isJoined || isJoining}
                onClick={() => void handleSync()}
                type="button"
              >
                {busyAction === "sync" ? "Syncing..." : "Sync transcript"}
              </button>

              <button
                className="button button-secondary button-block"
                disabled={busyAction === "feedback" || isJoined || isJoining}
                onClick={() => void handleFeedback()}
                type="button"
              >
                {busyAction === "feedback"
                  ? "Generating..."
                  : "Generate feedback"}
              </button>

              <button
                className="button button-secondary button-block"
                disabled={isJoined || isJoining}
                onClick={async () => {
                  if (callRef.current) {
                    await callRef.current.leave().catch(() => null);
                    callRef.current.destroy();
                    callRef.current = null;
                  }
                  clearActiveSession();
                  setActiveSession(null);
                  setCallState("idle");
                  setMessage("Session cleared from the studio.");
                }}
                type="button"
              >
                End & clear session
              </button>
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
