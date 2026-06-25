# SaleaPilot_AI Project Flow

This file captures the current end-to-end product flow in simple, product-level steps.

## Roles

- `Admin`
- `Salesperson`

## Admin Flow

1. Admin already exists in the database.
2. Admin opens the shared login page.
3. Admin enters email address and password.
4. System validates the credentials, recognizes the user role as `ADMIN`, and sends a real OTP to the admin email.
5. Admin enters the OTP to complete login.
6. System routes the admin to the `Admin Dashboard`.
7. Admin sees a workspace access management screen with sections for:
   - `Dashboard`
   - `Admin Management`
   - `Agents`
   - `Conversations`
8. Admin can invite a salesperson by entering the salesperson email address.
9. System derives safe placeholder name values from the email when first name and last name are not supplied.
10. System creates or refreshes the placeholder salesperson user record.
11. System creates an `Invitation` record with `PENDING` status for that salesperson email.
12. System sends a branded invitation email to the salesperson email address.
13. Admin can view a salesperson management list in the same workspace.
14. For each salesperson, admin can see:
   - name
   - email
   - status such as `INVITED`, `ACTIVE`, or `INACTIVE`
   - invitation state such as `PENDING` or `ACCEPTED`
   - last login or updated time
15. `Agents` in the admin workspace shows the current training personas only.
16. `Conversations` in the admin workspace shows saved conversation history across salespeople and agents.
17. Admin dashboard remains the single place to manage invitation and access flow.

## Salesperson Flow

1. Salesperson receives the invitation email.
2. Salesperson clicks the accept-invitation link or button in that email.
3. System opens the accept-invitation page directly.
4. The invited email address and invitation code are already present or prefilled on that page.
5. System validates the invitation code.
6. If the invitation code is valid, salesperson moves to a dedicated `Complete profile` step instead of entering the workspace directly.
7. System sends a real OTP to the invited salesperson email automatically when the complete-profile step opens.
8. Salesperson can also request or resend the OTP from that same page.
9. Salesperson completes profile onboarding by entering:
   - first name
   - last name
   - invited email address
   - OTP
   - password
10. System verifies the invitation token and OTP, stores the salesperson profile, saves the password, activates the account, and signs the salesperson in.
11. Invitation status becomes `ACCEPTED` once the salesperson completes the verified profile path.
12. Salesperson reaches a dashboard-style workspace organized around three connected areas:
   - `Agents`
   - `Conversations`
   - `Feedback`
13. In `Agents`, salesperson sees the fixed training personas:
   - `ideal`
   - `rude`
   - `busy`
14. Salesperson selects one scenario manually.
15. System finds the correct Eigi `agent_id` for the selected scenario.
16. System creates the Eigi `/v1/public/daily` voice conversation payload.
17. Payload includes:
    - selected `agent_id`
    - `conversation_metadata.name` as salesperson name
    - extra metadata like `user_id`, `scenario`, and `session_id` when needed
18. Eigi returns:
    - `id`
    - `conversation_id`
    - `dailyRoom`
    - `dailyToken`
19. System creates the `TrainingSession` record and an initial `Conversation` record.
20. Salesperson enters the session studio and can:
    - launch the room inside the workspace
    - open the room in a new tab
21. The launch URL uses both `dailyRoom` and `dailyToken`.
22. Salesperson talks to the AI customer persona.
23. In `Conversations`, the system stores and later fetches the salesperson's conversation with the selected agent.
24. After the session ends, the conversation can be synced manually or by the background automation worker.
25. Feedback generation happens after transcript or analysis data becomes available.
26. In `Feedback`, salesperson may briefly see a pending state before feedback is ready for a new session.
27. Once ready, salesperson views:
    - conversation history
    - transcript
    - feedback summary
    - strengths
    - improvement areas
    - scores and recommendations

## Returning Salesperson Login Flow

1. Returning salesperson opens the main login page.
2. Salesperson enters the same email address used during invitation onboarding.
3. Salesperson enters the password created during the complete-profile step.
4. System validates the credentials, recognizes the user role as `SALESPERSON`, and sends a real OTP to that salesperson email address.
5. Salesperson enters the OTP to complete login.
6. System routes the salesperson to the workspace and they can view only their own:
   - agents
   - conversations
   - feedback

## Backend Flow Summary

1. Validate user role and access.
2. Support one shared email + password login with OTP verification.
3. Support admin dashboard-driven invitation management.
4. Support branded Gmail-based invitation and OTP email delivery.
5. Support salesperson invitation acceptance and complete-profile onboarding.
6. Resolve user role from stored credentials and route users to the correct workspace after OTP verification.
7. Accept scenario selection from salesperson.
8. Resolve the scenario to Eigi `agent_id`.
9. Create the session through Eigi `/v1/public/daily`.
10. Save session identifiers and metadata in MongoDB.
11. Fetch conversation details after or during completion.
12. Generate and store one feedback record per training session.

## Important Rules

- Admin is pre-created in the database.
- Admin and returning salespeople use the same shared login page.
- The system determines whether the user is `ADMIN` or `SALESPERSON` from stored credentials.
- Admin logs in with email and password, then verifies a real OTP.
- Admin lands on a dedicated admin dashboard after login.
- Only admin can send invitations.
- Invitation flow should live inside the admin dashboard, not as a disconnected page.
- Invitation is tied to the salesperson email that admin entered.
- Salesperson should reach the invitation validation step from the invitation email link.
- Invitation code and invited email should be available on the accept-invitation page.
- Salesperson must complete the dedicated profile + OTP step before reaching the workspace.
- After onboarding, returning salesperson login uses email and password, then verifies a real OTP.
- Only invited salespeople can access training.
- Salesperson OTP is sent to the salesperson email used for onboarding and later login.
- Only salesperson can start a training session.
- Three personas are fixed for the current MVP.
- Salesperson workspace should clearly surface `Agents`, `Conversations`, and `Feedback`.
- Salesperson can view only their own conversations and feedback.
- Admin can review salesperson conversations and feedback from the admin side.
- One salesperson must never see another salesperson's conversations or feedback.
- Each scenario maps to one Eigi `agent_id`.
- Eigi is the primary runtime for `v1` voice agent sessions.
- `conversation_metadata.name` stores the salesperson name.
- Session launch should use both `dailyRoom` and `dailyToken`.
- One training session has one conversation.
- One training session has one feedback record.
