# Implementation Plan

## Goal

Build the backend for `SaleaPilot_AI`, a voice-based sales training platform where a salesperson practices with one of four fixed AI customer personas using Eigi-managed agents and Eigi `/v1/public/daily` sessions joined through Daily web calling.

The current product auth direction is:

- admin already exists in the database
- admin logs in directly with phone number and password
- admin does not use a mock OTP step
- admin sends invitation to the salesperson's real email address
- salesperson login is based on invited email + real email OTP

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
  Admin or salesperson using the platform
- `AuthChallenge`
  Email OTP challenge for salesperson login
- `Scenario`
  Fixed persona choice: `ideal`, `rude`, `busy`
- `TrainingSession`
  One practice session started by a salesperson
- `ConversationRecord`
  Stored conversation identifiers, metadata, status, and transcript references
- `FeedbackRecord`
  Session-level coaching feedback and summary

## Phase 3: Eigi Integration

- store Eigi API configuration securely
- create a service layer for Eigi API calls
- support voice conversation creation through the Eigi `/v1/public/daily` flow
- use the current MVP agent mapping:
  - `ideal` -> `6a397c577d18fcfe84e9d368`
  - `rude` -> `6a39847f7d18fcfe84e9d8ac`
  - `busy` -> `6a39855d7d18fcfe84e9d91e`
- build payload generation using:
  - selected `agent_id`
  - dynamic user/session metadata
  - `VOICE` conversation config
- use the current request shape:

```json
{
  "agent_id": "<selected_agent_id>",
  "conversation_metadata": {
    "name": "<salesperson_name>",
    "agent_id": "<selected_agent_id>"
  },
  "conversation_visibility": false,
  "conversation_config_type": "VOICE"
}
```

- treat `conversation_metadata` as the extension point for additional variables such as:
  - `user_id`
  - `user_name`
  - `scenario`
  - `session_id`
- retrieve conversation details
- list conversations for history views
- treat Eigi as the primary agent runtime for `v1`

## Phase 4: Auth And Invitation Flow

- keep one admin user pre-created in the database
- support direct admin login with phone number and password
- remove mock OTP dependency from the admin path
- allow only authenticated admins to send invitations
- store invitation state against the salesperson email address
- create salesperson email OTP challenges during login
- send real OTP emails to invited salesperson addresses
- verify salesperson OTP before granting access token
- mark invitation accepted when the verified salesperson completes first successful login

## Phase 5: Daily Session Flow

- create backend endpoint to start a training session
- validate selected scenario
- resolve the correct persona `agent_id`
- create conversation metadata payload
- initiate the web calling flow through the Eigi `/v1/public/daily` endpoint
- handle the expected response fields:
  - `id`
  - `conversation_id`
  - `dailyRoom`
  - `dailyToken`
- store session state in MongoDB
- return the Daily room and token data needed by the frontend to join the browser call

## Phase 6: Conversation History

- persist conversation identifiers and metadata
- fetch transcript and status from Eigi
- expose history APIs for frontend consumption
- support session detail views with scenario, timestamps, and transcript

## Phase 7: Feedback Pipeline

- define a feedback generation workflow after session completion
- produce structured coaching output for the salesperson
- include strengths, missed opportunities, objection handling quality, and improvement suggestions
- store generated feedback in MongoDB
- expose feedback APIs to the frontend

## Phase 8: Frontend Contract Support

Backend APIs should support frontend flows for:

- admin login
- admin invitation sending
- salesperson email OTP request
- salesperson OTP verification
- scenario selection
- call start
- session status polling
- transcript/history view
- feedback view

## Phase 9: Security and Reliability

- validate request payloads
- secure secrets with environment variables
- protect OTP generation, expiry, retry, and verification rules
- add retry/error handling around Eigi and Daily integrations
- add structured logs for external API operations
- add basic rate limiting around auth, OTP, and invitation endpoints

## Phase 10: Testing

- controller tests for direct admin login
- service tests for salesperson email OTP generation and verification
- invitation tests tied to salesperson email eligibility
- unit tests for scenario-to-agent mapping
- service tests for Eigi payload construction
- controller tests for session creation flow
- integration tests for MongoDB-backed session persistence
- mocked external tests for Eigi conversation retrieval

## First Deliverable

The first useful backend milestone should include:

1. FastAPI app bootstrapped
2. MongoDB connected
3. direct admin login working
4. invitation creation for salesperson email working
5. salesperson email OTP request and verification working
6. fixed scenario-to-agent mapping configured
7. endpoint to start an Eigi `/v1/public/daily` training session
8. conversation metadata saved
9. endpoint to fetch session history
10. endpoint to fetch generated feedback

## Open Items

- final email provider and OTP delivery implementation
- feedback generation source and rubric
- webhook vs polling approach for conversation completion
