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
  const [activeConvFilter, setActiveConvFilter] = useState("all");
  const [expandedConvId, setExpandedConvId] = useState<string | null>(null);

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

  function getAgentLabel(agentId: string): string {
    const scenario = scenarios.find((s) => s.agent_id === agentId);
    return scenario ? scenario.title : "Practice session";
  }

  function getStatusClass(status: string): string {
    const s = status.toLowerCase();
    if (s === "completed") return "completed";
    if (s === "failed") return "failed";
    if (s === "in_progress") return "in-progress";
    if (s === "disconnected") return "disconnected";
    return "disconnected";
  }

  function parseTranscriptTurns(text: string): Array<{ role: string; content: string }> {
    const turns: Array<{ role: string; content: string }> = [];
    const regex = /(user|assistant):\s*([\s\S]*?)(?=\s*(?:user|assistant):|$)/gi;
    let match;
    while ((match = regex.exec(text)) !== null) {
      const content = match[2].trim();
      if (content) turns.push({ role: match[1].toLowerCase(), content });
    }
    return turns;
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
            <div className="conv-list" style={{ padding: 0 }}>
              {conversations.slice(0, 3).map((conv) => {
                const statusClass = getStatusClass(conv.conversation_status);
                const statusLabel = conv.conversation_status.replaceAll("_", " ");
                const agentLabel = getAgentLabel(conv.agent_id);
                return (
                  <article className="conv-card" key={conv.id}>
                    <div className="conv-card-header">
                      <div className="conv-avatar">{agentLabel.slice(0, 2).toUpperCase()}</div>
                      <div className="conv-info">
                        <div className="conv-info-primary">
                          <span className="conv-name">{agentLabel}</span>
                        </div>
                        {conv.fetched_at && (
                          <div className="conv-meta-row">
                            <span className="conv-meta-item">
                              <span className="conv-meta-icon">📅</span>
                              {formatDate(conv.fetched_at)}
                            </span>
                          </div>
                        )}
                      </div>
                      <span className={`conv-status-badge ${statusClass}`}>{statusLabel}</span>
                    </div>
                  </article>
                );
              })}
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
              <span className="eyebrow">Session preview</span>
              <h2>What a session feels like</h2>
            </div>
          </div>
          <div className="voice-preview-card">
            <div className="voice-orb-shell compact">
              <div className="voice-orb" />
              <div className="voice-orb-ring" />
              <div className="voice-orb-ring ring-two" />
            </div>
            <p className="voice-preview-hint">Hover the orb to feel the interaction</p>
          </div>

          <div className="preview-chat">
            <div className="preview-bubble agent">
              <span className="preview-label">AI Agent</span>
              Hi! Thanks for reaching out. How can I help you today?
            </div>
            <div className="preview-bubble user">
              <span className="preview-label">You</span>
              I'm looking for a CRM solution for my sales team.
            </div>
            <div className="preview-bubble agent">
              <span className="preview-label">AI Agent</span>
              Great choice! Let me walk you through our top features. What's your team size?
            </div>
            <div className="preview-bubble user">
              <span className="preview-label">You</span>
              We have around 12 reps. What does the pricing look like?
            </div>
            <div className="preview-bubble agent">
              <span className="preview-label">AI Agent</span>
              For a team of 12, our Pro plan would be a perfect fit. Shall I break down the details?
            </div>
          </div>
        </article>
      </section>
    );
  }

  function renderConversations() {
    const convFilters = [
      { key: "all", label: "All", count: conversations.length },
      { key: "COMPLETED", label: "Completed", count: conversations.filter((c) => c.conversation_status === "COMPLETED").length },
      { key: "FAILED", label: "Failed", count: conversations.filter((c) => c.conversation_status === "FAILED").length },
      { key: "DISCONNECTED", label: "Disconnected", count: conversations.filter((c) => c.conversation_status === "DISCONNECTED").length },
      { key: "IN_PROGRESS", label: "In Progress", count: conversations.filter((c) => c.conversation_status === "IN_PROGRESS").length },
    ];

    const filtered =
      activeConvFilter === "all"
        ? conversations
        : conversations.filter((c) => c.conversation_status === activeConvFilter);

    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Saved voice sessions</span>
            <h2>Conversation history</h2>
          </div>
        </div>

        <div className="conv-filter-bar">
          {convFilters.map((f) => (
            <button
              key={f.key}
              className={`conv-filter-tab${activeConvFilter === f.key ? " active" : ""}`}
              onClick={() => setActiveConvFilter(f.key)}
              type="button"
            >
              {f.label}
              <span className="conv-filter-count">{f.count}</span>
            </button>
          ))}
        </div>

        {!filtered.length ? (
          <div className="empty-state">
            {conversations.length
              ? "No conversations match this filter."
              : "No conversations yet. Open Agents to start your first session."}
          </div>
        ) : (
          <div className="conv-list">
            {filtered.map((conv) => {
              const agentLabel = getAgentLabel(conv.agent_id);
              const statusClass = getStatusClass(conv.conversation_status);
              const statusLabel = conv.conversation_status.replaceAll("_", " ");
              const isExpanded = expandedConvId === conv.id;
              const turns = conv.transcript ? parseTranscriptTurns(conv.transcript) : [];
              const isSyncing = busyAction === `sync-${conv.training_session_id}`;

              return (
                <article className="conv-card" key={conv.id}>
                  <div className="conv-card-header">
                    <div className="conv-avatar">{agentLabel.slice(0, 2).toUpperCase()}</div>
                    <div className="conv-info">
                      <div className="conv-info-primary">
                        <span className="conv-name">{agentLabel}</span>
                      </div>
                      <div className="conv-meta-row">
                        {conv.fetched_at && (
                          <span className="conv-meta-item">
                            <span className="conv-meta-icon">📅</span>
                            {formatDate(conv.fetched_at)}
                          </span>
                        )}
                        <span className="conv-meta-item">
                          <span className="conv-meta-icon">🎙️</span>
                          Voice session
                        </span>
                      </div>
                    </div>
                    <span className={`conv-status-badge ${statusClass}`}>{statusLabel}</span>
                  </div>

                  <div className="conv-card-footer">
                    <div className="conv-card-actions">
                      {turns.length > 0 ? (
                        <button
                          className="conv-toggle-btn"
                          onClick={() => setExpandedConvId(isExpanded ? null : conv.id)}
                          type="button"
                        >
                          {isExpanded ? "▲ Hide conversation" : "▼ View conversation"}
                          <span className="conv-filter-count">{turns.length} turns</span>
                        </button>
                      ) : (
                        <span className="conv-no-transcript">Transcript not synced yet</span>
                      )}
                      {!conv.transcript && (
                        <button
                          className="conv-sync-btn"
                          disabled={isSyncing}
                          onClick={() => void handleSyncConversation(conv.training_session_id)}
                          type="button"
                        >
                          {isSyncing ? "Syncing..." : "Sync transcript"}
                        </button>
                      )}
                    </div>
                  </div>

                  {isExpanded && turns.length > 0 && (
                    <div className="conv-transcript-panel">
                      <div className="conv-transcript-turns">
                        {turns.map((turn, i) => (
                          <div className={`conv-turn ${turn.role}`} key={i}>
                            <div className={`conv-turn-avatar ${turn.role}`}>
                              {turn.role === "user" ? "SP" : "AI"}
                            </div>
                            <div className={`conv-turn-bubble ${turn.role}`}>
                              <div className={`conv-turn-label ${turn.role}`}>
                                {turn.role === "user" ? "You" : agentLabel}
                              </div>
                              {turn.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
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
