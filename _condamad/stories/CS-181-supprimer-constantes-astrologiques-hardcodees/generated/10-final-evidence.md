# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Final status: done
- Story key: `CS-181-supprimer-constantes-astrologiques-hardcodees`
- Source story: `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md`
- Capsule path: `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: existing CONDAMAD/audit dirty files plus new CS-181 capsule.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, `docs/recherches astro/2026-05-16-audit-chaine-calcul-theme-natal.md`, CS-181 story directory.
- AGENTS.md considered: root `AGENTS.md`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Created. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Created, pending final validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `hardcoded-astrology-before.md`, `hardcoded-astrology-after.md`, `astrology-constant-exceptions.md`. | Runtime/reference guards and scans executed. | PASS | Before/after inventory complete. |
| AC2 | `backend/app/services/natal/calculation_service.py` fallback removed. | Targeted tests and natal scan zero-hit. | PASS | No `_legacy_payload_for_mock_db` or local `sign_rulerships` fallback remains. |
| AC3 | Runtime aspect resolver and consumers updated. | Prediction/event/enriched/V3 targeted tests passed; aspect scan clean except classified display exceptions. | PASS | `ASPECTS_V1` and `ASPECTS = {` removed from runtime. |
| AC4 | Exception register created with exact symbols. | `test_astrology_reference_catalog_guard.py` passed; exception register reviewed. | PASS | No wildcard or folder exception. |
| AC5 | No astrology->prediction import introduced. | Boundary test and scan zero-hit. | PASS | `domain/astrology` remains independent. |
| AC6 | Guard added in `test_astrology_reference_catalog_guard.py`. | Reference/runtime guard tests passed. | PASS | Reintroduction of local daily aspect mappings is blocked. |
| AC7 | No dependency change. | `ruff format .`, `ruff check .`, targeted pytest suite and `git diff --check` passed. | PASS | Python commands ran after venv activation. |

## Files changed

- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/**`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- Backend unit tests and guards touched by the story.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_event_detector.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_natal_calculation_service.py` | `backend` | PASS | 0 | 54 passed. |
| `pytest -q app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_transit_signal_v3.py app/tests/unit/test_event_detector.py app/tests/unit/test_intraday_activation_v3.py app/tests/unit/test_impulse_signal_v3.py app/tests/unit/test_engine_orchestrator.py` | `backend` | FAIL then PASS | 1 then 0 | First review run exposed 22 failing tests; after fixes, 113 passed. |
| `ruff format .` | `backend` | PASS | 0 | 1390 files left unchanged after fixes. |
| `ruff check . --fix` then `ruff check .` | `backend` | PASS | 0 | Import ordering fixed, all checks passed. |
| Natal forbidden-symbol scan | `backend` | PASS | 1 | Zero hits expected. |
| Aspect forbidden-symbol scan | `backend` | PASS | 0 | Only `_STAR_DATA` and `_ASPECT_TONES` classified exceptions remain. |
| Astrology boundary scan | `backend` | PASS | 1 | Zero hits expected. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` | repo root | PASS | 0 | Story validation contract OK. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` | repo root | PASS | 0 | Story lint strict OK. |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8017` | `backend` | PASS | 0 | Backend started locally, then was stopped after smoke start. |

## Review loop

- Iteration 1 verdict: `BLOCKING`
  - Findings: missing final validation evidence; 22 targeted tests failed because V3 fixtures did not provide complete runtime aspect profiles/orb rules; `aspect_reference.py` selected `modern` internally instead of reading the loaded ruleset context.
- Fixes applied:
  - `aspect_orbs_by_code()` now receives `LoadedPredictionContext` and resolves the active aspect system from ruleset parameters.
  - V3/orchestrator test fixtures now provide complete `AspectProfileData` and `AspectOrbRuleData`.
  - Evidence and story status were updated after validation.
- Iteration 2 verdict: `CLEAN`

## Remaining risks

- Aucun risque restant identifié.
