# CONDAMAD Code Review - CS-195

## Review target

- Story: `CS-195-advanced-planetary-conditions`
- Capsule: `_condamad/stories/CS-195-advanced-planetary-conditions`
- Surface reviewed: backend astrology runtime references, advanced condition
  calculators, natal integration, dominance integration, chart JSON projection,
  reference seed data, migration, tests and CS-195 evidence.
- Frontend surface: none.

## Inputs reviewed

- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md`
- `_condamad/stories/CS-195-advanced-planetary-conditions/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-195-advanced-planetary-conditions/generated/06-validation-plan.md`
- `_condamad/stories/CS-195-advanced-planetary-conditions/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-195-advanced-planetary-conditions/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`, especially `RG-122`
- Current repository diff after review-fix iteration 3.

## Diff summary

- Replaced the dynamic `visibility_weight` compatibility alias on
  `AdvancedConditionWeightReferenceData` with an explicit runtime field.
- Updated `AdvancedConditionEngine` and the runtime mapper to consume
  `visibility_weight` and `ranking_weight` directly.
- Updated the repository test to prove the explicit advanced runtime contract.
- Tightened `test_astrology_prediction_boundary.py` with an exact CS-195
  exception for `visibility_weight` only in the advanced runtime contract files.

## Findings

None remaining after the fresh review pass.

## Resolved during this loop

### CR-005 Medium - Advanced runtime visibility axis was hidden behind an alias

- Bucket: patch
- Location: `backend/app/domain/astrology/runtime/runtime_reference.py`
- Source layer: acceptance / no-legacy / validation
- Evidence: CS-195 and the seed contract define `visibility_weight` as a
  required advanced weight axis, but the runtime dataclass stored
  `condition_visibility` and exposed `visibility_weight` only through
  `__getattr__`.
- Impact: the public runtime contract was less explicit than the DB-backed
  story contract and the guard was satisfied through string composition.
- Fix: accepted and implemented. The dataclass now has an explicit
  `visibility_weight` field, the mapper and engine use direct attributes, and
  the architecture guard allows that symbol only in the exact CS-195 runtime
  contract files.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1-AC2 | PASS | Migration/model/seed/repository/runtime tests pass, including explicit `visibility_weight`. |
| AC3-AC8 | PASS | Advanced contracts and calculators are covered by targeted domain tests. |
| AC9-AC10 | PASS | Profile enrichment and signal ordering are covered by advanced engine and natal contract tests. |
| AC11 | PASS | Dominance integration test covers advanced `ranking_weight`. |
| AC12 | PASS | Chart JSON test covers strict projection from `NatalResult.advanced_conditions`. |
| AC13 | PASS | Runtime guard and prediction-boundary guard pass with exact CS-195 exception only. |
| AC14 | PASS | Deferred technique scan returned zero hits. |
| AC15 | PASS | Full pytest, ruff, diff check and local API startup passed. |

## Validation audit

- `pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`: PASS, 20 passed.
- `ruff format .`: PASS, 1460 files left unchanged.
- `ruff check .`: PASS, all checks passed.
- Final targeted CS-195 suite plus prediction-boundary guard: PASS, 80 passed, 5 deselected.
- `pytest -q`: PASS, 2727 passed, 1 skipped, 1177 deselected.
- RG-122 import scan: PASS, zero hits.
- RG-122 narration scan: PASS, zero hits.
- RG-122 local advanced map scan: PASS, zero hits.
- RG-122 deferred technique scan: PASS, zero hits.
- `git diff --check`: PASS, only CRLF normalization warnings.
- Local API startup probe: PASS, `GET /docs` returned HTTP 200 on
  `127.0.0.1:8019`; process stopped.

## DRY / No Legacy audit

- No DB/API/service/prediction/LLM import exists in `advanced_conditions/**`.
- No local advanced type/weight map names exist.
- `visibility_weight` is explicit only where CS-195 requires the advanced
  runtime contract; the broader astrology/prediction boundary remains guarded.
- `json_builder.py` projects existing natal result data and does not instantiate
  `AdvancedConditionEngine` or `PlanetDominanceEngine`.
- Frontend remains untouched, as required.

## Commands run by reviewer

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

```powershell
pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
ruff format .
ruff check .
pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_heliacal_conditions.py backend/tests/unit/domain/astrology/test_speed_classifier.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_dominance_integration.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py backend/app/tests/unit/test_dignity_reference_seed.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/app/tests/unit/test_astrology_prediction_boundary.py
pytest -q
git diff --check
```

## Residual risks

None identified.

## Verdict

CLEAN
