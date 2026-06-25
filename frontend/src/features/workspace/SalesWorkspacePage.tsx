import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import {
  generateFeedback,
  getFeedback,
  listConversations,
  listScenarios,
  listTrainingSessions,
  startTrainingSession,
  syncConversation,
} from "../../lib/api/sales";
import { saveActiveSession } from "../../lib/storage";
import {
  Conversation,
  Feedback,
  Scenario,
  TrainingSession,
} from "../../types/models";
import { average, capitalize, formatDate } from "../../utils/format";

interface SalesWorkspacePageProps {
  view?: "dashboard" | "agents" | "conversations" | "feedback";
}

export function SalesWorkspacePage({
  view = "dashboard",
}: SalesWorkspacePageProps) {
  const { token, user, logout } = useAuth();
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [trainingSessions, setTrainingSessions] = useState<TrainingSession[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [feedbackMap, setFeedbackMap] = useState<Record<string, Feedback>>({});
  const [selectedConversationId, setSelectedConversationId] = useState<string>("");
  const [selectedFeedbackId, setSelectedFeedbackId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [busyAction, setBusyAction] = useState("");
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function bootstrapWorkspace() {
    if (!token) {
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const [scenarioResponse, sessionsResponse, conversationResponse] = await Promise.all([
        listScenarios(token),
        listTrainingSessions(token),
        listConversations(token),
      ]);

      setScenarios(scenarioResponse.items);
      setTrainingSessions(sessionsResponse);
      setConversations(conversationResponse.items);

      const nextFeedbackMap: Record<string, Feedback> = {};
      await Promise.all(
        sessionsResponse.map(async (session) => {
          try {
            const feedback = await getFeedback(token, session.id);
            nextFeedbackMap[session.id] = feedback;
          } catch {
            // Missing feedback is a valid state for new sessions.
          }
        }),
      );
      setFeedbackMap(nextFeedbackMap);

      if (!selectedConversationId) {
        setSelectedConversationId(conversationResponse.items[0]?.training_session_id || "");
      }
      if (!selectedFeedbackId) {
        setSelectedFeedbackId(Object.keys(nextFeedbackMap)[0] || sessionsResponse[0]?.id || "");
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to load workspace.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void bootstrapWorkspace();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const completedSessions = trainingSessions.filter((session) => session.ended_at).length;
  const lastSessionDate = trainingSessions[0]?.started_at || null;
  const feedbackItems = Object.values(feedbackMap);
  const averageConfidence = average(feedbackItems.map((item) => item.confidence_score));
  const averageClarity = average(feedbackItems.map((item) => item.clarity_score));

  const selectedConversation =
    conversations.find((item) => item.training_session_id === selectedConversationId) || null;
  const selectedFeedback =
    feedbackMap[selectedFeedbackId] ||
    (selectedConversationId ? feedbackMap[selectedConversationId] : undefined) ||
    null;

  async function handleStartSession(scenario: Scenario) {
    if (!token) {
      return;
    }

    setBusyAction(`session-${scenario.id}`);
    setMessage("");
    setErrorMessage("");

    try {
      const response = await startTrainingSession(token, scenario.key);
      saveActiveSession({
        scenarioKey: scenario.key,
        scenarioTitle: scenario.title,
        session: response,
      });
      setMessage(`${scenario.title} is ready. Open the session studio now.`);
      await bootstrapWorkspace();
      navigate("/workspace/session");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to start session.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleSyncConversation(trainingSessionId: string) {
    if (!token) {
      return;
    }

    setBusyAction(`sync-${trainingSessionId}`);
    setMessage("");
    setErrorMessage("");

    try {
      const synced = await syncConversation(token, trainingSessionId);
      setConversations((current) => {
        const existing = current.find((item) => item.id === synced.id);
        if (existing) {
          return current.map((item) => (item.id === synced.id ? synced : item));
        }
        return [synced, ...current];
      });
      setSelectedConversationId(trainingSessionId);
      setMessage("Conversation synced successfully.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to sync conversation.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleGenerateFeedback(trainingSessionId: string) {
    if (!token) {
      return;
    }

    setBusyAction(`feedback-${trainingSessionId}`);
    setMessage("");
    setErrorMessage("");

    try {
      const feedback = await generateFeedback(token, trainingSessionId);
      setFeedbackMap((current) => ({ ...current, [trainingSessionId]: feedback }));
      setSelectedFeedbackId(trainingSessionId);
      setMessage("Feedback generated successfully.");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to generate feedback.");
    } finally {
      setBusyAction("");
    }
  }

  function renderDashboard() {
    return (
      <>
        <section className="stats-grid">
          <article className="metric-card">
            <span>Agents</span>
            <strong>{scenarios.length}</strong>
            <p>Active AI personas available for practice.</p>
          </article>
          <article className="metric-card">
            <span>Conversations</span>
            <strong>{conversations.length}</strong>
            <p>Saved practice calls visible inside your workspace.</p>
          </article>
          <article className="metric-card">
            <span>Completed</span>
            <strong>{completedSessions}</strong>
            <p>Sessions that already reached a closed review state.</p>
          </article>
          <article className="metric-card">
            <span>Last session</span>
            <strong>{lastSessionDate ? "Available" : "Not yet"}</strong>
            <p>{formatDate(lastSessionDate)}</p>
          </article>
        </section>

        <section className="workspace-grid">
          <article className="panel spotlight-panel">
            <div className="voice-orb-shell">
              <div className="voice-orb" />
            </div>
            <span className="eyebrow">Ready to launch</span>
            <h2>Practice inside a product-native AI session studio.</h2>
            <p>
              Start from agents, move through the live voice flow, and return here to sync the
              conversation and open the coaching loop.
            </p>
            <div className="action-row">
              <Link className="button button-primary" to="/workspace/agents">
                Open agents
              </Link>
              <Link className="button button-secondary" to="/workspace/conversations">
                Review calls
              </Link>
            </div>
          </article>

          <article className="panel side-stack">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Pipeline mix</span>
                <h2>Coaching snapshot</h2>
              </div>
            </div>
            <div className="stack-list compact">
              <div className="list-card">
                <strong>Confidence average</strong>
                <span>{averageConfidence ? averageConfidence.toFixed(1) : "No score yet"}</span>
              </div>
              <div className="list-card">
                <strong>Clarity average</strong>
                <span>{averageClarity ? averageClarity.toFixed(1) : "No score yet"}</span>
              </div>
              <div className="list-card">
                <strong>Quick access</strong>
                <span>Agents, conversations, and feedback stay connected.</span>
              </div>
            </div>
          </article>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Recent activity</span>
              <h2>Latest conversations</h2>
            </div>
            <Link className="button button-secondary" to="/workspace/conversations">
              Open all conversations
            </Link>
          </div>
          {conversations.length ? (
            <div className="stack-list">
              {conversations.slice(0, 3).map((conversation) => (
                <div className="list-card" key={conversation.id}>
                  <strong>{conversation.conversation_status.replaceAll("_", " ")}</strong>
                  <span>{conversation.training_session_id}</span>
                  <p>{conversation.transcript?.slice(0, 160) || "Transcript will appear after sync."}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">No conversations yet. Open Agents to start your first session.</div>
          )}
        </section>
      </>
    );
  }

  function renderAgents() {
    return (
      <section className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Agent directory</span>
              <h2>Browse training personas</h2>
            </div>
          </div>
          <div className="stack-list">
            {scenarios.map((scenario) => (
              <div className="list-card" key={scenario.id}>
                <strong>{scenario.title}</strong>
                <span>{capitalize(scenario.key)}</span>
                <p>{scenario.description}</p>
                <button
                  className="button button-primary"
                  disabled={busyAction === `session-${scenario.id}`}
                  onClick={() => void handleStartSession(scenario)}
                  type="button"
                >
                  {busyAction === `session-${scenario.id}` ? "Preparing..." : "Start voice session"}
                </button>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Session direction</span>
              <h2>What happens next</h2>
            </div>
          </div>
          <div className="voice-preview-card">
            <div className="voice-orb-shell compact">
              <div className="voice-orb" />
            </div>
            <p>
              Your live training should feel like a focused AI simulation, not a meeting grid. The
              session studio will give you one voice-centered surface with the active persona and the
              secure room launch point.
            </p>
          </div>
        </article>
      </section>
    );
  }

  function renderConversations() {
    return (
      <section className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Saved voice sessions</span>
              <h2>Conversation history</h2>
            </div>
          </div>
          {conversations.length ? (
            <div className="stack-list">
              {conversations.map((conversation) => (
                <div
                  className={`list-card interactive ${selectedConversationId === conversation.training_session_id ? "selected-card" : ""}`}
                  key={conversation.id}
                  onClick={() => setSelectedConversationId(conversation.training_session_id)}
                >
                  <strong>{conversation.conversation_status.replaceAll("_", " ")}</strong>
                  <span>{formatDate(conversation.fetched_at)}</span>
                  <p>{conversation.transcript?.slice(0, 120) || "Transcript will appear after sync."}</p>
                  <button
                    className="button button-secondary"
                    disabled={busyAction === `sync-${conversation.training_session_id}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      void handleSyncConversation(conversation.training_session_id);
                    }}
                    type="button"
                  >
                    {busyAction === `sync-${conversation.training_session_id}` ? "Syncing..." : "Sync transcript"}
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">No saved conversations found for this salesperson yet.</div>
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Transcript detail</span>
              <h2>Open conversation</h2>
            </div>
          </div>
          {selectedConversation ? (
            <div className="detail-stack">
              <div className="detail-item"><strong>Status</strong><span>{selectedConversation.conversation_status}</span></div>
              <div className="detail-item"><strong>Fetched</strong><span>{formatDate(selectedConversation.fetched_at)}</span></div>
              <div className="transcript-box">{selectedConversation.transcript || "Transcript is not available yet. Run sync after the live practice session ends."}</div>
            </div>
          ) : (
            <div className="empty-state">Choose a conversation to inspect transcript detail.</div>
          )}
        </article>
      </section>
    );
  }

  function renderFeedback() {
    return (
      <section className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Coaching history</span>
              <h2>Feedback records</h2>
            </div>
          </div>
          {trainingSessions.length ? (
            <div className="stack-list">
              {trainingSessions.map((session) => {
                const feedback = feedbackMap[session.id];
                return (
                  <div
                    className={`list-card interactive ${selectedFeedbackId === session.id ? "selected-card" : ""}`}
                    key={session.id}
                    onClick={() => setSelectedFeedbackId(session.id)}
                  >
                    <strong>{capitalize(session.scenario_key)}</strong>
                    <span>{formatDate(session.started_at)}</span>
                    <p>{feedback?.summary || "Feedback is not generated yet for this session."}</p>
                    <button
                      className="button button-secondary"
                      disabled={busyAction === `feedback-${session.id}`}
                      onClick={(event) => {
                        event.stopPropagation();
                        void handleGenerateFeedback(session.id);
                      }}
                      type="button"
                    >
                      {busyAction === `feedback-${session.id}` ? "Generating..." : feedback ? "Refresh feedback" : "Generate feedback"}
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="empty-state">No training sessions exist yet. Start from agents to build feedback history.</div>
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Performance detail</span>
              <h2>Feedback summary</h2>
            </div>
          </div>
          {selectedFeedback ? (
            <div className="feedback-detail">
              <p className="feedback-summary">{selectedFeedback.summary}</p>
              <div className="feedback-score-grid">
                <div><span>Confidence</span><strong>{selectedFeedback.confidence_score.toFixed(1)}</strong></div>
                <div><span>Clarity</span><strong>{selectedFeedback.clarity_score.toFixed(1)}</strong></div>
                <div><span>Rapport</span><strong>{selectedFeedback.rapport_score.toFixed(1)}</strong></div>
                <div><span>Closing</span><strong>{selectedFeedback.closing_score.toFixed(1)}</strong></div>
              </div>
              <div className="detail-columns">
                <div>
                  <strong>Strengths</strong>
                  <ul>
                    {selectedFeedback.strengths.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </div>
                <div>
                  <strong>Improvement areas</strong>
                  <ul>
                    {selectedFeedback.improvement_areas.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </div>
              </div>
              <div>
                <strong>Recommendations</strong>
                <ul>
                  {selectedFeedback.recommendations.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            </div>
          ) : (
            <div className="empty-state">Choose a session to inspect feedback detail.</div>
          )}
        </article>
      </section>
    );
  }

  return (
    <main className="workspace-root">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SP</div>
          <div>
            <strong>SalesPilot AI</strong>
            <span>Sales workspace</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          <Link className={view === "dashboard" ? "sidebar-link active" : "sidebar-link"} to="/workspace">
            Dashboard
          </Link>
          <Link className={view === "agents" ? "sidebar-link active" : "sidebar-link"} to="/workspace/agents">
            Agents
          </Link>
          <Link className={view === "conversations" ? "sidebar-link active" : "sidebar-link"} to="/workspace/conversations">
            Conversations
          </Link>
          <Link className={view === "feedback" ? "sidebar-link active" : "sidebar-link"} to="/workspace/feedback">
            Feedback
          </Link>
        </nav>
        <div className="sidebar-card">
          <span className="eyebrow">Signed in</span>
          <strong>{user?.first_name} {user?.last_name}</strong>
          <span>{user?.email}</span>
        </div>
        <button className="button button-secondary button-block" type="button" onClick={logout}>
          Log out
        </button>
      </aside>

      <section className="workspace-content">
        <header className="workspace-header">
          <div>
            <span className="eyebrow">Sales flow</span>
            <h1>Welcome back, {user?.first_name}</h1>
            <p>Use the workspace to launch AI customer practice, inspect calls, and review coaching feedback.</p>
          </div>
          <button className="button button-secondary" onClick={() => void bootstrapWorkspace()} type="button">
            Refresh workspace
          </button>
        </header>

        {message ? <div className="message success">{message}</div> : null}
        {errorMessage ? <div className="message error">{errorMessage}</div> : null}
        {loading ? <div className="panel empty-state">Loading workspace...</div> : null}
        {!loading && view === "dashboard" ? renderDashboard() : null}
        {!loading && view === "agents" ? renderAgents() : null}
        {!loading && view === "conversations" ? renderConversations() : null}
        {!loading && view === "feedback" ? renderFeedback() : null}
      </section>
    </main>
  );
}
