# CS-220 Final Evidence

## Summary

CS-220 migrates dignity and dominance runtime consumption toward `NatalResult.chart_objects` while preserving historical outputs and calculators.

## Baseline / before

- Inspected `chart_object_runtime_data.py`, `chart_object_runtime_builder.py`, dignity contracts/service, dominance contracts/engine and `natal_calculation.py`.
- Initial `git status --short`: clean.
- Existing state: dignity inputs were built directly from natal positions; dominance engine accepted `planet_positions`; chart objects had no dominance payload.

## Validation results

| Command | Result | Notes |
|---|---|---|
| `. .\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location` | PASS | Backend formatting/lint passed: 1522 files unchanged, all checks passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | PASS | 1 test passed; AC10 targeted contract evidence. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` | PASS | 9 tests passed; includes selector uniqueness and minimum-data validation. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` | PASS | 10 tests passed; includes selector/enricher dignity-before-dominance validation and runtime payload projection. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | PASS | 19 tests passed; includes nominal-code guard. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS | 22 historical scoring and golden-case tests passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/dignities` | PASS | 12 dignity package regression tests passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py` | PASS | 1 dominance integration test passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q` | PASS | Final rerun after strict brief-alignment fixes passed: 3000 passed, 1 skipped, 1177 deselected in 261.81s. |
| `. .\.venv\Scripts\Activate.ps1; Push-Location backend; python -c "from app.main import app; print(app.title)"; Pop-Location` | PASS | Backend app imports successfully and reports `horoscope-backend`. |

## Static guard evidence

- `rg -n "object_type ==|\\.object_type ==|ChartObjectType\\.PLANET|ChartObjectType\\.LUMINARY" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance`: zero hits.
- `rg -n "TRADITIONAL_PLANETS|planet_name ==|code in" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance`: classified hits only. `accidental_dignity_calculator.py:129` and `essential_dignity_calculator.py:58` are historical calculator filters; `planet_dominance_engine.py:55` iterates projected candidates; `planet_dominance_engine.py:267` scores luminary emphasis from reference data. None is CS-220 selector/projector eligibility.
- `rg -n "planet_positions" backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance`: zero hits.
- `rg -n "PlanetDignityPayloadBuilder|MoonDignityPayloadBuilder|MarsDominancePayloadBuilder|AngleDominancePayloadBuilder" backend/app backend/tests`: zero hits.
- `rg -n "interpretation|narrative|prompt|llm|meaning|psychological" backend/app/domain/astrology/runtime backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance`: classified hits only. `dominance/planet_dominance_engine.py:16` is a pre-existing dominant-aspect evaluator import; `runtime/aspect_modifiers.py`, `runtime/aspect_runtime_data.py`, `runtime/house_runtime_data.py` and `runtime/runtime_reference.py` are pre-existing interpretation/reference runtime surfaces outside CS-220 payloads; `chart_object_runtime_data.py:79` is the existing `supports_interpretation` capability flag. CS-220 dignity/dominance payloads do not expose narrative, prompt, meaning, psychological or LLM fields.

## Review/fix loop

- Accepted High finding: CS-220 payload breakdowns copied free-text `reason`. Fixed by removing `reason` from dignity/dominance runtime breakdown payloads and projectors.
- Accepted Medium finding: unknown result targets were silently ignored. Fixed by tracking consumed result codes and raising `ValueError` for unknown dignity/dominance result targets; tests added.
- Accepted Low finding: nominal-code guard did not cover equality/membership on code fields. Fixed by adding AST guard over CS-220 modules.
- Accepted High re-review finding: validation evidence did not prove venv activation. Fixed by rerunning Python/Ruff commands after `. .\.venv\Scripts\Activate.ps1` and updating evidence.
- Accepted Low re-review finding: AC10 targeted command was missing. Fixed by adding/running `test_natal_result_contract.py`.
- Accepted High re-review finding: nominal-code/list scan was absent and unclassified. Fixed by rerunning the scan and classifying all hits.
- Accepted Medium re-review finding: a bare historical `pytest -q` row remained in evidence. Fixed by removing it from validation evidence.
- Accepted High re-review finding: broad narrative-payload scan evidence did not match the validation plan. Fixed by rerunning the exact broad scan and classifying all hits.
- Accepted brief-alignment finding: selectors delegated uniqueness and minimum-data checks downstream. Fixed by adding selector-level validation without nominal-code branching.
- Accepted brief-alignment finding: dominance projected only a minimal historical input shape. Fixed by carrying classifications and runtime dignity/motion/visibility payloads in `DominanceChartObjectInput`, with selector and enricher guards requiring dignity payload before dominance when applicable.

## Scope proof

- No frontend files changed.
- No API, DB, migration or public JSON builder file changed.
- `NatalResult.dignities` and `NatalResult.dominant_planets` remain populated.
- `NatalResult.chart_objects` stays excluded from public schema/dump.
