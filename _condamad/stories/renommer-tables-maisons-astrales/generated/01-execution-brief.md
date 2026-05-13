# Execution Brief

- Story key: `renommer-tables-maisons-astrales`
- Objective: rename the active SQL tables `houses`, `house_profiles`, and `house_category_weights` to their astral canonical names.
- Boundaries: backend DB models, Alembic migrations, targeted backend tests, and `docs/tables-maisons-et-roles.md`.
- Non-goals: no frontend changes, no JSON payload field rename, no business logic rewrite, no full test suite.
- Preflight: preserve pre-existing dirty files; consult `AGENTS.md` and regression guardrails; keep Python commands inside the venv.
- Write rules: no compatibility alias, no duplicate active table path, no new dependency.
- Done: ACs mapped to code/test evidence, targeted checks pass, old names absent from active model/test expectations except historical migration/downgrade references.
- Halt: destructive DB rewrite beyond rename, unclear Alembic lineage, repeated targeted validation failure without safe fix.
