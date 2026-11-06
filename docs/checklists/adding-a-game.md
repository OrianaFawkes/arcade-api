# Adding a Game to Arcade API

A repeatable checklist for integrating a new game into the Arcade backend.

## 1. Define the game

- [ ] Choose a unique, lowercase, URL-friendly game slug.
- [ ] Choose the display name.
- [ ] Decide whether the game uses the existing `Game` and `Score` database models.
- [ ] Define the score payload and ranking rules.
- [ ] Decide whether the leaderboard is global or has separate categories (e.g. difficulty).

**Important:** Reuse the existing database structures whenever possible. A new game does not automatically require a new table.

## 2. Implement backend behavior

- [ ] Add the game's score validation.
- [ ] Add its ranking-value calculation.
- [ ] Define how ties are resolved.
- [ ] Define which scores are eligible for leaderboards.
- [ ] Add or update the relevant service.
- [ ] Add the API endpoint(s).
- [ ] Add the game to the game catalog seed script.

Keep game-specific rules in the appropriate game/service modules rather than scattering them throughout the API endpoints.

## 3. Database changes

Ask: does this game require a change to the database schema?

### If no

- [ ] Update `scripts/seed_games.py` with the new game.
- [ ] Ensure the seed operation is idempotent (running it again must not create duplicates).
- [ ] No Alembic migration is required.

### If yes

- [ ] Update the SQLAlchemy models.
- [ ] Generate an Alembic migration.
- [ ] Inspect the generated migration manually.
- [ ] Test the migration against the development database.
- [ ] Commit the migration file.
- [ ] Apply the migration to the production database during release.

Never modify production database tables manually as a substitute for a committed migration.

## 4. Tests

- [ ] Test valid score payloads.
- [ ] Test invalid and incomplete payloads.
- [ ] Test boundary values.
- [ ] Test ranking calculations.
- [ ] Test tie-breaking.
- [ ] Test duplicate submissions, if applicable.
- [ ] Test expired and archived score exclusion.
- [ ] Test inactive game behavior.
- [ ] Test leaderboard pagination and filtering.
- [ ] Test unauthenticated and invalid-session requests.
- [ ] Run the complete pytest suite.

## 5. Local verification

- [ ] Start the development database.
- [ ] Apply pending development migrations.
- [ ] Seed the game catalog.
- [ ] Start the API.
- [ ] Inspect the endpoint in Swagger.
- [ ] Submit a valid score.
- [ ] Verify the leaderboard response.

Typical commands:

```bash
docker compose up -d
alembic upgrade head
python scripts/seed_games.py
pytest
uvicorn main:app --reload
```

Use the project's documented Codespaces startup procedure if it differs.

## 6. Commit and deploy

- [ ] Commit the implementation, tests, and any migration.
- [ ] Push to the configured deployment branch.
- [ ] Wait for GitHub Actions CI to pass.
- [ ] Confirm Render deploys the intended commit.
- [ ] Inspect the deployment logs if it fails.
- [ ] Apply production migrations if the release includes schema changes.
- [ ] Run the seed script against production if a new catalog entry was added.
- [ ] Verify the deployed game catalog and endpoints.
- [ ] Perform a production smoke test.

## 7. Flutter integration

- [ ] Add the game to the Flutter API integration.
- [ ] Map the game's score payload to the backend contract.
- [ ] Handle API errors and expired sessions.
- [ ] Verify leaderboard sorting and pagination.
- [ ] Test against a development or staging API before production where available.

## Completion criteria

A game is considered integrated when:

- Its catalog entry is available.
- Its score validation and ranking rules are tested.
- Its API endpoints work.
- Its leaderboard returns the expected results.
- Its Flutter client can submit and retrieve scores.
- Its behavior is documented where necessary.
