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
  transcriptPreview: string;
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
  const [deliveryPreview, setDeliveryPreview] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");

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
              transcriptPreview:
                conversation.transcript?.slice(0, 180) || "Transcript not synced yet.",
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
    setDeliveryPreview("");
    setErrorMessage("");

    try {
      const response = await sendInvitation(token, { email: inviteEmail });
      setMessage(`Invitation sent to ${response.email}.`);
      setDeliveryPreview(
        response.dev_invitation_token
          ? `Development invitation code: ${response.dev_invitation_token}`
          : "",
      );
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
    setDeliveryPreview("");
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
    setDeliveryPreview("");
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

          <article className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Access workspace</span>
                <h2>Invite and manage from one place</h2>
              </div>
            </div>
            <div className="detail-stack">
              <div className="detail-item">
                <strong>Invitation flow</strong>
                <span>Send email access directly to a salesperson from this dashboard.</span>
              </div>
              <div className="detail-item">
                <strong>Invited now</strong>
                <span>{invitedCount} salesperson accounts are waiting to complete access.</span>
              </div>
              <div className="detail-item">
                <strong>Admin management</strong>
                <span>Use the left navigation if you want the focused account-management workspace.</span>
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
                              void handleDelete(salesperson.id);
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

  function renderConversationsSection() {
    return (
      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Conversations</span>
            <h2>Salesperson and agent history</h2>
          </div>
        </div>
        {loadingConversations ? (
          <div className="empty-state">Loading conversation workspace...</div>
        ) : !allConversations.length ? (
          <div className="empty-state">
            No saved conversations are available across the sales team yet.
          </div>
        ) : (
          <div className="stack-list">
            {allConversations.map((conversation) => (
              <div className="list-card" key={conversation.id}>
                <strong>{conversation.salespersonName}</strong>
                <span>{conversation.salespersonEmail}</span>
                <span>Agent: {conversation.agentLabel}</span>
                <span>Status: {conversation.conversationStatus.replaceAll("_", " ")}</span>
                <span>Session {conversation.trainingSessionId}</span>
                <p>{conversation.transcriptPreview}</p>
              </div>
            ))}
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
        {deliveryPreview ? <div className="message success">{deliveryPreview}</div> : null}
        {errorMessage ? <div className="message error">{errorMessage}</div> : null}

        {renderActiveSection()}
      </section>
    </main>
  );
}
