# Dev Log

## Preflight

- Initial `git status --short`: `_condamad/run-state.json` was already modified before implementation.
- Story/status/brief alignment: CS-428 row matched the requested story path and source brief.
- Capsule was missing generated files; repaired with `condamad_prepare.py --repair-generated-only` and validated.
- An initial ambiguous prepare attempt created `_condamad/stories/cs-428/`; it was removed after path verification.

## Search evidence

- Targeted guardrails resolved: RG-011, RG-150, RG-152, RG-155, RG-157, RG-168.
- CS-427 product contract dimensions found under `backend/app/domain/theme_natal/product_contract.py`.
- Legacy `UserNatalInterpretationModel` retained only as out-of-scope historical persistence.

## Implementation notes

- Added one canonical slot model and one canonical run model.
- Public visibility is owned by slot status `accepted`; raw/parsed LLM traces remain on runs.
- SQLite idempotence is enforced by unique indexes and explicit `IntegrityError` recovery.
- Quota integration is exposed through `accepted_now` and `consume_quota_after_publication`.

## Commands run

See `generated/06-validation-plan.md` for the command list and results.

## Issues encountered

- `pytest tests/integration ...` without `--long` deselected integration tests by repository policy; rerun with `--long` passed.
- First temp SQLite Alembic proof hit a Windows file-lock cleanup error after upgrade; rerun with `engine.dispose()` passed.

## Decisions made

- No frontend, provider call, prompt, API cutover, mass migration, or legacy table deletion was introduced.
- `source_generation_run_id` is stored as an integer pointer without a circular FK to avoid cross-table DDL ordering issues.

## Final `git status --short`

- Recorded in `generated/10-final-evidence.md` after final consistency gate.
