# Final Evidence - CS-234-enrichir-profils-structurels-signes-db

## Story status

- Validation outcome: targeted PASS, full-suite PASS_WITH_LIMITATIONS.
- Ready for review: yes.
- Story key: `CS-234-enrichir-profils-structurels-signes-db`.
- Source story: `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/00-story.md`.
- Capsule path: `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db`.

## Summary

CS-234 enriches `astral_sign_profiles` with DB-backed structural sign classifications:

- seasonal quadrant;
- fertility class;
- voice class;
- form class.

The implementation keeps `keywords_json` and `shadow_keywords_json` editorial-only and does not change runtime natal payloads, API routes or frontend files.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: repository was dirty before implementation with unrelated `.gitignore`, `_condamad/codex-runs/**`, skill folders and CS-235/CS-236 artifacts.
- AGENTS.md considered: repository root `AGENTS.md`.
- Capsule generated: yes; helper generated a duplicate inferred capsule path, then generated files were copied into the requested CS-234 capsule and the duplicate helper capsule was removed.
- Capsule validation: `condamad_validate.py` PASS before implementation.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Updated to target story key. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Touched and forbidden files recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Targeted commands recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generic guardrails retained. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed for review. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | SQLAlchemy model and Alembic migration add four non-null profile FKs and four taxonomy tables. | Targeted pytest. | PASS | |
| AC2 | `astral_structural_reference_catalog.json` and seed service define all twelve rows. | Targeted pytest and `evidence/seed-check.txt`. | PASS | |
| AC3 | Expected code sets persisted in taxonomy seed data. | Integration tests assert counts and joined code matrix. | PASS | |
| AC4 | Structural attributes load from structural catalog; keyword JSON remains editorial source only. | Integration test keeps keyword assertions separate from structural joins. | PASS | |
| AC5 | No production change under `backend/app/domain/astrology`. | Exact-word `rg` scan found no local mapping. | PASS | |
| AC6 | No production change under `backend/app/services/natal`. | Exact-word `rg` scan found no local mapping. | PASS | |
| AC7 | Migration extends astral head without recreating old tables. | Integration tests keep `signs`, `sign_rulerships`, `astral_sign_rulerships` absent. | PASS | |
| AC8 | Evidence files persisted under `evidence/**`. | Python existence check and capsule validation. | PASS | |
| AC9 | Sect/gender source decision recorded. | `rg "sect|gender"` source scan reviewed. | PASS | |

## Files changed

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/migrations/versions/20260523_0137_enrich_astral_sign_profiles.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json`
- `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/generated/**`
- `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None from the target implementation.
- Removed duplicate helper-generated capsule directory `story-cs-234-enrichir-profils-structurels-signes-db-enrichir-profils-structurels-signes-db`.

## Tests added or updated

- Integration migration test now asserts new taxonomy tables, non-null FKs and twelve sign classification mappings.
- Unit repository/model test now asserts sign profile structural FK contract.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-234-enrichir-profils-structurels-signes-db` | repo root | PASS | 0 | Capsule structure valid before implementation. |
| `.venv\Scripts\Activate.ps1; cd backend; ruff format <modified Python files>` | repo root | PASS | 0 | Python files formatted. |
| `.venv\Scripts\Activate.ps1; cd backend; ruff check <modified Python files>` | repo root | PASS | 0 | Scoped lint clean. |
| `.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q app\tests\integration\test_reference_data_migrations.py app\tests\unit\test_prediction_reference_repository.py` | repo root | PASS | 0 | 32 passed, 5 deselected. |
| `rg -n "\b(seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute)\b" backend\app\domain\astrology backend\app\services\natal -g "*.py"` | repo root | PASS | 1 | No matches; exit 1 expected for absence scan. |
| Brief raw no-boundary mapping scan | repo root | REVIEWED | 0 | Only pre-existing non-mapping `muted signal` occurrence found. |
| `rg -n "sect|gender" docs\"recherches astro" docs\db_seeder\astrology` | repo root | PASS | 0 | Source ownership found and recorded. |
| `.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | PASS | 0 | Backend lint clean. |
| `.venv\Scripts\Activate.ps1; cd backend; python -B -c "<evidence existence check>"` | repo root | PASS | 0 | Required evidence files exist. |
| `git diff --check -- <CS-234 touched files>` | repo root | PASS | 0 | No whitespace errors; Git emitted line-ending warnings. |

## Commands skipped or blocked

- App server start: NOT RUN. Reason: backend DB schema/seed story with no route, frontend or runtime API surface; targeted migration and seed tests cover the changed behavior.
- Full backend suite: RUN BUT NOT GREEN. `.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q` failed with 1 unrelated existing failure in `app/tests/unit/test_aspect_ruleset_schema.py::TestAspectRulesetSchemaValidation::test_aspect_missing_default_orb_deg_raises`.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback or duplicate active path added.
- New production structural values are sourced from `astral_structural_reference_catalog.json`, not from domain/natal mappings.
- Exact-word mapping scan over `backend/app/domain/astrology` and `backend/app/services/natal` passed with no matches.
- Public JSON, frontend and natal runtime surfaces were not changed.

## Final worktree status

- Final `git status --short` remains dirty because the repository had many unrelated pre-existing changes.
- CS-234 changed files are listed above.

## Diff review

- `git diff --stat`: reviewed for CS-234 touched tracked files.
- `git diff --check`: PASS for CS-234 touched tracked files, with line-ending warnings only.

## Remaining risks

- Full backend suite still has one unrelated failing test outside this story surface.
- The exact traditional assignment of fertility/voice/form classifications should be reviewed by a domain reviewer because the story required persistence and source decision, not runtime interpretation.

## Suggested reviewer focus

- Verify taxonomy naming and sign classification assignments in `astral_structural_reference_catalog.json`.
- Review Alembic downgrade/upgrade behavior for SQLite and production DB.
- Confirm no runtime/public contract change is desired in CS-234.
