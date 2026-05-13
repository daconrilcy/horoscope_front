# Execution Brief

- Story key: `rename-planet-profiles-table`
- Objective: rename the SQL table `planet_profiles` to `astral_prediction_daily_planet_profiles`.
- Boundary: backend DB model, Alembic migration, schema/seed tests, active docs.
- Non-goals: no runtime DTO/function rename, no scoring behavior change, no frontend edits.
- Preflight: read `AGENTS.md`, `git status --short`, regression guardrails, relevant model/repository/migration/tests/docs.
- Write rules: smallest coherent delta, no compatibility table alias, preserve user changes, Python commands only after `.\.venv\Scripts\Activate.ps1`.
- Done: ACs traced, targeted tests/lint attempted, final evidence complete, story status updated.

