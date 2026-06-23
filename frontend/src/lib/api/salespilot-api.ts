import { apiRequest } from "./client";
import type {
  ConversationListResponse,
  ConversationRecord,
  FeedbackRecord,
  InvitationAcceptResponse,
  InvitationResponse,
  LoginResponse,
  MessageResponse,
  ScenarioListResponse,
  StartTrainingSessionResponse,
  TrainingSessionSummary,
} from "../../types/api";

export const salesPilotApi = {
  adminLogin: (payload: { phone_number: string; password: string }) =>
    apiRequest<LoginResponse>("/v1/auth/admin/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  salespersonRequestOtp: (payload: { email: string }) =>
    apiRequest<MessageResponse>("/v1/auth/salesperson/request-otp", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  salespersonVerifyOtp: (payload: { email: string; otp: string }) =>
    apiRequest<LoginResponse>("/v1/auth/salesperson/verify-otp", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  resetPassword: (payload: { email: string }) =>
    apiRequest<MessageResponse>("/v1/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  sendInvitation: (
    payload: { email: string; first_name: string; last_name: string },
    token: string,
  ) =>
    apiRequest<InvitationResponse>("/v1/invitations", {
      method: "POST",
      body: JSON.stringify(payload),
      token,
    }),

  acceptInvitation: (payload: { token: string }) =>
    apiRequest<InvitationAcceptResponse>("/v1/invitations/accept", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listScenarios: (token: string) =>
    apiRequest<ScenarioListResponse>("/v1/scenarios?active_only=true", {
      token,
    }),

  startTrainingSession: (payload: { scenario_key: string }, token: string) =>
    apiRequest<StartTrainingSessionResponse>("/v1/training-sessions", {
      method: "POST",
      body: JSON.stringify(payload),
      token,
    }),

  listTrainingSessions: (token: string) =>
    apiRequest<TrainingSessionSummary[]>("/v1/training-sessions", {
      token,
    }),

  listConversations: (token: string) =>
    apiRequest<ConversationListResponse>("/v1/conversations?page=1&page_size=10", {
      token,
    }),

  getConversationDetail: (trainingSessionId: string, token: string) =>
    apiRequest<ConversationRecord>(`/v1/conversations/${trainingSessionId}`, {
      token,
    }),

  syncConversation: (trainingSessionId: string, token: string) =>
    apiRequest<ConversationRecord>(`/v1/conversations/${trainingSessionId}/sync`, {
      method: "POST",
      token,
    }),

  getFeedbackDetail: (trainingSessionId: string, token: string) =>
    apiRequest<FeedbackRecord>(`/v1/feedback/${trainingSessionId}`, {
      token,
    }),

  generateFeedback: (trainingSessionId: string, token: string) =>
    apiRequest<FeedbackRecord>(`/v1/feedback/${trainingSessionId}/generate`, {
      method: "POST",
      token,
    }),
};
