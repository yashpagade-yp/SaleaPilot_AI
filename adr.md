# ADR

## Architecture Decision Record

This file captures the current high-level technical decisions for `SaleaPilot_AI`.

## ADR-001: Backend Framework

- Decision: Use `Python + FastAPI` for the backend.
- Reason:
  - strong fit for API-first backend development
  - fast iteration for integration-heavy workflows
  - clean request validation and async support
  - good fit for AI and voice integration services

## ADR-002: Database

- Decision: Use `MongoDB` as the primary database.
- Reason:
  - flexible schema for evolving conversation and feedback records
  - natural fit for session metadata and transcript-oriented storage
  - easy to store nested payloads returned by external integrations

## ADR-003: Frontend Stack

- Decision: Use `React + Vite` for the frontend.
- Reason:
  - React supports component-driven UI for training, history, and feedback screens
  - Vite supports fast frontend development and a simple app setup

## ADR-004: Voice Calling Approach

- Decision: Use `Daily` for web calling.
- Reason:
  - the product is centered on browser-based live voice training
  - Daily fits real-time call session delivery for web users

## ADR-005: Agent Platform

- Decision: Use `Eigi` for persona agent management and conversation operations.
- Reason:
  - agents are predefined in Eigi
  - each persona has a dedicated `agent_id`
  - Eigi provides conversation retrieval and listing APIs
  - conversation metadata can carry session context

## ADR-006: Persona Strategy

- Decision: Start with four fixed personas only.
- Personas:
  - `ideal`
  - `rude`
  - `confused`
  - `busy`
- Reason:
  - clear MVP scope
  - easier scenario-to-agent mapping
  - simpler backend and frontend flows

## ADR-007: Scenario Selection

- Decision: The salesperson selects the scenario manually.
- Reason:
  - keeps the user flow simple
  - gives the trainee direct control over practice type

## ADR-008: Conversation Tracking

- Decision: Store `agent_id` and session context inside conversation metadata.
- Reason:
  - matches the observed Eigi payload pattern
  - improves traceability for history and feedback generation

## ADR-009: Salesperson Name in Metadata

- Decision: Store the salesperson name in `conversation_metadata.name`.
- Reason:
  - improves readability in Eigi-side records
  - makes conversation history easier to inspect

## ADR-010: Feedback Requirement

- Decision: Backend must support both conversation history and salesperson feedback.
- Reason:
  - training value depends on more than raw call storage
  - feedback is a core product outcome, not an optional extra

## Pending ADRs

These still need confirmation later:

- authentication and user model design
- webhook vs polling for conversation completion
- feedback generation model and rubric
