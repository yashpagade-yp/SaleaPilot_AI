import { FormEvent, useEffect, useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  deleteSalesperson,
  listAdminAgents,
  listSalespeople,
  listSalespersonConversations,
  sendInvitation,
  updateSalespersonStatus,
} from "../../lib/api/admin";
import {
  AdminSalesperson,
  Conversation,
  Scenario,
} from "../../types/models";
import { capitalize, formatDate } from "../../utils/format";

type AdminSectionId = "dashboard" | "management" | "agents" | "conversations";

interface AdminConversationItem {
  id: string;
  salespersonId: string;
  salespersonName: string;
  salespersonEmail: string;
  agentLabel: string;
  conversationStatus: string;
  transcript: string | null;
  fetchedAt: string | null;
  trainingSessionId: string;
}

const adminSections: Array<{
  id: AdminSectionId;
  label: string;
  group: "platform" | "workspace";
}> = [
  { id: "dashboard", label: "Dashboard", group: "platform" },
  { id: "management", label: "Admin Management", group: "platform" },
  { id: "agents", label: "Agents", group: "workspace" },
  { id: "conversations", label: "Conversations", group: "workspace" },
];

export function AdminWorkspacePage() {
  const { token, user, logout } = useAuth();
  const [activeSection, setActiveSection] = useState<AdminSectionId>("dashboard");
  const [agents, setAgents] = useState<Scenario[]>([]);
  const [salespeople, setSalespeople] = useState<AdminSalesperson[]>([]);
  const [allConversations, setAllConversations] = useState<AdminConversationItem[]>([]);
  const [selectedSalespersonId, setSelectedSalespersonId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [busyAction, setBusyAction] = useState<string>("");
  const [message, setMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [activeConvFilter, setActiveConvFilter] = useState("all");
  const [expandedConvId, setExpandedConvId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; name: string } | null>(null);

  const selectedSalesperson = useMemo(
    () => salespeople.find((salesperson) => salesperson.id === selectedSalespersonId) || null,
    [salespeople, selectedSalespersonId],
  );

  const invitedCount = salespeople.filter((item) => item.status === "INVITED").length;
  const activeCount = salespeople.filter((item) => item.is_active).length;

  async function fetchAllConversations(
    activeToken: string,
    currentSalespeople: AdminSalesperson[],
    currentAgents: Scenario[],
  ) {
    if (!currentSalespeople.length) {
      setAllConversations([]);
      return;
    }

    setLoadingConversations(true);
    try {
      const results = await Promise.allSettled(
        currentSalespeople.map(async (salesperson) => {
          const response = await listSalespersonConversations(activeToken, salesperson.id, 1, 50);
          return response.items.map((conversation): AdminConversationItem => {
            const matchedAgent =
              currentAgents.find((agent) => agent.agent_id === conversation.agent_id) || null;
              return {
              id: conversation.id,
              salespersonId: salesperson.id,
              salespersonName: `${salesperson.first_name} ${salesperson.last_name}`,
              salespersonEmail: salesperson.email,
              agentLabel: matchedAgent ? matchedAgent.title : conversation.agent_id,
              conversationStatus: conversation.conversation_status,
              transcript: conversation.transcript || null,
              fetchedAt: conversation.fetched_at,
              trainingSessionId: conversation.training_session_id,
            };
          });
        }),
      );

      const nextItems = results
        .filter(
          (result): result is PromiseFulfilledResult<AdminConversationItem[]> =>
            result.status === "fulfilled",
        )
        .flatMap((result) => result.value)
        .sort((left, right) => {
          const leftTime = left.fetchedAt ? new Date(left.fetchedAt).getTime() : 0;
          const rightTime = right.fetchedAt ? new Date(right.fetchedAt).getTime() : 0;
          return rightTime - leftTime;
        });

      setAllConversations(nextItems);

      if (results.some((result) => result.status === "rejected")) {
        setErrorMessage(
          "Some salesperson conversations could not be loaded, but the conversation workspace is still available.",
        );
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to load conversation workspace.",
      );
    } finally {
      setLoadingConversations(false);
    }
  }

  async function refreshDashboard() {
    if (!token) {
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
      const [agentsResult, salespeopleResult] = await Promise.allSettled([
        listAdminAgents(token),
        listSalespeople(token),
      ]);

      const nextAgents =
        agentsResult.status === "fulfilled" ? agentsResult.value.items : [];
      const nextSalespeople =
        salespeopleResult.status === "fulfilled" ? salespeopleResult.value.items : [];

      setAgents(nextAgents);
      setSalespeople(nextSalespeople);

      if (agentsResult.status === "rejected" && salespeopleResult.status === "rejected") {
        throw new Error("We couldn't load the admin workspace right now.");
      }

      if (salespeopleResult.status === "rejected") {
        setErrorMessage(
          "Salespeople data is unavailable right now. You can still use the rest of the admin workspace.",
        );
      } else if (agentsResult.status === "rejected") {
        setErrorMessage(
          "Training personas are unavailable right now. User management is still available.",
        );
      }

      setSelectedSalespersonId((current) => current || nextSalespeople[0]?.id || "");

      if (activeSection === "conversations" && salespeopleResult.status === "fulfilled") {
        await fetchAllConversations(token, nextSalespeople, nextAgents);
      } else if (activeSection !== "conversations") {
        setAllConversations([]);
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to load admin workspace.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (!token || activeSection !== "conversations") {
      return;
    }

    void fetchAllConversations(token, salespeople, agents);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSection]);

  async function handleInviteSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setBusyAction("invite");
    setMessage("");
    setErrorMessage("");

    try {
      const response = await sendInvitation(token, { email: inviteEmail });
      setMessage(`Invitation sent to ${response.email}.`);
      setInviteEmail("");
      await refreshDashboard();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to send invitation.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleStatusChange(salespersonId: string, isActive: boolean) {
    if (!token) {
      return;
    }

    setBusyAction(`status-${salespersonId}`);
    setMessage("");
    setErrorMessage("");

    try {
      const updated = await updateSalespersonStatus(token, salespersonId, isActive);
      setSalespeople((current) =>
        current.map((item) => (item.id === salespersonId ? updated : item)),
      );
      setMessage(
        `${updated.first_name} ${updated.last_name} is now ${updated.is_active ? "active" : "inactive"}.`,
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to update user status.");
    } finally {
      setBusyAction("");
    }
  }

  async function handleDelete(salespersonId: string) {
    if (!token) {
      return;
    }

    setBusyAction(`delete-${salespersonId}`);
    setMessage("");
    setErrorMessage("");

    try {
      const response = await deleteSalesperson(token, salespersonId);
      setMessage(response.message);
      setSalespeople((current) => current.filter((item) => item.id !== salespersonId));
      setAllConversations((current) =>
        current.filter((item) => item.salespersonId !== salespersonId),
      );
      if (selectedSalespersonId === salespersonId) {
        setSelectedSalespersonId("");
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Unable to delete salesperson.");
    } finally {
      setBusyAction("");
    }
  }

  function renderInvitePanel() {
    return (
      <article className="panel compact-panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Invite salesperson</span>
            <h2>Send invitation email</h2>
          </div>
        </div>
        <form className="stack-form" onSubmit={handleInviteSubmit}>
          <label>
            <span>Email address</span>
            <input
              value={inviteEmail}
              onChange={(event) => setInviteEmail(event.target.value)}
              placeholder="Enter salesperson email"
              type="email"
            />
          </label>
          <button
            className="button button-primary button-block"
            disabled={busyAction === "invite"}
            type="submit"
          >
            {busyAction === "invite" ? "Sending..." : "Send invitation"}
          </button>
        </form>
      </article>
    );
  }

  function renderDashboardSection() {
    return (
      <>
        <section className="stats-grid">
          <article className="metric-card">
            <span>Total salespeople</span>
            <strong>{salespeople.length}</strong>
          </article>
          <article className="metric-card">
            <span>Active now</span>
            <strong>{activeCount}</strong>
          </article>
          <article className="metric-card">
            <span>Invited</span>
            <strong>{invitedCount}</strong>
          </article>
          <article className="metric-card">
            <span>Inactive</span>
            <strong>{Math.max(salespeople.length - activeCount - invitedCount, 0)}</strong>
          </article>
        </section>

        <section className="admin-management-grid">
          {renderInvitePanel()}

          <article className="panel quick-stats-panel">
            <div className="panel-header" style={{ marginBottom: "12px" }}>
              <div>
                <span className="eyebrow">Quick stats</span>
                <h2 style={{ fontSize: "1.35rem", margin: "6px 0 0" }}>Workspace at a glance</h2>
              </div>
            </div>
            <div className="quick-stats-grid">
              <div className="quick-stat-item">
                <span className="quick-stat-icon">📨</span>
                <div>
                  <strong>Last invite sent</strong>
                  <span>
                    {salespeople
                      .filter((sp) => sp.latest_invitation_sent_at)
                      .sort((a, b) => new Date(b.latest_invitation_sent_at!).getTime() - new Date(a.latest_invitation_sent_at!).getTime())[0]
                      ?.latest_invitation_sent_at
                      ? formatDate(
                          salespeople
                            .filter((sp) => sp.latest_invitation_sent_at)
                            .sort((a, b) => new Date(b.latest_invitation_sent_at!).getTime() - new Date(a.latest_invitation_sent_at!).getTime())[0]
                            .latest_invitation_sent_at
                        )
                      : "None yet"}
                  </span>
                </div>
              </div>
              <div className="quick-stat-item">
                <span className="quick-stat-icon">⏳</span>
                <div>
                  <strong>Pending invitations</strong>
                  <span>{invitedCount} waiting to join</span>
                </div>
              </div>
              <div className="quick-stat-item">
                <span className="quick-stat-icon">🤖</span>
                <div>
                  <strong>Active agents</strong>
                  <span>{agents.filter((a) => a.is_active).length} of {agents.length} online</span>
                </div>
              </div>
              <div className="quick-stat-item">
                <span className="quick-stat-icon">✅</span>
                <div>
                  <strong>Active salespeople</strong>
                  <span>{activeCount} of {salespeople.length} active</span>
                </div>
              </div>
            </div>
          </article>

        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Sales team</span>
              <h2>Manage salespeople</h2>
            </div>
          </div>
          {loading ? (
            <div className="empty-state">Loading admin data...</div>
          ) : !salespeople.length ? (
            <div className="empty-state">
              No salespeople are available right now. Send an invitation to begin the access flow.
            </div>
          ) : (
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Status</th>
                    <th>Last login</th>
                    <th>Invitation</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {salespeople.map((salesperson) => (
                    <tr
                      className={selectedSalespersonId === salesperson.id ? "selected-row" : ""}
                      key={salesperson.id}
                      onClick={() => setSelectedSalespersonId(salesperson.id)}
                    >
                      <td>
                        <strong>{salesperson.first_name} {salesperson.last_name}</strong>
                        <span>{salesperson.email}</span>
                      </td>
                      <td>
                        <span className={`status-pill ${salesperson.is_active ? "active" : "inactive"}`}>
                          {salesperson.status}
                        </span>
                      </td>
                      <td>{formatDate(salesperson.last_login_at)}</td>
                      <td>{salesperson.latest_invitation_status || "None"}</td>
                      <td>
                        <div className="table-actions">
                          <button
                            className="table-button"
                            disabled={busyAction === `status-${salesperson.id}`}
                            onClick={(event) => {
                              event.stopPropagation();
                              void handleStatusChange(salesperson.id, !salesperson.is_active);
                            }}
                            type="button"
                          >
                            {salesperson.is_active ? "Make inactive" : "Make active"}
                          </button>
                          <button
                            className="table-button danger"
                            disabled={busyAction === `delete-${salesperson.id}`}
                            onClick={(event) => {
                              event.stopPropagation();
                              setDeleteConfirm({
                                id: salesperson.id,
                                name: `${salesperson.first_name} ${salesperson.last_name}`,
                              });
                            }}
                            type="button"
                          >
                            Delete user
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </>
    );
  }

  function renderManagementSection() {
    return (
      <section className="admin-management-grid">
        {renderInvitePanel()}

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Selected user</span>
              <h2>
                {selectedSalesperson
                  ? `${selectedSalesperson.first_name} ${selectedSalesperson.last_name}`
                  : "Choose a salesperson"}
              </h2>
            </div>
          </div>
          {selectedSalesperson ? (
            <div className="detail-stack">
              <div className="detail-item"><strong>Email</strong><span>{selectedSalesperson.email}</span></div>
              <div className="detail-item"><strong>Status</strong><span>{selectedSalesperson.status}</span></div>
              <div className="detail-item"><strong>Last login</strong><span>{formatDate(selectedSalesperson.last_login_at)}</span></div>
              <div className="detail-item"><strong>Updated</strong><span>{formatDate(selectedSalesperson.updated_at)}</span></div>
              <div className="detail-item"><strong>Invitation</strong><span>{selectedSalesperson.latest_invitation_status || "None"}</span></div>
            </div>
          ) : (
            <div className="empty-state">Select a salesperson from the Dashboard section to manage account details here.</div>
          )}
        </article>
      </section>
    );
  }

  function renderAgentsSection() {
    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Agents</span>
            <h2>Current agent set</h2>
          </div>
        </div>
        <div className="stack-list">
          {agents.length ? (
            agents.map((agent) => (
              <div className="list-card" key={agent.id}>
                <strong>{agent.title}</strong>
                <span>{capitalize(agent.key)}</span>
                <p>{agent.description}</p>
              </div>
            ))
          ) : (
            <div className="empty-state">No training personas are available right now.</div>
          )}
        </div>
      </section>
    );
  }

  function getInitials(name: string): string {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return (parts[0]?.slice(0, 2) ?? "SP").toUpperCase();
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

  function renderConversationsSection() {
    const convFilters = [
      { key: "all", label: "All", count: allConversations.length },
      { key: "COMPLETED", label: "Completed", count: allConversations.filter((c) => c.conversationStatus === "COMPLETED").length },
      { key: "FAILED", label: "Failed", count: allConversations.filter((c) => c.conversationStatus === "FAILED").length },
      { key: "DISCONNECTED", label: "Disconnected", count: allConversations.filter((c) => c.conversationStatus === "DISCONNECTED").length },
      { key: "IN_PROGRESS", label: "In Progress", count: allConversations.filter((c) => c.conversationStatus === "IN_PROGRESS").length },
    ];

    const filtered =
      activeConvFilter === "all"
        ? allConversations
        : allConversations.filter((c) => c.conversationStatus === activeConvFilter);

    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Conversations</span>
            <h2>Salesperson and agent history</h2>
          </div>
        </div>

        {/* Filter tabs */}
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

        {loadingConversations ? (
          <div className="empty-state">Loading conversations...</div>
        ) : !filtered.length ? (
          <div className="empty-state">No conversations match this filter.</div>
        ) : (
          <div className="conv-list">
            {filtered.map((conv) => {
              const initials = getInitials(conv.salespersonName);
              const statusClass = getStatusClass(conv.conversationStatus);
              const statusLabel = conv.conversationStatus.replaceAll("_", " ");
              const isExpanded = expandedConvId === conv.id;
              const turns = conv.transcript ? parseTranscriptTurns(conv.transcript) : [];

              return (
                <article className="conv-card" key={conv.id}>
                  <div className="conv-card-header">
                    <div className="conv-avatar">{initials}</div>
                    <div className="conv-info">
                      <div className="conv-info-primary">
                        <span className="conv-name">{conv.salespersonName}</span>
                        <span className="conv-email">{conv.salespersonEmail}</span>
                      </div>
                      <div className="conv-meta-row">
                        <span className="conv-meta-item">
                          <span className="conv-meta-icon">🤖</span>
                          {conv.agentLabel}
                        </span>
                        {conv.fetchedAt && (
                          <span className="conv-meta-item">
                            <span className="conv-meta-icon">📅</span>
                            {formatDate(conv.fetchedAt)}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className={`conv-status-badge ${statusClass}`}>
                      {statusLabel}
                    </span>
                  </div>

                  <div className="conv-card-footer">
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
                                {turn.role === "user" ? "Salesperson" : "AI Agent"}
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

  function renderActiveSection() {
    if (activeSection === "management") {
      return renderManagementSection();
    }

    if (activeSection === "agents") {
      return renderAgentsSection();
    }

    if (activeSection === "conversations") {
      return renderConversationsSection();
    }

    return renderDashboardSection();
  }

  return (
    <main className="workspace-root">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SP</div>
          <div>
            <strong>SalesPilot AI</strong>
            <span>Workspace</span>
          </div>
        </div>

        <div className="sidebar-group">
          <span className="sidebar-group-label">Platform</span>
          <nav className="sidebar-nav">
            {adminSections
              .filter((section) => section.group === "platform")
              .map((section) => (
                <button
                  className={activeSection === section.id ? "sidebar-link active" : "sidebar-link"}
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  type="button"
                >
                  {section.label}
                </button>
              ))}
          </nav>
        </div>

        <div className="sidebar-group">
          <span className="sidebar-group-label">Workspace</span>
          <nav className="sidebar-nav">
            {adminSections
              .filter((section) => section.group === "workspace")
              .map((section) => (
                <button
                  className={activeSection === section.id ? "sidebar-link active" : "sidebar-link"}
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  type="button"
                >
                  {section.label}
                </button>
              ))}
            <button
              className="sidebar-link"
              onClick={() => void refreshDashboard()}
              type="button"
            >
              Refresh workspace
            </button>
          </nav>
        </div>

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
            <span className="eyebrow">Admin workspace</span>
            <h1>
              {activeSection === "dashboard" && "Manage salesperson access"}
              {activeSection === "management" && "Admin management"}
              {activeSection === "agents" && "Current training agents"}
              {activeSection === "conversations" && "Conversation workspace"}
            </h1>
            <p>
              {activeSection === "dashboard" &&
                "Use the dashboard only for salesperson records, statuses, and account actions."}
              {activeSection === "management" &&
                "Send invitation emails and review one salesperson account at a time."}
              {activeSection === "agents" &&
                "Review only the currently available voice-training personas in this section."}
              {activeSection === "conversations" &&
                "Review all saved conversations that happened between salespeople and AI agents."}
            </p>
          </div>
          <button
            className="button button-secondary"
            onClick={() => void refreshDashboard()}
            type="button"
          >
            Refresh admin view
          </button>
        </header>

        {message ? <div className="message success">{message}</div> : null}
        {errorMessage ? <div className="message error">{errorMessage}</div> : null}

        {renderActiveSection()}
      </section>
      {deleteConfirm && (
        <div className="confirm-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
            <div className="confirm-icon">⚠️</div>
            <h3>Delete salesperson</h3>
            <p>
              Are you sure you want to delete{" "}
              <strong>{deleteConfirm.name}</strong>?{" "}
              This action cannot be undone.
            </p>
            <div className="confirm-actions">
              <button
                className="button button-secondary"
                onClick={() => setDeleteConfirm(null)}
                type="button"
              >
                Cancel
              </button>
              <button
                className="button button-danger"
                disabled={busyAction === `delete-${deleteConfirm.id}`}
                onClick={() => {
                  void handleDelete(deleteConfirm.id);
                  setDeleteConfirm(null);
                }}
                type="button"
              >
                {busyAction === `delete-${deleteConfirm.id}` ? "Deleting..." : "Yes, delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
