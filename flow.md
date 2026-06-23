# SaleaPilot_AI Project Flow

This file captures the current end-to-end product flow in simple steps.

## Roles

- `Admin`
- `Salesperson`

## Admin Flow

1. Admin already exists in the database.
2. Admin opens the platform login screen.
3. Admin enters phone number and password.
4. System validates the admin credentials directly.
5. Admin logs in successfully without any OTP step.
6. Admin opens the invitation section.
7. Admin enters the salesperson email and any supporting identity fields needed by the product.
8. System creates an `Invitation` record with `PENDING` status for that salesperson email.
9. System sends the invitation to the salesperson email.
10. Admin can view invitation status later, such as pending or accepted.

## Salesperson Flow

1. Salesperson receives the invitation email.
2. Invitation marks that email as allowed to access salesperson login.
3. Salesperson opens the platform login screen.
4. Salesperson enters the invited email address.
5. System sends a real OTP to that salesperson email.
6. Salesperson enters the OTP and logs in successfully.
7. Invitation status becomes `ACCEPTED` once the salesperson completes the verified login path.
8. Salesperson sees the fixed training scenarios:
   - `ideal`
   - `rude`
   - `busy`
9. Salesperson selects one scenario manually.
10. System finds the correct Eigi `agent_id` for the selected scenario.
11. System creates the Eigi `/v1/public/daily` voice conversation payload.
12. Payload includes:
    - selected `agent_id`
    - `conversation_metadata.name` as salesperson name
    - extra metadata like `user_id`, `scenario`, and `session_id` when needed
13. Eigi returns:
    - `id`
    - `conversation_id`
    - `dailyRoom`
    - `dailyToken`
14. System creates the `TrainingSession` record.
15. Salesperson joins the browser web call using `dailyRoom` and `dailyToken`.
16. Salesperson talks to the AI customer persona.
17. Conversation data is stored and later fetched from Eigi.
18. After the session ends, the system saves the `Conversation` record.
19. System generates one `Feedback` record for that session.
20. Salesperson views:
    - conversation history
    - transcript
    - feedback summary
    - strengths
    - improvement areas
    - scores and recommendations

## Backend Flow Summary

1. Validate user role and access.
2. Support direct admin login with phone number and password.
3. Support salesperson email-based OTP login for invited emails.
4. Accept scenario selection from salesperson.
5. Resolve the scenario to Eigi `agent_id`.
6. Create the session through Eigi `/v1/public/daily`.
7. Save session identifiers and metadata in MongoDB.
8. Fetch conversation details after or during completion.
9. Generate and store one feedback record per training session.

## Important Rules

- Admin is pre-created in the database.
- Admin logs in with phone number and password only.
- Only admin can send invitations.
- Invitation is tied to the salesperson email that admin entered.
- Only invited salespeople can access training.
- Salesperson login uses a real OTP sent to the invited email.
- Only salesperson can start a training session.
- Three personas are fixed for the current MVP.
- Each scenario maps to one Eigi `agent_id`.
- Eigi is the primary runtime for `v1` voice agent sessions.
- `conversation_metadata.name` stores the salesperson name.
- One training session has one conversation.
- One training session has one feedback record.
