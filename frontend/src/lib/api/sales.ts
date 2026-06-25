import { apiRequest } from "./client";
import {
  Conversation,
  ConversationListResponse,
  Feedback,
  ScenarioListResponse,
  StartTrainingSessionResponse,
  TrainingSession,
} from "../../types/models";

export function listScenarios(token: string) {
  return apiRequest<ScenarioListResponse>("/v1/scenarios", { token });
}

export function startTrainingSession(token: string, scenarioKey: string) {
  return apiRequest<StartTrainingSessionResponse>("/v1/training-sessions", {
    method: "POST",
    token,
    body: JSON.stringify({ scenario_key: scenarioKey }),
  });
}

export function listTrainingSessions(token: string) {
  return apiRequest<TrainingSession[]>("/v1/training-sessions", { token });
}

export function listConversations(token: string, page = 1, pageSize = 10) {
  return apiRequest<ConversationListResponse>(
    `/v1/conversations?page=${page}&page_size=${pageSize}`,
    { token },
  );
}

export function getConversationDetail(token: string, trainingSessionId: string) {
  return apiRequest<Conversation>(`/v1/conversations/${trainingSessionId}`, { token });
}

export function syncConversation(token: string, trainingSessionId: string) {
  return apiRequest<Conversation>(`/v1/conversations/${trainingSessionId}/sync`, {
    method: "POST",
    token,
  });
}

export function getFeedback(token: string, trainingSessionId: string) {
  return apiRequest<Feedback>(`/v1/feedback/${trainingSessionId}`, { token });
}

export function generateFeedback(token: string, trainingSessionId: string) {
  return apiRequest<Feedback>(`/v1/feedback/${trainingSessionId}/generate`, {
    method: "POST",
    token,
  });
}
