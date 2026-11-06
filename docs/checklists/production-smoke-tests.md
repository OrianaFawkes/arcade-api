# Arcade API Production Smoke Tests

Run these checks after the initial deployment and after releases that affect API behavior.

Set `BASE_URL` to the deployed Render service URL.

## 1. Basic service checks

| Endpoint | Expected result |
|---|---|
| `GET /health` | HTTP 200, `{"status":"ok"}` |
| `GET /health/database` | HTTP 200, database connected |
| `GET /api/v1/games` | HTTP 200, expected game catalog |
| `GET /docs` | Swagger UI loads |

## 2. Player journey

Use Swagger or Postman to perform the following sequence:

- [ ] Create an anonymous player using a unique test display name.
- [ ] Save the returned session token securely for the duration of the test.
- [ ] Retrieve the authenticated player's profile.
- [ ] Submit a valid score for a supported game.
- [ ] Retrieve the corresponding leaderboard.
- [ ] Confirm the submitted score appears as expected.
- [ ] Verify an unauthenticated request is rejected where authentication is required.
- [ ] Verify an invalid or revoked token is rejected.
- [ ] Verify an invalid score payload is rejected.
- [ ] Verify leaderboard pagination and filtering.

Use the actual request schemas and paths exposed by the deployed Swagger documentation.

## 3. Persistence

- [ ] Submit a test score.
- [ ] Confirm it appears on the leaderboard.
- [ ] Allow the API to restart or redeploy.
- [ ] Retrieve the leaderboard again.
- [ ] Confirm the score remains present.

Do not delete production records merely to clean up a smoke test.

## 4. Operational checks

- [ ] Check Render deployment status.
- [ ] Check recent runtime logs for unexpected errors.
- [ ] Confirm Neon remains reachable.
- [ ] Confirm the API is running the expected commit.

## 5. Record the result

| Item | Result |
|---|---|
| Date | |
| Deployment commit | |
| Database migration revision | |
| Health checks | |
| Player journey | |
| Persistence | |
| Notes / failures | |

A smoke test verifies basic production behavior. It does not replace the automated test suite or a full end-to-end test of the Flutter application.
