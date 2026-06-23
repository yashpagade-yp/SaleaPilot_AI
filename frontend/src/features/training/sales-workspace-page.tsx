import { useEffect, useMemo, useState, type FormEvent } from "react";

import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { EmptyState } from "../../components/ui/empty-state";
import { Input } from "../../components/ui/input";
import { MetricCard } from "../../components/ui/metric-card";
import { NoticeBanner } from "../../components/ui/notice-banner";
import { StatusPill } from "../../components/ui/status-pill";
import { DailyCallPanel } from "./components/daily-call-panel";
import { useAuthSession } from "../../hooks/use-auth-session";
import { salesPilotApi } from "../../lib/api/salespilot-api";
import type {
  ConversationRecord,
  FeedbackRecord,
  Scenario,
  StartTrainingSessionResponse,
  TrainingSessionSummary,
} from "../../types/api";

export function SalesWorkspacePage() {
  const auth = useAuthSession();
  const [emailState, setEmailState] = useState({ email: "" });
  const [otpState, setOtpState] = useState({ otp: "" });
  const [status, setStatus] = useState(
    "Enter your invited email to begin practice access.",
  );
  const [loading, setLoading] = useState<string | null>(null);
  const [otpRequested, setOtpRequested] = useState(false);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>("");
  const [latestSession, setLatestSession] = useState<StartTrainingSessionResponse | null>(null);
  const [sessionHistory, setSessionHistory] = useState<TrainingSessionSummary[]>([]);
  const [conversationList, setConversationList] = useState<ConversationRecord[]>([]);
  const [activeConversation, setActiveConversation] = useState<ConversationRecord | null>(null);
  const [feedbackRecord, setFeedbackRecord] = useState<FeedbackRecord | null>(null);

  const canUseWorkspace = Boolean(auth.accessToken && auth.user?.role === "SALESPERSON");

  useEffect(() => {
    if (!canUseWorkspace || !auth.accessToken) {
      return;
    }

    void loadWorkspaceData(auth.accessToken);
  }, [auth.accessToken, canUseWorkspace]);

  const activeSessionId = useMemo(
    () => latestSession?.session_id ?? sessionHistory[0]?.id ?? "",
    [latestSession, sessionHistory],
  );

  const selectedScenarioDetails = useMemo(
    () => scenarios.find((scenario) => scenario.key === selectedScenario) ?? null,
    [scenarios, selectedScenario],
  );

  const conversationAnalysisRows = useMemo(() => {
    if (!activeConversation) {
      return [];
    }

    return Object.entries(activeConversation.analysis ?? {}).slice(0, 6);
  }, [activeConversation]);

  async function loadWorkspaceData(token: string) {
    try {
      const [scenarioResponse, sessionResponse, conversationResponse] = await Promise.all([
        salesPilotApi.listScenarios(token),
        salesPilotApi.listTrainingSessions(token),
        salesPilotApi.listConversations(token),
      ]);

      setScenarios(scenarioResponse.items);
      setSessionHistory(sessionResponse);
      setConversationList(conversationResponse.items);
      if (scenarioResponse.items.length > 0 && !selectedScenario) {
        setSelectedScenario(scenarioResponse.items[0].key);
      }
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to load workspace data.");
    }
  }

  const handleRequestOtp = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading("request-otp");

    try {
      const response = await salesPilotApi.salespersonRequestOtp({ email: emailState.email });
      setOtpRequested(true);
      setStatus("Your sign-in code is on the way. Check your email and enter it below.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to request OTP.");
      setOtpRequested(false);
    } finally {
      setLoading(null);
    }
  };

  const handleVerifyOtp = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading("verify-otp");

    try {
      const response = await salesPilotApi.salespersonVerifyOtp({
        email: emailState.email,
        otp: otpState.otp,
      });
      auth.applyLogin(response);
      setStatus(`Welcome ${response.user.first_name}. You're ready to practice.`);
      await loadWorkspaceData(response.access_token);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to verify OTP.");
    } finally {
      setLoading(null);
    }
  };

  const handleStartSession = async () => {
    if (!auth.accessToken || !selectedScenario) {
      setStatus("Choose a scenario and complete OTP login before starting a session.");
      return;
    }

    setLoading("session");
    try {
      const response = await salesPilotApi.startTrainingSession(
        { scenario_key: selectedScenario },
        auth.accessToken,
      );
      setLatestSession(response);
      setStatus(
        response.daily_room
          ? "Your practice session is ready. Join the call below."
          : "Your practice session was created, but the call link is not available yet.",
      );
      await loadWorkspaceData(auth.accessToken);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to start training session.");
    } finally {
      setLoading(null);
    }
  };

  const handleOpenConversation = async (trainingSessionId: string, syncFirst = false) => {
    if (!auth.accessToken) {
      return;
    }

    setLoading(syncFirst ? "sync" : "conversation");
    try {
      const response = syncFirst
        ? await salesPilotApi.syncConversation(trainingSessionId, auth.accessToken)
        : await salesPilotApi.getConversationDetail(trainingSessionId, auth.accessToken);
      setActiveConversation(response);
      setStatus(syncFirst ? "Your conversation record has been refreshed." : "Conversation loaded.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to open conversation.");
    } finally {
      setLoading(null);
    }
  };

  const handleGenerateFeedback = async (trainingSessionId: string) => {
    if (!auth.accessToken) {
      return;
    }

    setLoading("feedback");
    try {
      const response = await salesPilotApi.generateFeedback(trainingSessionId, auth.accessToken);
      setFeedbackRecord(response);
      setStatus("Coaching feedback is ready to review.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to generate feedback.");
    } finally {
      setLoading(null);
    }
  };

  const handleLoadFeedback = async (trainingSessionId: string) => {
    if (!auth.accessToken) {
      return;
    }

    setLoading("feedback-load");
    try {
      const response = await salesPilotApi.getFeedbackDetail(trainingSessionId, auth.accessToken);
      setFeedbackRecord(response);
      setStatus("Feedback loaded.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Unable to fetch feedback.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <Card style={{ display: "grid", gap: 14 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
          <div style={{ display: "grid", gap: 8 }}>
            <span className="section-label">Salesperson Flow</span>
            <h1 style={{ margin: 0 }}>Invited email first, then OTP login</h1>
            <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
              Start with the email your team lead invited. Once you verify the code sent to your inbox, your practice space opens up right away.
            </p>
          </div>
          <StatusPill
            label={canUseWorkspace ? "Ready to practice" : "Verify your sign-in code"}
            tone={canUseWorkspace ? "success" : "warning"}
          />
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 14,
          }}
        >
          <MetricCard
            label="Access style"
            value="Secure"
            helper="Your invited email keeps sign-in simple while protecting access."
          />
          <MetricCard
            label="Practice paths"
            value={String(scenarios.length)}
            helper="Persona choices appear as soon as your sign-in is complete."
          />
          <MetricCard
            label="Practice space"
            value={canUseWorkspace ? "Open" : "Locked"}
            helper="Once your code is verified, you can move straight into live call training."
          />
        </div>
      </Card>

      <NoticeBanner
        title="Practice starts here"
        description="Sign in with your invited email, verify the code, and continue into focused sales practice with scenario-based coaching."
        tone={canUseWorkspace ? "success" : "info"}
      />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 20,
        }}
      >
        <Card style={{ display: "grid", gap: 18 }}>
          <strong>1. Enter invited email</strong>
          <form onSubmit={handleRequestOtp} style={{ display: "grid", gap: 16 }}>
            <Input
              label="Salesperson email"
              name="salesperson_login_email"
              type="email"
              autoComplete="email"
              value={emailState.email}
              onChange={(event) => setEmailState({ email: event.target.value })}
              placeholder="Enter the invited salesperson email"
              hint="Use the same email your team lead invited."
              required
            />
            <Button type="submit" disabled={loading === "request-otp" || !emailState.email}>
              {loading === "request-otp" ? "Sending code..." : "Send sign-in code"}
            </Button>
          </form>
        </Card>

        <Card style={{ display: "grid", gap: 18 }}>
          <strong>2. Verify OTP</strong>
          {otpRequested ? (
            <form onSubmit={handleVerifyOtp} style={{ display: "grid", gap: 16 }}>
              <Input
                label="Sign-in code"
                name="salesperson_email_otp"
                autoComplete="one-time-code"
                value={otpState.otp}
                onChange={(event) => setOtpState({ otp: event.target.value })}
                placeholder="Enter the code from your email"
                required
              />
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <Button
                  type="submit"
                  variant="secondary"
                  disabled={loading === "verify-otp" || !otpState.otp}
                >
                  {loading === "verify-otp" ? "Verifying..." : "Verify code"}
                </Button>
                {canUseWorkspace ? (
                  <Button type="button" variant="ghost" onClick={auth.clearSession}>
                    Sign out
                  </Button>
                ) : null}
              </div>
            </form>
          ) : (
            <EmptyState
              title="Request your code first"
              description="Enter your invited email above, and we’ll send the sign-in code you need to continue."
            />
          )}
        </Card>
      </div>

      <Card style={{ display: "grid", gap: 18 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
          <strong>3. Training workspace after verified login</strong>
          <StatusPill
            label={canUseWorkspace ? "Open for practice" : "Unlocks after sign-in"}
            tone={canUseWorkspace ? "success" : "warning"}
          />
        </div>

        {canUseWorkspace ? (
          <div style={{ display: "grid", gap: 18 }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: 20,
              }}
            >
              <Card style={{ display: "grid", gap: 18 }}>
                <strong>Scenario selection and session start</strong>
                <label style={{ display: "grid", gap: 10 }}>
                  <span style={{ fontWeight: 600 }}>Choose persona</span>
                  <select
                    value={selectedScenario}
                    onChange={(event) => setSelectedScenario(event.target.value)}
                    style={{
                      borderRadius: 16,
                      border: "1px solid rgba(123, 163, 255, 0.18)",
                      background: "rgba(6, 16, 30, 0.8)",
                      color: "#eff4ff",
                      padding: "14px 16px",
                    }}
                  >
                    {scenarios.map((scenario) => (
                      <option key={scenario.id} value={scenario.key}>
                        {scenario.title}
                      </option>
                    ))}
                  </select>
                </label>
                {selectedScenarioDetails ? (
                  <NoticeBanner
                    title={selectedScenarioDetails.title}
                    description={selectedScenarioDetails.description}
                    tone="info"
                  />
                ) : (
                  <EmptyState
                    title="Practice options are loading"
                    description="Your persona choices will appear here as soon as your practice space finishes loading."
                  />
                )}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: 12,
                  }}
                >
                  {scenarios.map((scenario) => (
                    <div
                      key={scenario.id}
                      style={{
                        padding: 16,
                        borderRadius: 18,
                        border:
                          selectedScenario === scenario.key
                            ? "1px solid rgba(104, 213, 255, 0.28)"
                            : "1px solid rgba(123, 163, 255, 0.12)",
                        background:
                          selectedScenario === scenario.key
                            ? "rgba(104, 213, 255, 0.08)"
                            : "rgba(6, 16, 30, 0.52)",
                      }}
                    >
                      <strong>{scenario.title}</strong>
                      <p style={{ margin: "8px 0 0", color: "#9eb0cf", lineHeight: 1.6 }}>
                        {scenario.description}
                      </p>
                    </div>
                  ))}
                </div>
                <Button onClick={handleStartSession} disabled={loading === "session" || !selectedScenario}>
                  {loading === "session" ? "Starting session..." : "Start practice session"}
                </Button>
              </Card>

              <DailyCallPanel
                roomUrl={latestSession?.daily_room ?? null}
                token={latestSession?.daily_token ?? null}
                sessionReference={latestSession?.conversation_id ?? null}
                onStatusChange={setStatus}
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: 20,
              }}
            >
              <Card style={{ display: "grid", gap: 18 }}>
                <strong>Practice history</strong>
                <div style={{ display: "grid", gap: 12 }}>
                  {sessionHistory.length === 0 ? (
                    <EmptyState
                      title="No practice sessions yet"
                      description="Once you complete your first session, it will appear here with quick actions to review the conversation and feedback."
                    />
                  ) : (
                    sessionHistory.map((session) => (
                      <div
                        key={session.id}
                        style={{
                          display: "grid",
                          gap: 12,
                          padding: 16,
                          borderRadius: 18,
                          border: "1px solid rgba(123, 163, 255, 0.12)",
                          background: "rgba(6, 16, 30, 0.52)",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            gap: 12,
                            flexWrap: "wrap",
                          }}
                        >
                          <strong>{session.scenario_key}</strong>
                          <StatusPill label={session.status} />
                        </div>
                        <p style={{ margin: 0, color: "#9eb0cf" }}>Session reference: {session.id}</p>
                        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                          <Button
                            variant="secondary"
                            onClick={() => handleOpenConversation(session.id)}
                            disabled={loading === "conversation"}
                          >
                            Review conversation
                          </Button>
                          <Button
                            variant="ghost"
                            onClick={() => handleOpenConversation(session.id, true)}
                            disabled={loading === "sync"}
                          >
                            Refresh record
                          </Button>
                          <Button
                            variant="ghost"
                            onClick={() => handleLoadFeedback(session.id)}
                            disabled={loading === "feedback-load"}
                          >
                            Open feedback
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </Card>

              <Card style={{ display: "grid", gap: 18 }}>
                <strong>Conversation list</strong>
                <div style={{ display: "grid", gap: 12 }}>
                  {conversationList.length === 0 ? (
                    <EmptyState
                      title="No conversations yet"
                      description="After your first call, your recent conversation records will appear here for quick review."
                    />
                  ) : (
                    conversationList.map((conversation) => (
                      <div
                        key={conversation.id}
                        style={{
                          padding: 16,
                          borderRadius: 18,
                          border: "1px solid rgba(123, 163, 255, 0.12)",
                          background: "rgba(6, 16, 30, 0.52)",
                          display: "grid",
                          gap: 10,
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                          <strong>{conversation.conversation_type}</strong>
                          <StatusPill label={conversation.conversation_status} />
                        </div>
                        <p style={{ margin: 0, color: "#9eb0cf" }}>
                          Practice session: {conversation.training_session_id}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </Card>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: 20,
              }}
            >
              <Card style={{ display: "grid", gap: 18 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                  <strong>Transcript and call detail</strong>
                  {activeSessionId ? (
                    <Button
                      variant="secondary"
                      onClick={() => handleGenerateFeedback(activeSessionId)}
                      disabled={loading === "feedback"}
                    >
                      {loading === "feedback" ? "Preparing..." : "Generate coaching"}
                    </Button>
                  ) : null}
                </div>
                {activeConversation ? (
                  <div style={{ display: "grid", gap: 14 }}>
                    <StatusPill label={activeConversation.conversation_status} />
                    <p style={{ margin: 0, color: "#9eb0cf" }}>
                      Call reference: {activeConversation.conversation_id}
                    </p>
                    <div
                      style={{
                        padding: 16,
                        borderRadius: 18,
                        background: "rgba(6, 16, 30, 0.72)",
                        border: "1px solid rgba(123, 163, 255, 0.12)",
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.7,
                        color: "#dfe8f8",
                        minHeight: 220,
                      }}
                    >
                      {activeConversation.transcript ?? "Transcript not available yet."}
                    </div>
                    {conversationAnalysisRows.length > 0 ? (
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                          gap: 12,
                        }}
                      >
                      {conversationAnalysisRows.map(([key, value]) => (
                          <MetricCard
                            key={key}
                            label={key}
                            value={typeof value === "number" ? value.toFixed(1) : String(value)}
                            helper="A useful signal taken from your conversation review."
                          />
                        ))}
                      </div>
                    ) : null}
                  </div>
                ) : (
                  <EmptyState
                    title="Open a conversation to review it"
                    description="Choose a practice session from your history to see the transcript and key conversation signals here."
                  />
                )}
              </Card>

              <Card style={{ display: "grid", gap: 18 }}>
                <strong>Feedback summary</strong>
                {feedbackRecord ? (
                  <div style={{ display: "grid", gap: 14 }}>
                    <p style={{ margin: 0, color: "#dfe8f8", lineHeight: 1.7 }}>
                      {feedbackRecord.summary}
                    </p>
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                        gap: 12,
                      }}
                    >
                      <ScoreCard label="Confidence" value={feedbackRecord.confidence_score} />
                      <ScoreCard label="Clarity" value={feedbackRecord.clarity_score} />
                      <ScoreCard label="Rapport" value={feedbackRecord.rapport_score} />
                      <ScoreCard label="Closing" value={feedbackRecord.closing_score} />
                    </div>
                    <ListBlock title="Strengths" items={feedbackRecord.strengths} />
                    <ListBlock
                      title="Improvement areas"
                      items={feedbackRecord.improvement_areas}
                    />
                    <ListBlock title="Recommendations" items={feedbackRecord.recommendations} />
                  </div>
                ) : (
                  <EmptyState
                    title="Coaching will appear here"
                    description="Generate feedback from a selected practice session, or reopen an existing coaching summary when it’s ready."
                  />
                )}
              </Card>
            </div>
          </div>
        ) : (
          <EmptyState
            title="Verify your sign-in code to begin"
            description="Once your email code is confirmed, your practice space opens and you can move into scenario-based training."
          />
        )}
      </Card>

      <Card style={{ display: "grid", gap: 12 }}>
        <strong>Latest update</strong>
        <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>{status}</p>
      </Card>
    </div>
  );
}

function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <div
      style={{
        padding: 16,
        borderRadius: 18,
        background: "rgba(6, 16, 30, 0.72)",
        border: "1px solid rgba(123, 163, 255, 0.12)",
        display: "grid",
        gap: 8,
      }}
    >
      <span style={{ color: "#9eb0cf" }}>{label}</span>
      <strong style={{ fontSize: "1.7rem" }}>{value.toFixed(1)}</strong>
    </div>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <strong>{title}</strong>
      <ul style={{ margin: 0, paddingLeft: 20, color: "#9eb0cf", lineHeight: 1.7 }}>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
