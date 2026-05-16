# CONDAMAD Code Review

## Review target

- Story: `CS-181-supprimer-constantes-astrologiques-hardcodees`
- Capsule: `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees`
- Closure class: full-closure
- Final review date: 2026-05-17

## Inputs reviewed

- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/generated/06-validation-plan.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/generated/10-final-evidence.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/guard-evidence.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-before.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-after.md`
- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/astrology-constant-exceptions.md`
- `_condamad/stories/regression-guardrails.md`
- Git diff for backend implementation, tests, guardrails and story evidence.

## Diff summary

- Removed the natal service legacy mock fallback that rebuilt astrology references locally.
- Added `backend/app/domain/prediction/aspect_reference.py` to resolve major aspects and aspect orbs from the loaded runtime context.
- Replaced local daily aspect mappings in event detection, enriched events, transit/intraday builders and natal aspect orchestration.
- Extended prediction reference DTO/loading with aspect `angle` and `family_code`.
- Added and updated backend tests/guards to require runtime-backed aspect profiles and orb rules.
- Added `RG-112` and closed story status to `done`.

## Review layers

- Diff integrity: PASS. Changed files are within CS-181 backend/story scope; no frontend, dependency, migration, requirements or secret changes found.
- Acceptance audit: PASS. AC1-AC7 have code and validation evidence in `generated/10-final-evidence.md`.
- Validation audit: PASS. Required lint, targeted tests, scans and `git diff --check` were run after venv activation where Python commands were involved.
- DRY / No Legacy audit: PASS. Local DB-backed aspect mappings and natal fallback reconstruction were removed; remaining `_STAR_DATA` and `_ASPECT_TONES` are exact classified exceptions.
- Edge/security/data audit: PASS. Missing runtime aspect/orb data now fails explicitly through `PredictionContextError`; no API/auth/data persistence surface changed.

## Findings

No remaining actionable findings.

### Resolved during review/fix iteration

#### CR-1 High - Runtime aspect closure was not validated by current tests

- Bucket: patch
- Location: `backend/app/tests/unit/test_intraday_activation_v3.py`, `backend/app/tests/unit/test_engine_orchestrator.py`
- Source layer: validation / acceptance
- Evidence: first reviewer run failed 22 targeted tests because fixtures lacked `family_code`, `angle` or `aspect_orb_rules` required by the new runtime contract.
- Impact: CS-181 could not be accepted because the validation suite contradicted the final evidence.
- Fix applied: updated test fixtures with complete `AspectProfileData` and explicit `AspectOrbRuleData`; rerun result was 113 passed.

#### CR-2 Medium - Shared aspect orb resolver selected `modern` internally

- Bucket: patch
- Location: `backend/app/domain/prediction/aspect_reference.py`
- Source layer: no-legacy / acceptance
- Evidence: the first implementation computed the active aspect-system chain from a local `configured = "modern"` inside the shared helper.
- Impact: the helper could become a hidden configuration fallback instead of using the loaded ruleset context.
- Fix applied: `aspect_orbs_by_code()` now receives `LoadedPredictionContext` and resolves `aspect_system` / `aspect_school` from `ruleset_context.parameters`.

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | Before/after inventory and exception register present; runtime/reference guard tests passed. |
| AC2 | PASS | Natal fallback helper removed; natal forbidden-symbol scan zero-hit. |
| AC3 | PASS | Daily aspect mappings replaced by runtime resolver; targeted prediction tests passed. |
| AC4 | PASS | Exceptions are exact symbols, no wildcard/folder exception. |
| AC5 | PASS | `app/domain/astrology` import boundary test and scan passed. |
| AC6 | PASS | AST guard blocks `ASPECTS_V1`, `ASPECTS` and literal aspect mapping reintroduction. |
| AC7 | PASS | `ruff format .`, `ruff check .`, targeted pytest suite and scans passed. |

## Validation audit

| Command | Result |
|---|---|
| `ruff format .` | PASS |
| `ruff check . --fix` then `ruff check .` | PASS |
| `pytest -q app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_transit_signal_v3.py app/tests/unit/test_event_detector.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py app/tests/unit/test_engine_orchestrator.py` | PASS, 113 passed |
| Natal forbidden-symbol scan | PASS, zero hit |
| Aspect forbidden-symbol scan | PASS, only classified `_STAR_DATA` / `_ASPECT_TONES` hits |
| Astrology boundary scan | PASS, zero hit |
| `git diff --check` | PASS |
| `condamad_story_validate.py 00-story.md` | PASS |
| `condamad_story_lint.py --strict 00-story.md` | PASS |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8017` | PASS, smoke start then stopped |

## Residual risks

Aucun risque restant identifié.

## Verdict

CLEAN
