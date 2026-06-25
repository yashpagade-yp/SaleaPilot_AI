# SaleaPilot_AI

AI-powered voice training platform for salespeople practicing realistic customer conversations.

## Overview

`SaleaPilot_AI` is a voice-based sales training platform where salespeople practice with AI customer personas in realistic call scenarios.

The system uses:

- `Eigi` for persona-based AI agents, `/v1/public/daily` session creation, and conversation operations
- `Daily` for web-based voice call joining
- `Python + FastAPI` for the backend
- `MongoDB` for the database
- `React + Vite` for the frontend

## Product Goal

Help salespeople improve how they handle real customer conversations by practicing with AI-driven customer personas.

## Current Product Flow

The current product flow now follows these rules:

- `Admin` already exists in the backend database
- admin logs in directly with `phone number + password`
- admin does **not** use a mock OTP flow
- admin lands on a dashboard-style admin workspace after login
- admin sends an invitation to the salesperson's real email address
- admin should manage salespeople from one place instead of jumping across separate screens
- invitation email should contain an accept-invitation link or button
- invitation page should open with invited email and invitation code already available
- invitation allows that salesperson email to use the platform login flow
- salesperson then logs in with the invited email address
- system sends a real OTP to the salesperson email
- salesperson completes login by entering the email OTP
- salesperson-side UX may receive later flow refinements

## Fixed Training Personas

The current MVP supports three predefined personas:

- `ideal`
- `rude`
- `busy`

These personas are created in Eigi and selected manually by the salesperson during training.

Current scenario-to-agent mapping:

- `ideal` -> `6a397c577d18fcfe84e9d368`
- `rude` -> `6a39847f7d18fcfe84e9d8ac`
- `busy` -> `6a39855d7d18fcfe84e9d91e`

The `confused` persona is intentionally postponed for a later version to reduce credit usage.

## Core Responsibilities

- user and session management
- direct admin authentication
- admin dashboard access management
- salesperson invitation by email
- salesperson email-OTP authentication
- scenario selection for the three fixed personas
- Eigi agent mapping and conversation metadata creation
- Eigi `/v1/public/daily` session orchestration
- Daily room/token delivery for frontend web call joining
- conversation history retrieval
- post-session feedback generation

## Salesperson Workspace Direction

The salesperson workspace should be organized around three connected sections:

- `Agents`
  The three training personas the salesperson can practice with.
- `Conversations`
  The salesperson's conversation records with a selected agent or persona.
- `Feedback`
  The salesperson's performance review, including summary, strengths, improvement areas, scores, and recommendations.

## Eigi Daily Conversation Flow

The current Daily-based conversation creation pattern uses a payload like:

```json
{
  "agent_id": "698b08ba0944eaf73a6011a5",
  "conversation_metadata": {
    "name": "sda",
    "agent_id": "698b08ba0944eaf73a6011a5"
  },
  "conversation_visibility": false,
  "conversation_config_type": "VOICE"
}
```

For product use, the backend should:

- replace `agent_id` dynamically based on the selected scenario
- keep `conversation_config_type` as `VOICE`
- keep `conversation_visibility` as `false` unless product rules change
- use `conversation_metadata.name` for the salesperson's name
- add extra dynamic variables inside `conversation_metadata` when needed

Suggested metadata additions:

- `user_id`
- `user_name`
- `scenario`
- `session_id`

The expected response format is:

```json
{
  "details": "Daily conversation session created successfully",
  "id": "6a39178c7d18fcfe84e998af",
  "conversation_id": "978b94d7-a283-43d6-857a-e5afcc45db73",
  "dailyRoom": "https://cloud-fb3e28818d034e0692196061c.daily.co/f0vuQxrim51tlXIDDY4S",
  "dailyToken": "token-value"
}
```

This means the system should store and use:

- internal Eigi record `id`
- `conversation_id` for history lookup
- `dailyRoom` for the web call join flow
- `dailyToken` for room access

## Product Auth And Access Flow

### Admin

- admin record is pre-created in the database
- admin logs in using phone number and password
- admin reaches the `Admin Dashboard` after successful login
- admin uses the same dashboard to:
  - send invitations
  - view salesperson records
  - review status such as invited, active, or inactive
  - manage access-related actions over time

### Salesperson

- salesperson receives the invitation email
- salesperson clicks the accept-invitation link or button from the email
- salesperson reaches the accept-invitation page
- invited email and invitation code are already present or prefilled there
- system validates the invitation code
- salesperson then logs in with the invited email address
- system sends a real OTP to that email
- salesperson enters OTP to complete login
- salesperson accesses a workspace built around:
  - agents
  - conversations
  - feedback
- salesperson uses `Agents` to choose a training persona
- salesperson uses `Conversations` to review call history and transcript
- salesperson uses `Feedback` to review performance after each session
- each salesperson can see only their own conversations and feedback
- admins can review salesperson conversations and feedback from the admin side
- one salesperson must never see another salesperson's conversations or feedback

## Admin Dashboard Direction

The admin experience should feel like a real management dashboard instead of a basic form page.

The dashboard direction includes:

- a clean sidebar or workspace navigation structure
- a clear workspace access management header
- an invite panel inside the dashboard
- a salesperson list or table inside the dashboard
- status visibility for invited and active users
- room for future actions such as conversation review, activation control, and removal

## Runtime Direction For V1

For the first version, the live training call should use:

- `Eigi` as the primary voice-agent runtime
- `Eigi /v1/public/daily` to create the call session
- `Daily` on the frontend to join the browser call

This means we do not need a separate Pipecat-based runtime for the core `v1`
voice flow if Eigi is already handling the agent runtime for these sessions.

## Gmail Email Setup

Invitation and OTP emails now use async Gmail SMTP with HTML and plain-text
templates.

1. Copy `backend/.env.example` to `backend/.env`.
2. Set `gmail_user` to your Gmail address.
3. Set `gmail_app_password` to your 16-character Gmail App Password.
4. Set `FRONTEND_BASE_URL` to the frontend app URL that should open from the
   invitation email. For local development use `http://localhost:5173`.
5. Optionally set:
   - `company_name`
   - `support_email`
   - `logo_url`
6. Restart the backend server after updating the environment file.

How to get a Gmail App Password:

1. Enable 2-Step Verification on your Google account.
2. Go to `Google Account -> Security -> App Passwords`.
3. Generate a password for `Mail` on `Other device`.
4. Paste that 16-character password into `gmail_app_password`.

Notes:

- Invitation emails and OTP emails are both sent through the same Gmail async
  helper.
- In non-production environments, the frontend still shows a development
  preview of the invitation code and OTP so local testing is not blocked if
  mailbox delivery is delayed.

## Planned Backend Modules

- `backend/commons/`
  Shared helpers such as config, logging, constants, and utility functions.
- `backend/core/apis/`
  FastAPI route definitions and request/response schemas.
- `backend/core/controller/`
  Business orchestration for sessions, conversations, and feedback.
- `backend/core/services/`
  Integrations for Eigi session creation, conversation retrieval, and feedback generation.
- `backend/core/models/`
  MongoDB document models and persistence definitions.
- `backend/core/cruds/`
  Database access logic.

## Planning Docs

- [implementation plan.md](./implementation%20plan.md)
- [adr.md](./adr.md)
