# Frontend Implementation Plan

This document defines the fresh frontend rebuild plan for `SalesPilot AI`.

The frontend should follow the finalized backend flow from [flow.md](../flow.md) and the product notes from [README.md](../README.md).

## Product Direction

The frontend should feel like one polished product, not two disconnected apps.

There should be:

- one shared product experience
- one common authentication entry pattern
- role-based routing after user identification
- separate internal experiences for `Admin` and `Salesperson`

That means:

- `Admin` is routed to the admin workspace
- `Salesperson` is routed to the salesperson workspace

We should not build two unrelated login products.

## Visual Direction

The frontend should use a premium dark product style.

Color balance:

- `50%` black
- `30%` white
- `20%` soft silk-like reference tone from the provided screenshots

This silk-like accent should feel like a:

- light warm neutral
- soft skin-toned beige
- smooth premium highlight color
- subtle luxury accent, not a loud bright color

The final UI should feel:

- dark
- modern
- product-focused
- high contrast
- smooth and user-friendly

Avoid:

- flat, dull screens
- repeated old frontend patterns
- meeting-app styling for voice practice
- overly light cream-first layouts as the final product style

## Landing Visual Rule

The landing page should take the provided dark hero reference as the primary visual direction.

That means:

- black should remain the dominant base
- white should remain the primary text and contrast color
- the silk-like warm tone should be introduced as a controlled accent layer

This accent should be used in places like:

- soft gradient blending
- glow details
- highlight words
- subtle borders
- hover states
- supporting visual surfaces

The landing page should not become cream-based or light-themed.

It should stay a dark premium hero system with a soft warm luxury accent.

## Main Frontend Areas

The rebuild should cover these product areas:

1. Landing page
2. Invitation acceptance flow
3. Shared authentication flow with role-based routing
4. Admin workspace
5. Salesperson workspace
6. Voice practice session UI

## Landing Page Plan

The landing page should contain `5` major sections.

These are sections in one smooth landing experience, not literal labels like `Slide 1`, `Slide 2`, and so on.

### Section 1: Hero

Purpose:

- introduce `SalesPilot AI`
- create a strong first impression
- explain the product in one sharp line
- guide users into the product flow

Content direction:

- bold headline about AI sales practice
- short supporting copy
- CTA for entering the product
- premium dark hero treatment inspired by the provided hero references
- black-and-white visual base with a soft silk-like warm accent layered into the design

### Section 2: How The Product Works

Purpose:

- explain the core workflow clearly
- show that the system starts from admin setup and ends in salesperson coaching

Content direction:

- admin creates access
- salesperson accepts invitation
- salesperson verifies identity
- salesperson practices with AI personas
- system stores conversation and feedback

### Section 3: AI Practice Personas

Purpose:

- present the training value of the product
- explain the available customer behaviors

Content direction:

- `ideal`
- `rude`
- `busy`

Each persona block should explain what kind of challenge it gives the salesperson.

### Section 4: Conversation And Feedback Value

Purpose:

- show that the product is not only about calling
- show that conversation history and coaching are part of the system

Content direction:

- conversation review
- transcript visibility
- performance insights
- strengths
- improvement areas
- scoring and recommendations

### Section 5: Product Entry / Final CTA

Purpose:

- move the user into the product flow
- clearly direct users toward sign-in / access

Content direction:

- one final strong CTA
- clear message that access depends on role and invitation status
- transition into the role-based auth journey

## Auth And Access Plan

The frontend must not present separate product identities for admin and salesperson.

We should use one product entry flow and separate the experience by role after validation.

### Admin Auth

- admin already exists in the backend database
- admin signs in with `phone number + password`
- no OTP for admin
- successful login routes admin to the admin workspace

### Salesperson Auth

- salesperson is invited by admin
- salesperson receives invitation email
- email contains an invitation code and accept-invitation link
- accept-invitation page opens with invited email and invitation code prefilled
- invitation code is validated first
- salesperson continues with invited email OTP verification
- successful verification routes salesperson to the salesperson workspace

## Invitation Flow Plan

The invitation journey should feel structured and guided.

### Step 1: Invitation Email

The email should communicate:

- the salesperson has been invited
- the invitation code
- the accept-invitation button
- that the code is tied to the invited email

### Step 2: Accept Invitation Page

This page should:

- receive the email and invitation code from the invite link
- show them in a controlled, product-friendly UI
- validate the code
- move the user into OTP and account completion

### Step 3: OTP And Profile Completion

This stage should support:

- invited email confirmation
- OTP input
- password creation if required by the backend path
- basic profile completion fields when part of the flow

## Admin Workspace Plan

The admin side should be a real management workspace, not a plain form screen.

### Admin Goals

- sign in quickly
- send invitations
- monitor salesperson access
- review user status
- review salesperson conversations
- review salesperson feedback

### Admin Workspace Sections

- dashboard header / overview
- invitation panel
- salesperson management list
- salesperson detail actions
- conversation review access
- feedback review access

### Admin UX Direction

The admin workspace should feel:

- operational
- clear
- table-friendly
- easy to scan
- suitable for repeated team management tasks

## Salesperson Workspace Plan

The salesperson workspace should be built around `3` primary product sections:

- `Agents`
- `Conversations`
- `Feedback`

### Dashboard View

The main dashboard should summarize:

- available training personas
- recent conversations
- latest feedback activity
- quick actions to start practice or review progress

### Agents Section

Purpose:

- browse available training personas
- understand what each persona represents
- choose one persona and start practice

Expected behavior:

- search or browse agents
- see agent description
- select persona
- start voice practice session

### Conversations Section

Purpose:

- let the salesperson review past sessions

Expected behavior:

- see only their own conversations
- search and filter conversations
- open transcript and related details
- review history by session

### Feedback Section

Purpose:

- let the salesperson review performance after each session

Expected behavior:

- see only their own feedback
- open session-level feedback
- view strengths
- view improvement areas
- view scores
- view recommendations

## Access Rules In Frontend

Frontend behavior must respect these product rules:

- admin can access admin-only management views
- salesperson can access only salesperson views
- salesperson can view only their own conversations
- salesperson can view only their own feedback
- one salesperson must never see another salesperson's data
- admin can review salesperson conversations and feedback from the admin side

## Voice Practice Session UI Plan

The live session UI should not look like Google Meet, Zoom, or a generic meeting screen.

It should feel like a native AI training interface.

### Voice Session Experience

The experience should emphasize:

- one focused AI conversation space
- voice-first interaction
- agent identity / persona context
- lightweight conversation cues
- calm visual focus

### UI Direction

Use the provided references to create:

- a centered AI orb or voice core
- minimal call controls
- persona context
- subtle transcript/chat moments where useful
- a product-native training feel

Avoid:

- participant-grid meeting visuals
- conference-app layouts
- generic video-call styling

## Frontend Information Architecture

Suggested route direction:

- `/`
  Landing page
- `/accept-invitation`
  Invite validation and continuation flow
- `/login`
  Shared entry point for authenticated access paths
- `/admin/...`
  Admin workspace routes
- `/workspace/...`
  Salesperson workspace routes

Role-based routing should decide which protected area becomes available after authentication.

## Suggested Frontend Structure

The rebuild should follow a clean structure aligned with the frontend standards:

- `src/app` or framework route directory for route entry
- `src/features/landing`
- `src/features/auth`
- `src/features/invitation`
- `src/features/admin`
- `src/features/workspace`
- `src/features/agents`
- `src/features/conversations`
- `src/features/feedback`
- `src/features/session`
- `src/components/ui`
- `src/components/layout`
- `src/lib/api`
- `src/hooks`
- `src/styles`

## State And API Plan

Frontend should keep backend communication centralized.

Needed frontend data areas:

- auth state
- current user identity
- current role
- invitation validation state
- salesperson workspace data
- admin workspace data
- active voice session state

API handling should cover:

- loading states
- empty states
- unauthorized states
- error states
- success confirmation states

## Responsive Plan

The frontend should work well on:

- desktop
- laptop
- tablet
- mobile

Priority:

- landing page remains visually impressive on all sizes
- dashboards remain readable and navigable
- key forms remain simple and accessible

## Implementation Order

Recommended execution order:

1. Set up frontend app foundation, theme tokens, routing, and shared layout system.
2. Build the 5-section landing page in the final dark style.
3. Build the invitation acceptance flow.
4. Build the shared auth flow with role-based routing.
5. Build the admin workspace.
6. Build the salesperson dashboard shell.
7. Build `Agents`, `Conversations`, and `Feedback` sections.
8. Build the non-meeting-style live voice session UI.
9. Connect all frontend flows to backend APIs.
10. Test role gates, invitation flow, session flow, and review flow.

## Final Goal

The rebuilt frontend should present `SalesPilot AI` as a polished dark SaaS product where:

- the landing page sells the product clearly
- admin starts the access journey
- salesperson completes a guided invite and OTP path
- role-based routing keeps the app unified
- practice happens through AI personas
- conversations and feedback remain central to the product value
- the voice session feels like an AI sales simulator, not a meeting tool
