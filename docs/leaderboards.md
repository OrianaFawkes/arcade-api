
# Arcade Leaderboards

This document defines the leaderboard rules, ranking behavior, API contract, and implementation guidelines for Arcade games.

It serves as the reference for both backend implementation and frontend integration.

For game registration and score submission requirements, see [Game Integration](./game-integration.md).

---

## 1. Overview

Arcade provides public, game-specific leaderboards.

Each leaderboard displays a player's best eligible score rather than every individual attempt.

The leaderboard system is designed to support different ranking rules across games while maintaining a consistent API response structure.

### Core principles

- Each player appears at most once per leaderboard.
- Only eligible scores are considered.
- Each game defines its own ranking rules.
- Ranking is calculated before pagination.
- Leaderboards are publicly accessible without authentication.
- Individual score attempts are retained independently of leaderboard eligibility.

---

## 2. Score Eligibility

A score is eligible for leaderboard consideration when:

- Its `archived_at` value is `NULL`.
- Its `expires_at` value is later than the current UTC time.
- Its associated game is active.

Expired and archived scores are excluded from leaderboard results.

Scores are not deleted when they expire. Their eligibility is determined at query time.

### Best-attempt selection

Each player contributes only their best eligible attempt to a leaderboard.

If their previous best attempt expires or is archived, their next-best eligible attempt becomes their leaderboard entry.

The best attempt is selected independently for each leaderboard category where applicable.

For example, Proximity maintains separate leaderboards for each difficulty. A player can therefore have one entry on Beginner, another on Intermediate, and another on Expert.

---

## 3. Ranking and Tie-breaking

Every game must define:

1. Its primary ranking metric.
2. Whether higher or lower values are better.
3. Any secondary ranking metrics.
4. Its tie-breaking rules.
5. Whether it has separate leaderboard categories.

Ties are resolved deterministically. Unless a game explicitly defines otherwise, earlier submissions rank ahead of later submissions, with score UUID as the final tie-breaker.

Every entry receives a unique sequential rank.

---

## 4. Current Game Leaderboards

### 4.1 Proximity

**Game slug:** `proximity`

**Leaderboard categories:**

- `beginner`
- `intermediate`
- `expert`

Each difficulty has its own leaderboard.

**Primary ranking metric:** `elapsed_seconds`

**Ranking direction:** Ascending (lower is better).

**Best-attempt selection:**

- Only scores matching the requested difficulty are considered.
- Each player contributes their fastest eligible attempt for that difficulty.

**Tie-breaking:**

1. Lower elapsed time.
2. Earlier submission (`created_at`).
3. Lower score UUID.

**Score data:**

```json
{
  "difficulty": "beginner",
  "elapsed_seconds": 83
}
```

**API endpoint:**

```http
GET /api/v1/games/proximity/leaderboard?difficulty=beginner
```

The `difficulty` query parameter is required.

Accepted values:

- `beginner`
- `intermediate`
- `expert`

### 4.2 Powers of Two

**Game slug:** `powers-of-two`

**Leaderboard categories:** One global leaderboard.

**Primary ranking metric:** `score`

**Ranking direction:** Descending (higher is better).

**Best-attempt selection:**

- Each player contributes their highest-scoring eligible attempt.

**Tie-breaking:**

1. Higher score.
2. Higher tile value.
3. Earlier submission (`created_at`).
4. Lower score UUID.

**Score data:**

```json
{
  "score": 4096,
  "tile": 512
}
```

**API endpoint:**

```http
GET /api/v1/games/powers-of-two/leaderboard
```

No difficulty parameter is supported.

---

## 5. API Contract

### Endpoint

```http
GET /api/v1/games/{game_slug}/leaderboard
```

The endpoint is public and does not require a player session.

### Query parameters

| Parameter | Type | Default | Constraints |
|---|---|---:|---|
| `game_slug` | string | Required | Must identify an active supported game |
| `difficulty` | string | None | Required for Proximity only |
| `limit` | integer | 10 | 1–100 |
| `offset` | integer | 0 | 0 or greater |

### Successful response

```json
{
  "game_slug": "proximity",
  "total_entries": 42,
  "limit": 10,
  "offset": 0,
  "entries": [
    {
      "rank": 1,
      "display_name": "Player0001",
      "data": {
        "difficulty": "beginner",
        "elapsed_seconds": 83
      },
      "created_at": "2026-11-05T02:00:00Z"
    }
  ]
}
```

### Response fields

| Field | Description |
|---|---|
| `game_slug` | Game associated with the leaderboard |
| `total_entries` | Number of distinct players with eligible entries |
| `limit` | Requested page size |
| `offset` | Number of entries skipped |
| `entries` | Leaderboard entries for the requested page |
| `rank` | Global rank before pagination |
| `display_name` | Player's public display name |
| `data` | Game-specific score data |
| `created_at` | Submission time of the selected best attempt |

### Pagination behavior

Pagination is applied after best-attempt selection and global ranking.

For example, if a leaderboard has 25 entries:

```http
GET /api/v1/games/powers-of-two/leaderboard?limit=10&offset=0
```

Returns ranks 1–10.

```http
GET /api/v1/games/powers-of-two/leaderboard?limit=10&offset=10
```

Returns ranks 11–20.

The second page must not restart ranking at 1.

`total_entries` always represents the complete number of eligible player entries, not the number of entries on the current page.

### Error responses

| Status | Meaning |
|---|---|
| `404` | Game does not exist or is inactive |
| `422` | Invalid difficulty, unsupported game/filter combination, or invalid pagination parameters |

---

## 6. Implementation Guidelines

Leaderboard selection and ranking belong in the backend.

The frontend must not determine a player's rank by sorting only the currently loaded page.

The backend is responsible for:

- Filtering expired and archived scores.
- Selecting the best eligible attempt per player.
- Applying game-specific ranking rules.
- Resolving ties deterministically.
- Calculating global ranks.
- Applying pagination.
- Returning the total number of eligible player entries.

PostgreSQL window functions are used to select best attempts and calculate global ranks.

Leaderboard retrieval must not modify, archive, or delete score records.

---

## 7. Adding Leaderboards for Future Games

Every new game that supports leaderboards must document its ranking rules before implementation.

Use the following template when adding a game.

### [Game Name]

**Game slug:** `[game-slug]`

**Leaderboard categories:** `[One global board / separate categories]`

**Primary ranking metric:** `[Metric]`

**Ranking direction:** `[Ascending / Descending]`

**Best-attempt selection:**

- `[Describe how a player's best attempt is selected.]`

**Tie-breaking:**

1. `[Primary tie-breaker]`
2. `[Secondary tie-breaker]`
3. Earlier submission (`created_at`), unless another rule is justified.
4. Lower score UUID as final deterministic tie-breaker.

**Score data:**

```json
{
  "example_metric": 100
}
```

**API endpoint:**

```http
GET /api/v1/games/[game-slug]/leaderboard
```

**Additional considerations:**

- `[Special eligibility requirements]`
- `[Additional query parameters]`
- `[Category-specific behavior]`
- `[Other game-specific rules]`

### Future game leaderboard registry

| Game | Slug | Categories | Primary metric | Direction | Status |
|---|---|---|---|---|---|
| Proximity | `proximity` | Difficulty | `elapsed_seconds` | Ascending | Implemented |
| Powers of Two | `powers-of-two` | Global | `score` | Descending | Implemented |
| Future game | `[game-slug]` | TBD | TBD | TBD | Planned |

Update this registry whenever a game gains leaderboard support.

---

## 8. Future Considerations

The current implementation intentionally keeps the leaderboard system simple.

Potential future improvements include:

- Friends-only and private leaderboards.
- Seasonal and event-based leaderboards.
- Time-period filters.
- Regional leaderboards.
- Cursor-based pagination for larger datasets.
- Leaderboard caching if query performance requires it.
- Anti-cheat and score verification mechanisms.
- Administrative score moderation.

These features should be introduced only when product requirements justify them.

The current system remains the source of truth for global, all-time game leaderboards.
