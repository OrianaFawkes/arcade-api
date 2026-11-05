# Game Integration Guide

This document describes how a game is registered with Arcade API and how it submits scores.

## 1. Register the game

Every game must have a record in the `games` table.

Each game has:

- `slug`: Stable, unique identifier used by API routes and client requests.
- `name`: Display name shown in the game catalog.
- `is_active`: Whether the game is available for normal use and score submission.

Use lowercase kebab-case for slugs. Once a game has been released, avoid changing its slug because clients and stored scores may depend on it.

Initial games:

| Slug | Name |
|---|---|
| `proximity` | Proximity |
| `powers-of-two` | Powers of Two |

Run the seed script from the repository root to insert the initial games:

```bash
python -m scripts.seed_games
```

The script is idempotent: existing game records are not overwritten.

## 2. Game catalog

Clients retrieve the active game catalog through:

```http
GET /api/v1/games
```

Only active games are returned.

Example response:

```json
[
  {
    "id": "00000000-0000-0000-0000-000000000001",
    "slug": "proximity",
    "name": "Proximity"
  }
]
```

The UUID above is illustrative.

Clients should use the slug when submitting scores rather than hardcoding database IDs.

## 3. Score submission

The planned common endpoint is:

```http
POST /api/v1/games/{game_slug}/scores
Authorization: Bearer <player-session-token>
Content-Type: application/json
```

The player is identified by the bearer token. Clients must not submit a player ID, game ID, or ranking value.

The request body is game-specific and is validated using that game's Pydantic submission schema.

### Proximity

Request:

```json
{
  "difficulty": "beginner",
  "elapsed_seconds": 183
}
```

Supported difficulties:

- `beginner`
- `intermediate`
- `expert`

`elapsed_seconds` is the completed run's elapsed time in whole seconds. The client can format it as `MM:SS` for display.

Ranking:

- Lower elapsed time is better.
- Leaderboards are separated by difficulty.
- Equal times are ordered by earlier submission.

### Powers of Two

Request:

```json
{
  "score": 123456,
  "tile": 2048
}
```

Validation:

- `score` must be zero or greater.
- `tile` must be at least 2 and a power of two.

Ranking:

1. Higher score is better.
2. If scores are equal, the higher tile is better.
3. If both values are equal, the earlier submission ranks first.

## 4. Score storage

Each accepted submission represents an individual attempt.

The `scores` table stores:

- The associated player.
- The associated game.
- Game-specific submission data in JSONB.
- A server-calculated `ranking_value`.
- Submission and retention timestamps.

The client never supplies `ranking_value`. The backend calculates it from the validated game-specific payload.

Current ranking values:

| Game | Ranking value | Direction |
|---|---:|---|
| Proximity | `elapsed_seconds` | Ascending |
| Powers of Two | `score` | Descending |

Game-specific tiebreakers are applied separately when leaderboard queries are implemented.

## 5. Adding another game

When integrating a new game:

1. Choose a stable, unique slug and display name.
2. Register the game in the seed/catalog setup.
3. Create a Pydantic submission schema under `app/schemas/scores/`.
4. Define validation rules for every submitted field.
5. Define the ranking metric and tiebreaker rules.
6. Register the schema and ranking behavior with the score-submission implementation.
7. Add tests for valid payloads, invalid payloads, and ranking behavior.
8. Update this document with the game's request format and ranking rules.

Do not accept client-supplied player IDs, game IDs, or ranking values.

## 6. Important trust boundary

A valid player session identifies the submitting player; it does not prove that a client-reported score is legitimate.

Score validation, rate limiting, plausibility checks, and anomaly detection are separate concerns. Browser-based games cannot guarantee score authenticity solely through bearer authentication or CORS configuration.

For stronger guarantees, game logic and score calculation should eventually be made server-authoritative where practical.