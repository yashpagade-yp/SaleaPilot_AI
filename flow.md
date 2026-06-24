# SaleaPilot_AI Project Flow

This file captures the current end-to-end product flow in simple, product-level steps.

## Roles

- `Admin`
- `Salesperson`

## Admin Flow

1. Admin already exists in the database.
2. Admin opens the admin login page.
3. Admin enters phone number and password.
4. System validates the admin credentials directly.
5. Admin logs in successfully without any OTP step.
6. Admin lands on the `Admin Dashboard`.
7. Admin sees a workspace access management screen.
8. Admin can invite a salesperson by entering:
   - first name
   - last name
   - email
9. System creates an `Invitation` record with `PENDING` status for that salesperson email.
10. System sends the invitation to the salesperson email.
11. Admin can view a salesperson management list in the same dashboard.
12. For each salesperson, admin can eventually see:
   - name
   - email
   - status such as `INVITED`, `ACTIVE`, or `INACTIVE`
   - updated time
13. Admin dashboard is the single place to manage invitation and access flow.

## Salesperson Flow

1. Salesperson receives the invitation email.
2. Salesperson copies the invitation token string from that email.
3. Salesperson opens the platform login screen.
4. Salesperson pastes the invitation token into the invitation field.
5. System validates that invitation token.
6. If the token is valid, salesperson enters the invited email address.
7. System sends a real OTP to that salesperson email.
8. Salesperson enters the OTP and logs in successfully.
9. Invitation status becomes `ACCEPTED` once the salesperson completes the verified login path.
10. Salesperson enters a workspace organized around three connected areas:
   - `Agents`
   - `Conversations`
   - `Feedback`
11. In `Agents`, salesperson sees the fixed training personas:
   - `ideal`
   - `rude`
   - `busy`
12. Salesperson selects one scenario manually.
13. System finds the correct Eigi `agent_id` for the selected scenario.
14. System creates the Eigi `/v1/public/daily` voice conversation payload.
15. Payload includes:
    - selected `agent_id`
    - `conversation_metadata.name` as salesperson name
    - extra metadata like `user_id`, `scenario`, and `session_id` when needed
16. Eigi returns:
    - `id`
    - `conversation_id`
    - `dailyRoom`
    - `dailyToken`
17. System creates the `TrainingSession` record.
18. Salesperson joins the browser web call using `dailyRoom` and `dailyToken`.
19. Salesperson talks to the AI customer persona.
20. In `Conversations`, the system stores and later fetches the salesperson's conversation with the selected agent.
21. After the session ends, the system saves the `Conversation` record.
22. System generates one `Feedback` record for that session.
23. In `Feedback`, salesperson views:
    - conversation history
    - transcript
    - feedback summary
    - strengths
    - improvement areas
    - scores and recommendations

## Backend Flow Summary

1. Validate user role and access.
2. Support direct admin login with phone number and password.
3. Support admin dashboard-driven invitation management.
4. Support salesperson email-based OTP login for invited emails.
5. Accept scenario selection from salesperson.
6. Resolve the scenario to Eigi `agent_id`.
7. Create the session through Eigi `/v1/public/daily`.
8. Save session identifiers and metadata in MongoDB.
9. Fetch conversation details after or during completion.
10. Generate and store one feedback record per training session.

## Important Rules

- Admin is pre-created in the database.
- Admin logs in with phone number and password only.
- Admin lands on a dedicated admin dashboard after login.
- Only admin can send invitations.
- Invitation flow should live inside the admin dashboard, not as a disconnected page.
- Invitation is tied to the salesperson email that admin entered.
- Salesperson must validate the invitation token before requesting the email OTP.
- Only invited salespeople can access training.
- Salesperson login uses a real OTP sent to the invited email.
- Only salesperson can start a training session.
- Three personas are fixed for the current MVP.
- Salesperson workspace should clearly surface `Agents`, `Conversations`, and `Feedback`.
- Salesperson can view only their own conversations and feedback.
- Admin can review salesperson conversations and feedback from the admin side.
- One salesperson must never see another salesperson's conversations or feedback.
- Each scenario maps to one Eigi `agent_id`.
- Eigi is the primary runtime for `v1` voice agent sessions.
- `conversation_metadata.name` stores the salesperson name.
- One training session has one conversation.
- One training session has one feedback record.
