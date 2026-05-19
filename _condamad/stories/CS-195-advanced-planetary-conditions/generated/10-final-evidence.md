# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: completed
- Story key: CS-195-advanced-planetary-conditions
- Source story: `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md`
- Capsule path: `_condamad/stories/CS-195-advanced-planetary-conditions`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` was already modified.
- AGENTS considered: root `AGENTS.md`.
- Dependencies: CS-192, CS-193 and CS-194 were marked `done`.
- Frontend: not touched.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Pre-existing user-modified source. |
| `generated/01-execution-brief.md` | yes | yes | PASS | CS-195 specific. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC15 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Backend-only scope. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Targeted commands and scans listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-122 mapped. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Migration, models, seed JSON and seed service for `astral_advanced_condition_*`. | Runtime repository and migration tests passed. | PASS | |
| AC2 | Runtime contracts, mapper, repository loaders and integrity validation. | `test_astrology_runtime_reference_repository.py` passed. | PASS | |
| AC3 | `AdvancedPlanetaryCondition`, `PlanetConditionAxisImpact`. | Immutability test passed. | PASS | |
| AC4 | Mutual reception calculator. | `test_mutual_reception_calculator.py` passed. | PASS | |
| AC5 | Hayz calculator from real accidental dignity facts. | `test_hayz_calculator.py`, `test_accidental_dignity_calculator.py` and natal pipeline test passed. | PASS | Review finding fixed. |
| AC6 | Speed classifier from real accidental dignity facts. | `test_speed_classifier.py` and `test_accidental_dignity_calculator.py` passed. | PASS | Review finding fixed. |
| AC7 | Heliacal/orientation calculator from real accidental dignity facts plus natal solar facts. | `test_heliacal_conditions.py`, `test_accidental_dignity_calculator.py` and natal pipeline test passed. | PASS | Review finding fixed. |
| AC8 | Aspect condition detector with condition-compatible targets. | `test_besiegement_detector.py` and natal pipeline test passed. | PASS | Review finding fixed. |
| AC9 | Advanced engine enriches profiles with advanced breakdown/facts. | `test_advanced_condition_engine.py` passed. | PASS | |
| AC10 | Natal orchestration builds signals after profile enrichment. | Targeted suite passed. | PASS | |
| AC11 | Dominance consumes advanced `ranking_weight`. | `test_dominance_integration.py` passed. | PASS | |
| AC12 | JSON helper projects `advanced_conditions`. | `test_chart_json_builder.py` and serializer guard passed. | PASS | |
| AC13 | Guard blocks forbidden imports/maps/narration. | Guard test and RG-122 scans passed. | PASS | |
| AC14 | Deferred techniques absent. | Deferred technique scan returned zero hits. | PASS | |
| AC15 | Public contract stable except authorized additions. | Full `pytest -q`, `ruff format .`, `ruff check .`, `git diff --check` passed. | PASS | |

## Files changed

See `git status --short` for full list. Main implementation areas:

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_*.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/services/chart/json_builder.py`
- `docs/db_seeder/astrology/astral_advanced_condition_*.json`
- Targeted backend tests for CS-195.

## Files deleted

- None.

## Tests added or updated

- Added calculator, engine and dominance tests under `backend/tests/unit/domain/astrology`.
- Updated runtime repository, runtime guard, JSON builder and natal contract tests.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_speed_classifier.py backend/tests/unit/domain/astrology/test_heliacal_conditions.py backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_dominance_integration.py` | repo root | PASS | 0 | 8 passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | repo root | PASS | 0 | 53 passed. |
| `pytest -q backend/app/tests/unit/test_chart_result_service.py backend/app/tests/integration/test_reference_data_migrations.py` | repo root | PASS | 0 | 6 passed, 5 deselected. |
| `ruff format .` | repo root | PASS | 0 | Formatting applied, final rerun unchanged. |
| `ruff check .` | repo root | PASS | 0 | All checks passed. |
| `pytest -q` | repo root | PASS | 0 | 2725 passed, 1 skipped, 1177 deselected. |
| RG-122 import scan | repo root | PASS | 1 | Zero hits. |
| RG-122 narration scan | repo root | PASS | 1 | Zero hits. |
| RG-122 local-map scan | repo root | PASS | 1 | Zero hits. |
| RG-122 deferred-technique scan | repo root | PASS | 1 | Zero hits. |
| `git diff --check` | repo root | PASS | 0 | Only line-ending warnings; no whitespace errors. |
| `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_heliacal_conditions.py backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_speed_classifier.py backend/tests/unit/domain/astrology/test_dominance_integration.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | repo root | PASS | 0 | Review/fix rerun: 30 passed. |
| `pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py backend/app/tests/unit/test_dignity_reference_seed.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | repo root | PASS | 0 | Regression rerun after full-suite findings: 22 passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` | repo root | PASS | 0 | Review/fix iteration 2: 35 passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_heliacal_conditions.py backend/tests/unit/domain/astrology/test_speed_classifier.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_dominance_integration.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py backend/app/tests/unit/test_dignity_reference_seed.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | PASS | 0 | Final targeted CS-195 validation: 77 passed, 5 deselected. |
| `pytest -q` | repo root | PASS | 0 | Final full suite: 2726 passed, 1 skipped, 1177 deselected. |
| `ruff format --check .` | repo root | PASS | 0 | 1459 files already formatted. |
| `ruff check .` | repo root | PASS | 0 | All checks passed. |
| `git diff --check` | repo root | PASS | 0 | Only line-ending warnings; no whitespace errors. |
| RG-122 import scan | repo root | PASS | 1 | Zero hits. |
| RG-122 narration scan | repo root | PASS | 1 | Zero hits. |
| RG-122 local-map scan | repo root | PASS | 1 | Zero hits. |
| RG-122 deferred-technique scan | repo root | PASS | 1 | Zero hits. |
| `uvicorn app.main:app --host 127.0.0.1 --port 8019` then `GET /docs` | `backend` | PASS | 0 | Local API startup probe returned HTTP 200; process stopped. |

## Review loop

- Subagents used: no.
- Iterations: 2 review/fix iterations, ending with a fresh CLEAN review.
- Fixed findings:
  - Real runtime pipeline now evaluates CS-195 accidental source schemas and weights.
  - Aspect relational targets now match the detected condition.
  - Public runtime weight contract exposes `visibility_weight`.
  - Payload evidence now compares the same natal fixture before/after the authorized addition.
  - Aspect conditions no longer recreate benefic/malefic planet sets locally; they resolve natures from the DB-backed runtime `PlanetNatureReferenceSet`.
- Rejected findings: none.

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- `advanced_conditions/**` has no DB/API/service/prediction imports.
- No forbidden advanced local map names remain.
- Planet nature assignments are loaded from `astral_planet_natures.planet_codes_json` into the typed runtime and guarded against local set reintroduction.
- No serializer-side `AdvancedConditionEngine` call exists.
- No frontend files were changed.

## Diff review

- Scope is backend astrology runtime/domain/serialization, seed data, migration, tests and capsule evidence.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` was dirty before implementation and remains classified as pre-existing user change.
- No generated lock/cache files were added.

## Final worktree status

- Expected story changes plus pre-existing modified `00-story.md`.

## Remaining risks

- None identified after validation.

## Suggested reviewer focus

- Review that advanced calculators correctly rely on existing dignity/runtime facts rather than introducing duplicate astrology reference vocabularies.
