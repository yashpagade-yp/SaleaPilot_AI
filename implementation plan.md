# Implementation Plan

## Goal

Build the product flow for `SaleaPilot_AI`, a voice-based sales training platform where an admin manages workspace access from a dashboard and a salesperson practices with one of three fixed AI customer personas using Eigi-managed agents and Eigi `/v1/public/daily` sessions joined through Daily web calling, with the salesperson workspace centered around `Agents`, `Conversations`, and `Feedback`.

The current product auth direction is:

- admin already exists in the database
- admin logs in directly with phone number and password
- admin does not use a mock OTP step
- admin lands on a dashboard-style management workspace after login
- admin sends invitation to the salesperson's real email address
- admin should manage invitation and salesperson access from one dashboard
- salesperson opens the accept-invitation page from the invitation email link
- invitation page should carry or prefill invited email and invitation code
- salesperson login then continues with invited email + real email OTP
- salesperson-side flow may receive additional UX updates later

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
- route the admin into a dedicated dashboard experience after login
- allow only authenticated admins to send invitations
- store invitation state against the salesperson email address
- support dashboard-driven salesperson listing and access status visibility
- validate invitation code before salesperson OTP request is allowed
- support accept-invitation page flow driven from the invitation email link
- create salesperson email OTP challenges during login
- send real OTP emails to invited salesperson addresses
- verify salesperson OTP before granting access token
- mark invitation accepted when the verified salesperson completes first successful login

## Phase 4A: Admin Dashboard Flow

- design the admin experience around one management dashboard
- include invite form inside the dashboard
- include salesperson list inside the dashboard
- show basic salesperson status such as `INVITED`, `ACTIVE`, and `INACTIVE`
- prepare UI/backend contract for actions like conversation viewing and activation control

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
- ensure the frontend call experience is rendered as a product-native AI interaction screen, not a Google Meet or generic meeting-style interface

## Phase 6: Conversation History

- support the `Conversations` section of the salesperson workspace
- persist conversation identifiers and metadata
- fetch transcript and status from Eigi
- expose history APIs for frontend consumption
- support session detail views with scenario, timestamps, and transcript

## Phase 7: Feedback Pipeline

- support the `Feedback` section of the salesperson workspace
- define a feedback generation workflow after session completion
- produce structured coaching output for the salesperson
- include strengths, missed opportunities, objection handling quality, and improvement suggestions
- store generated feedback in MongoDB
- expose feedback APIs to the frontend

## Phase 8: Frontend Contract Support

Backend APIs should support frontend flows for:

- admin login
- admin dashboard load
- admin invitation sending
- admin salesperson listing and status display
- accept-invitation link flow before salesperson login
- invitation code validation before salesperson login
- salesperson email OTP request
- salesperson OTP verification
- salesperson workspace `Agents` view
- scenario selection
- call start
- product-native live AI call screen with voice-first agent experience
- session status polling
- salesperson workspace `Conversations` view
- salesperson workspace `Feedback` view

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
4. admin dashboard-ready invitation flow working
5. invitation creation for salesperson email working
6. salesperson email OTP request and verification working
7. fixed scenario-to-agent mapping configured
8. endpoint to start an Eigi `/v1/public/daily` training session
9. conversation metadata saved
10. endpoint to fetch session history
11. endpoint to fetch generated feedback

## Open Items

- final email provider and OTP delivery implementation
- feedback generation source and rubric
- webhook vs polling approach for conversation completion
- frontend UX implementation for invitation-email-link accept flow
- frontend UX implementation for non-meeting-style live agent interaction
