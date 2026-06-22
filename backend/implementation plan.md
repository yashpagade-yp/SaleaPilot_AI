# Implementation Plan

## Goal

Build the backend for `SaleaPilot_AI`, a voice-based sales training platform where a salesperson practices with one of four fixed AI customer personas using Daily web calling and Eigi-managed agents.

## Phase 1: Project Foundation

- set up FastAPI application structure
- add environment-based configuration
- configure logging
- connect MongoDB
- define base dependency and settings management
- add health check and version endpoints

## Phase 2: Domain Modeling

Define the initial backend entities:

- `User`
  Salesperson using the platform
- `Scenario`
  Fixed persona choice: `ideal`, `rude`, `confused`, `busy`
- `AgentMapping`
  Mapping from scenario to Eigi `agent_id`
- `TrainingSession`
  One practice session started by a salesperson
- `ConversationRecord`
  Stored conversation identifiers, metadata, status, and transcript references
- `FeedbackRecord`
  Session-level coaching feedback and summary

## Phase 3: Eigi Integration

- store Eigi API configuration securely
- create a service layer for Eigi API calls
- support Daily voice conversation creation through the Eigi public Daily flow
- build payload generation using:
  - selected `agent_id`
  - dynamic user/session metadata
  - `VOICE` conversation config
- retrieve conversation details
- list conversations for history views

## Phase 4: Daily Session Flow

- create backend endpoint to start a training session
- validate selected scenario
- resolve the correct persona `agent_id`
- create conversation metadata payload
- initiate the web calling flow through the Eigi Daily endpoint
- store session state in MongoDB

## Phase 5: Conversation History

- persist conversation identifiers and metadata
- fetch transcript and status from Eigi
- expose history APIs for frontend consumption
- support session detail views with scenario, timestamps, and transcript

## Phase 6: Feedback Pipeline

- define a feedback generation workflow after session completion
- produce structured coaching output for the salesperson
- include strengths, missed opportunities, objection handling quality, and improvement suggestions
- store generated feedback in MongoDB
- expose feedback APIs to the frontend

## Phase 7: Frontend Contract Support

Backend APIs should support frontend flows for:

- user session bootstrap
- scenario selection
- call start
- session status polling
- transcript/history view
- feedback view

## Phase 8: Security and Reliability

- validate request payloads
- secure secrets with environment variables
- add retry/error handling around Eigi and Daily integrations
- add structured logs for external API operations
- add basic rate limiting and auth once user auth flow is defined

## Phase 9: Testing

- unit tests for scenario-to-agent mapping
- service tests for Eigi payload construction
- controller tests for session creation flow
- integration tests for MongoDB-backed session persistence
- mocked external tests for Eigi conversation retrieval

## First Deliverable

The first useful backend milestone should include:

1. FastAPI app bootstrapped
2. MongoDB connected
3. fixed scenario-to-agent mapping configured
4. endpoint to start a training session
5. conversation metadata saved
6. endpoint to fetch session history
7. endpoint to fetch generated feedback

## Open Items

- exact Eigi Daily endpoint contract
- frontend authentication approach
- feedback generation source and rubric
- webhook vs polling approach for conversation completion

