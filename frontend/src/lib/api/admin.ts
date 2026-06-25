import { apiRequest } from "./client";
import {
  AdminMessageResponse,
  AdminSalespeopleResponse,
  ConversationListResponse,
  FeedbackListResponse,
  InvitationResponse,
  ScenarioListResponse,
  AdminSalesperson,
} from "../../types/models";

export function listAdminAgents(token: string) {
  return apiRequest<ScenarioListResponse>("/v1/admin/agents", { token });
}

export function listSalespeople(token: string) {
  return apiRequest<AdminSalespeopleResponse>("/v1/admin/salespeople", { token });
}

export function sendInvitation(
  token: string,
  payload: { email: string },
) {
  return apiRequest<InvitationResponse>("/v1/invitations", {
    method: "POST",
    token,
    body: JSON.stringify(payload),
  });
}

export function updateSalespersonStatus(
  token: string,
  salespersonId: string,
  isActive: boolean,
) {
  return apiRequest<AdminSalesperson>(`/v1/admin/salespeople/${salespersonId}/status`, {
    method: "PATCH",
    token,
    body: JSON.stringify({ is_active: isActive }),
  });
}

export function listSalespersonConversations(
  token: string,
  salespersonId: string,
  page = 1,
  pageSize = 10,
) {
  return apiRequest<ConversationListResponse>(
    `/v1/admin/salespeople/${salespersonId}/conversations?page=${page}&page_size=${pageSize}`,
    { token },
  );
}

export function listSalespersonFeedback(
  token: string,
  salespersonId: string,
  page = 1,
  pageSize = 10,
) {
  return apiRequest<FeedbackListResponse>(
    `/v1/admin/salespeople/${salespersonId}/feedback?page=${page}&page_size=${pageSize}`,
    { token },
  );
}

export function deleteSalesperson(token: string, salespersonId: string) {
  return apiRequest<AdminMessageResponse>(`/v1/admin/salespeople/${salespersonId}`, {
    method: "DELETE",
    token,
  });
}
