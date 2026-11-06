# Arcade API Production Release Checklist

A repeatable procedure for releasing changes to the production Arcade API.

## 1. Before pushing

- [ ] Make changes in a GitHub Codespace or local development environment.
- [ ] Keep production credentials out of source code and committed files.
- [ ] Update tests when behavior changes.
- [ ] Update API documentation or README when the contract changes.
- [ ] Run the complete test suite.

```bash
pytest
```

- [ ] Check the Git diff for accidental secrets, local database URLs, or unrelated changes.

## 2. Database migration review

Determine whether the release changes the database schema.

### No schema changes

No production migration is required.

### Schema changes

- [ ] Generate the migration.
- [ ] Review the migration file.
- [ ] Test it against the development database.
- [ ] Commit the migration file.
- [ ] Confirm the migration is compatible with the currently deployed API.
- [ ] Prepare a rollback or recovery plan for risky changes.

Do not assume that rolling back an application deployment also rolls back database migrations.

## 3. Commit and CI

- [ ] Commit changes to the repository.
- [ ] Push to the configured deployment branch.
- [ ] Confirm GitHub Actions CI passes.
- [ ] If CI fails, inspect the failing job and fix the code or tests in the development environment.
- [ ] Do not deploy an unverified commit.

## 4. Render deployment

- [ ] Confirm Render is deploying the intended commit.
- [ ] Inspect build and runtime logs if deployment fails.
- [ ] Confirm the deployment becomes live.
- [ ] Confirm the health check passes.

With automatic deployment enabled, Render handles the normal build and deployment after a qualifying push.

## 5. Production database operations

Only perform these steps when applicable.

### Schema migration

From a trusted development environment, configure `DATABASE_URL` temporarily with the Neon production connection string.

Verify the destination without printing credentials:

```bash
python -c "import os; from sqlalchemy.engine import make_url; u = make_url(os.environ['DATABASE_URL']); print('Host:', u.host); print('Database:', u.database); print('Driver:', u.drivername)"
```

Then run:

```bash
alembic upgrade head
alembic current
```

Confirm the database is at the expected migration revision.

Unset the temporary variable afterward:

```bash
unset DATABASE_URL
```

Never commit the production connection string or put it in a normal development `.env` file.

### Game catalog

If the release adds or changes game catalog entries:

```bash
python scripts/seed_games.py
```

Run this only after confirming the production database URL is correctly configured.

The seed script must be idempotent.

## 6. Production smoke tests

- [ ] `GET /health` returns success.
- [ ] `GET /health/database` confirms database connectivity.
- [ ] `GET /api/v1/games` returns the expected game catalog.
- [ ] Relevant changed endpoints work.
- [ ] Authentication behaves as expected.
- [ ] Leaderboards return expected results.
- [ ] No unexpected errors appear in Render logs.

## 7. After release

- [ ] Confirm the live deployment corresponds to the intended commit.
- [ ] Record any migration revision applied.
- [ ] Update relevant documentation.
- [ ] Investigate unexpected errors before proceeding with further releases.

## Operational rules

- Render hosts the API.
- Neon stores persistent production database data.
- Render's service filesystem is not the production database.
- Application code changes are deployed through Git.
- Database schema changes are applied through Alembic.
- Catalog changes are applied through the seed script.
- Never assume a code rollback reverses database changes.
- Never run destructive database commands against production without a deliberate recovery plan.
