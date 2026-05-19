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
- Current repository diff and untracked CS-195 files.

## Diff summary

- Added pure advanced condition domain under
  `backend/app/domain/astrology/advanced_conditions/**`.
- Added runtime contracts and loaders for `astral_advanced_condition_*`.
- Added DB model/migration/seed sync for advanced condition references.
- Added DB-backed planet nature assignment payload on `astral_planet_natures`
  so aspect conditions do not recreate benefic/malefic planet sets locally.
- Integrated `NatalResult.advanced_conditions`, enriched condition profiles,
  dominance scoring via advanced `ranking_weight`, and strict chart JSON
  projection.
- Added focused tests and RG-122 architecture guards.

## Findings

### CR-001 High - Aspect conditions recreated benefic/malefic planet sets locally

- Bucket: patch
- Location:
  `backend/app/domain/astrology/advanced_conditions/aspect_condition_detector.py`
- Source layer: acceptance / no-legacy / regression guardrail
- Evidence: the detector mapped Venus/Jupiter and Mars/Saturn directly in
  `_planet_nature`, while CS-195 and `RG-122` require planet natures to come
  from runtime references and forbid local benefic/malefic maps.
- Impact: a future reference-data change would not affect aspect conditions,
  and the advanced condition engine would own a second active vocabulary.
- Fix: accepted and implemented. `astral_planet_natures` now carries
  `planet_codes_json`, the runtime exposes `PlanetNatureReferenceSet`, and
  `AspectConditionDetector` resolves partner natures from
  `runtime_reference.planet_natures`.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1-AC2 | PASS | Migration/model/seed/repository/runtime tests pass, including planet nature assignment loading. |
| AC3-AC8 | PASS | Advanced contracts and calculators are covered by targeted domain tests. |
| AC9-AC10 | PASS | Profile enrichment and signal ordering are covered by advanced engine and natal contract tests. |
| AC11 | PASS | Dominance integration test covers advanced `ranking_weight`. |
| AC12 | PASS | Chart JSON test covers strict projection from `NatalResult.advanced_conditions`. |
| AC13 | PASS | Runtime guard now blocks forbidden imports, maps, narration and local planet nature sets. |
| AC14 | PASS | Deferred technique scan returned zero hits. |
| AC15 | PASS | Full pytest, ruff, diff check and local API startup passed. |

## Validation audit

- `pytest -q ...` targeted CS-195 suite: PASS, 77 passed, 5 deselected.
- `pytest -q`: PASS, 2726 passed, 1 skipped, 1177 deselected.
- `ruff format --check .`: PASS, 1459 files already formatted.
- `ruff check .`: PASS, all checks passed.
- `git diff --check`: PASS, only CRLF normalization warnings.
- RG-122 import scan: PASS, zero hits.
- RG-122 narration scan: PASS, zero hits.
- RG-122 local advanced map scan: PASS, zero hits.
- RG-122 deferred technique scan: PASS, zero hits.
- Local API startup probe: PASS, `GET /docs` returned HTTP 200 on
  `127.0.0.1:8019`; process stopped.

## DRY / No Legacy audit

- No DB/API/service/prediction/LLM import exists in `advanced_conditions/**`.
- No local advanced type/weight map names exist.
- The prior local benefic/malefic planet set was removed and guarded.
- `json_builder.py` projects existing natal result data and does not instantiate
  `AdvancedConditionEngine` or `PlanetDominanceEngine`.
- Frontend remains untouched, as required.

## Commands run by reviewer

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

```powershell
pytest -q backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_besiegement_detector.py backend/tests/unit/domain/astrology/test_heliacal_conditions.py backend/tests/unit/domain/astrology/test_speed_classifier.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_dominance_integration.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py backend/app/tests/unit/test_dignity_reference_seed.py backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q
ruff format .
ruff format --check .
ruff check .
git diff --check
```

## Residual risks

- None identified.

## Verdict

CLEAN
