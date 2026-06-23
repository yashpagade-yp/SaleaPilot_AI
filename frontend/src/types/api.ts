export type UserRole = "ADMIN" | "SALESPERSON";

export interface UserProfile {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string | null;
  role: UserRole;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
  last_login_at: string | null;
}

export interface MessageResponse {
  message: string;
}

export interface InvitationResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  status: string;
  invited_by: string;
  expires_at: string;
  accepted_at: string | null;
}

export interface InvitationAcceptResponse extends MessageResponse {
  email: string;
  status: string;
  next_step: string;
}

export interface Scenario {
  id: string;
  key: "IDEAL" | "RUDE" | "BUSY" | string;
  title: string;
  description: string;
  is_active: boolean;
  sort_order: number;
}

export interface ScenarioListResponse {
  items: Scenario[];
}

export interface TrainingSessionSummary {
  id: string;
  user_id: string;
  scenario_id: string;
  scenario_key: string;
  agent_id: string;
  status: string;
  conversation_id: string | null;
  started_at: string | null;
  ended_at: string | null;
}

export interface StartTrainingSessionResponse {
  session_id: string;
  eigi_record_id: string | null;
  conversation_id: string | null;
  daily_room: string | null;
  daily_token: string | null;
  status: string;
}

export interface ConversationRecord {
  id: string;
  training_session_id: string;
  conversation_id: string;
  agent_id: string;
  conversation_type: string;
  conversation_status: string;
  conversation_visibility: boolean;
  transcript: string | null;
  analysis: Record<string, unknown>;
  fetched_at: string | null;
}

export interface ConversationListResponse {
  items: ConversationRecord[];
  page: number;
  page_size: number;
  total: number;
}

export interface FeedbackRecord {
  id: string;
  training_session_id: string;
  user_id: string;
  scenario_id: string;
  summary: string;
  strengths: string[];
  improvement_areas: string[];
  objection_handling_score: number;
  confidence_score: number;
  clarity_score: number;
  rapport_score: number;
  closing_score: number;
  recommendations: string[];
  raw_feedback_payload: Record<string, unknown> | null;
  created_at: string;
}

export interface ApiErrorShape {
  detail?: string;
  message?: string;
}
