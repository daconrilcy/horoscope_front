# Execution Brief - CS-017

## Primary objective

Decouple prediction API routers from the legacy `app.prediction` namespace while preserving public/runtime API behavior.

## Boundaries

- In scope: prediction API routers, canonical import ownership, API import guard, OpenAPI before/after evidence.
- Out of scope: frontend, database migrations, prediction engine migration, DTO moves beyond router needs.
- Behavior change allowed: no.

## Write rules

- Do not recreate `backend/app/prediction`.
- Do not add wrappers, aliases, re-exports, or fallback behavior for `app.prediction`.
- Keep route handlers as HTTP adapters; use domain/services owners for prediction responsibilities.
- Preserve unrelated worktree changes, including existing CS-018 artifacts.

## Done conditions

- `backend/app/api` has zero `app.prediction` imports.
- OpenAPI before/after snapshots are persisted.
- Daily prediction API, horoscope narration, architecture guard, Ruff, and full backend tests pass.
- `generated/10-final-evidence.md` and `_condamad/stories/story-status.md` are synchronized.
