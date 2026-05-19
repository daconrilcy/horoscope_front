# Execution Brief

- Story key: `CS-190-seed-astral-dignity-reference-runtime`
- Objective: integrate astral dignity JSON seed data into backend DB migrations, models, repositories and seed flow.
- Boundaries: backend DB/reference seed code, SQLAlchemy models, repositories, targeted tests, CONDAMAD evidence.
- Non-goals: frontend changes, API endpoints, scoring calculation engine implementation.
- Preflight: preserve pre-existing JSON worktree changes and inspect existing seed/model patterns before writing backend code.
- Completion: migrations/models/repositories/seed/tests implemented, validations recorded, final evidence complete.
- Halt conditions: incompatible existing schema pattern, required destructive DB reset, or missing canonical seed path.
