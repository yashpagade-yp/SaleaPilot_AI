# Backend

This folder contains the backend for `SaleaPilot_AI`.

## Purpose

The backend powers a voice-based sales training platform where salespeople practice with AI customer personas. The backend is responsible for:

- user and session management
- scenario selection for the four fixed personas
- Eigi agent mapping and conversation metadata creation
- Daily-based web calling session orchestration
- conversation history retrieval
- post-session feedback generation

## Planned Stack

- `Python`
- `FastAPI`
- `MongoDB`

## Core Responsibilities

- expose APIs for frontend session flows
- map each training scenario to a fixed Eigi `agent_id`
- create and track voice conversation payloads
- persist users, sessions, summaries, and feedback
- fetch conversation history from Eigi
- prepare structured feedback for the salesperson

## Scenario Set

The first version supports four fixed customer personas:

- `ideal`
- `rude`
- `confused`
- `busy`

These personas are predefined in Eigi and selected manually by the salesperson during training.

## Proposed Backend Modules

- `commons/`
  Shared helpers such as config, logging, constants, and utility functions.
- `apis/`
  FastAPI route definitions and request/response schemas.
- `controllers/`
  Business orchestration for sessions, conversations, and feedback.
- `services/`
  Integrations for Eigi, Daily, and feedback generation.
- `models/`
  MongoDB document models and persistence definitions.
- `repositories/` or `cruds/`
  Database access logic.

## Initial Goals

1. Define backend folder structure.
2. Add configuration handling for Eigi, Daily, MongoDB, and app settings.
3. Build session APIs for scenario-based call startup.
4. Store session metadata and conversation references.
5. Fetch conversation history and generate salesperson feedback.

