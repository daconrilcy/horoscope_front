# Dev Log

## Preflight

- Repository root: `C:/dev/horoscope_front`
- Current date: 2026-05-15
- Initial `git status --short`: worktree already dirty with CS-172 runtime files, story registry files, natal runtime files, and untracked capsule/runtime repository files.
- AGENTS.md considered: root `AGENTS.md`.
- Regression guardrails considered: `RG-091` to `RG-107`; `RG-107` added for this story.

## Search evidence

- `ReferenceDataService.get_active_reference_data|reference_data: dict` in natal/domain runtime: zero hits.
- Forbidden DB-backed constants in natal/domain runtime: zero hits.
- `UNKNOWN_SIGN|EXACT_ORB_DEG|TIGHT_RATIO|MODERATE_RATIO` in natal/domain runtime: zero hits.
- SwissEph simplified fallback patterns in natal/domain runtime: zero hits.
- prediction/LLM imports in `backend/app/domain/astrology`: zero hits.

## Implementation notes

- Added immutable runtime reference contracts and exported them through `app.domain.astrology.runtime`.
- Added infra mapper/repository and blocking integrity validation.
- Switched natal service/domain to `AstrologyRuntimeReference`.
- Seeded canonical house systems in the reference seed path.
- Removed `phase="unknown"` sentinel from aspect runtime builder.
- Replaced forbidden aspect strength threshold constant names with injectable immutable threshold contract.
- Migrated tests from partial dict fixtures to typed runtime reference factory.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `ruff format .` | PASS | Run from `backend` after venv activation. |
| `ruff check .` | PASS | Run from `backend` after venv activation. |
| `pytest -q tests/unit/domain/astrology/test_runtime_ref.py tests/unit/domain/astrology/test_natal_result_contract.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py app/tests/unit/test_natal_calculation_service.py` | PASS | 37 passed. |
| `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_runtime_ref.py tests/unit/domain/astrology/test_natal_result_contract.py` | PASS | 12 passed after review fixes. |
| `pytest -q tests/unit/domain/astrology app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_reference_data_service.py app/tests/unit/test_scope_separation_imports.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_runtime_reference_guard.py` | PASS | 100 passed after review fixes. |
| `pytest -q` | FAIL | Completed after ~14 minutes; broader suite still fails outside the targeted CS-172 subset. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-172-big-bang-reference-runtime-astrology/00-story.md` | PASS | Story validation passed. |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` | PASS | Process started during bounded smoke and was stopped. |

## Issues encountered

- Generated traceability had 13 malformed AC rows; corrected to the 12 real ACs.
- Full backend pytest did not complete inside the 10 minute command budget.

## Decisions made

- Did not add a compatibility path for dict-based runtime data.
- Did not keep the legacy `ReferenceDataService` cache expectation in natal tests; test now documents direct runtime reference loading.
- Did not add frontend validation because `frontend/**` is untouched.

## Final `git status --short`

Recorded in `10-final-evidence.md`.
