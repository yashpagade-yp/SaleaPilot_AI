# SaleaPilot_AI

AI-powered voice training platform for salespeople practicing realistic customer conversations.

## Overview

`SaleaPilot_AI` is a voice-based sales training platform where salespeople practice with AI customer personas in realistic call scenarios.

The system uses:

- `Eigi` for persona-based AI agents and conversation operations
- `Daily` for web-based voice calling
- `Python + FastAPI` for the backend
- `MongoDB` for the database
- `React + Vite` for the frontend

## Product Goal

Help salespeople improve how they handle real customer conversations by practicing with AI-driven customer personas.

## Fixed Training Personas

The first version supports four predefined personas:

- `ideal`
- `rude`
- `confused`
- `busy`

These personas are predefined in Eigi and selected manually by the salesperson during training.

## Core Responsibilities

- user and session management
- scenario selection for the four fixed personas
- Eigi agent mapping and conversation metadata creation
- Daily-based web calling session orchestration
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

## Planned Backend Modules

- `backend/commons/`
  Shared helpers such as config, logging, constants, and utility functions.
- `backend/apis/`
  FastAPI route definitions and request/response schemas.
- `backend/controllers/`
  Business orchestration for sessions, conversations, and feedback.
- `backend/services/`
  Integrations for Eigi, Daily, and feedback generation.
- `backend/models/`
  MongoDB document models and persistence definitions.
- `backend/repositories/` or `backend/cruds/`
  Database access logic.

## Planning Docs

- [implementation plan.md](./implementation%20plan.md)
- [adr.md](./adr.md)
