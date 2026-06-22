# SaleaPilot_AI Project Flow

This file captures the current end-to-end product flow in simple steps.

## Roles

- `Admin`
- `Salesperson`

## Admin Flow

1. Admin already exists in the database.
2. Admin opens the platform login screen.
3. Admin enters phone number and password.
4. System sends a mock OTP to the admin phone number.
5. Admin enters the OTP and logs in successfully.
6. Admin opens the invitation section.
7. Admin enters the salesperson details, mainly email and basic identity fields if needed.
8. System creates an `Invitation` record with `PENDING` status.
9. System sends the invitation to the salesperson email.
10. Admin can view invitation status later, such as pending or accepted.

## Salesperson Flow

1. Salesperson receives the invitation email.
2. Salesperson opens the invitation link or invitation flow.
3. Salesperson completes account setup.
4. System creates or activates the `Salesperson` user account.
5. Invitation status becomes `ACCEPTED`.
6. Salesperson logs in to the platform.
7. Salesperson sees the four fixed training scenarios:
   - `ideal`
   - `rude`
   - `confused`
   - `busy`
8. Salesperson selects one scenario manually.
9. System finds the correct Eigi `agent_id` for the selected scenario.
10. System creates the Eigi Daily voice conversation payload.
11. Payload includes:
    - selected `agent_id`
    - `conversation_metadata.name` as salesperson name
    - extra metadata like `user_id`, `scenario`, and `session_id` when needed
12. Eigi returns:
    - `id`
    - `conversation_id`
    - `dailyRoom`
    - `dailyToken`
13. System creates the `TrainingSession` record.
14. Salesperson joins the web call using Daily.
15. Salesperson talks to the AI customer persona.
16. Conversation data is stored and later fetched from Eigi.
17. After the session ends, the system saves the `Conversation` record.
18. System generates one `Feedback` record for that session.
19. Salesperson views:
    - conversation history
    - transcript
    - feedback summary
    - strengths
    - improvement areas
    - scores and recommendations

## Backend Flow Summary

1. Validate user role and access.
2. Accept scenario selection from salesperson.
3. Resolve the scenario to Eigi `agent_id`.
4. Create Daily conversation through Eigi.
5. Save session identifiers and metadata in MongoDB.
6. Fetch conversation details after or during completion.
7. Generate and store one feedback record per training session.

## Important Rules

- Admin is pre-created in the database.
- Admin logs in with phone number, password, and mock OTP.
- Only admin can send invitations.
- Only invited salespeople can access training.
- Only salesperson can start a training session.
- Four personas are fixed for MVP.
- Each scenario maps to one Eigi `agent_id`.
- `conversation_metadata.name` stores the salesperson name.
- One training session has one conversation.
- One training session has one feedback record.
