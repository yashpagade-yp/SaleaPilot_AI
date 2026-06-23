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

## Current Auth Direction

The product authentication flow now follows these rules:

- `Admin` already exists in the backend database
- admin logs in directly with `phone number + password`
- admin does **not** use a mock OTP flow
- admin sends an invitation to the salesperson's real email address
- invitation allows that salesperson email to use the platform login flow
- salesperson logs in with the invited email address
- system sends a real OTP to the salesperson email
- salesperson completes login by entering the email OTP

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
- salesperson invitation by email
- salesperson email-OTP authentication
- scenario selection for the four fixed personas
- Eigi agent mapping and conversation metadata creation
- Eigi `/v1/public/daily` session orchestration
- Daily room/token delivery for frontend web call joining
- conversation history retrieval
- post-session feedback generation

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
- admin opens the invitation area after successful login
- admin sends an invitation to the salesperson email

### Salesperson

- salesperson receives the invitation email
- salesperson logs in with the invited email address
- system sends a real OTP to that email
- salesperson enters OTP to complete login
- salesperson accesses scenario selection, web calling, history, transcript, and feedback

## Runtime Direction For V1

For the first version, the live training call should use:

- `Eigi` as the primary voice-agent runtime
- `Eigi /v1/public/daily` to create the call session
- `Daily` on the frontend to join the browser call

This means we do not need a separate Pipecat-based runtime for the core `v1`
voice flow if Eigi is already handling the agent runtime for these sessions.

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
