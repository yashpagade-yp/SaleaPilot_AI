import { apiRequest } from "./client";
import {
  InvitationAcceptResponse,
  LoginResponse,
  OtpSentResponse,
} from "../../types/models";

export function adminLogin(payload: {
  email: string;
  password: string;
}) {
  return apiRequest<OtpSentResponse>("/v1/auth/admin/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function verifyAdminOtp(payload: { email: string; otp: string }) {
  return apiRequest<LoginResponse>("/v1/auth/admin/verify-otp", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(payload: {
  email: string;
  password: string;
}) {
  return apiRequest<OtpSentResponse>("/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function verifyOtp(payload: { email: string; otp: string }) {
  return apiRequest<LoginResponse>("/v1/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function acceptInvitation(token: string) {
  return apiRequest<InvitationAcceptResponse>("/v1/invitations/accept", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export function requestSalespersonOtp(payload: {
  invitation_token: string;
  email: string;
}) {
  return apiRequest<OtpSentResponse>("/v1/auth/salesperson/request-otp", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function salespersonLogin(payload: {
  email: string;
  password: string;
}) {
  return apiRequest<OtpSentResponse>("/v1/auth/salesperson/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function verifySalespersonOtp(payload: { email: string; otp: string }) {
  return apiRequest<LoginResponse>("/v1/auth/salesperson/verify-otp", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function completeSalespersonProfile(payload: {
  invitation_token: string;
  email: string;
  first_name: string;
  last_name: string;
  otp: string;
  password: string;
}) {
  return apiRequest<LoginResponse>("/v1/auth/salesperson/complete-profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
