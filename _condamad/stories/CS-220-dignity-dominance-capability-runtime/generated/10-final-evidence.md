# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-220-dignity-dominance-capability-runtime
- Source story: `_condamad/stories/CS-220-dignity-dominance-capability-runtime/00-story.md`
- Capsule path: `_condamad/stories/CS-220-dignity-dominance-capability-runtime`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Regression guardrails considered: `RG-135`, `RG-141` to `RG-147`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Added. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC24. |
| `generated/04-target-files.md` | yes | yes | PASS | Added. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Added. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Added. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

All AC1-AC24 are implemented by the runtime contract, new dignity/dominance chart-object modules, natal orchestration update, unit tests, integration tests and architecture guards. Detailed mapping is in `generated/03-acceptance-traceability.md`.

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | modified | Dignity/dominance payloads and phase validators | AC1, AC2, AC3, AC13, AC20, AC22 |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | modified | Initial dignity/dominance capabilities | AC3, AC14, AC23 |
| `backend/app/domain/astrology/dignities/chart_object_inputs.py` | added | Dignity selector/projector/enricher | AC4, AC6, AC7, AC8, AC21 |
| `backend/app/domain/astrology/dominance/chart_object_inputs.py` | added | Dominance selector/projector/enricher | AC5, AC17, AC18, AC19 |
| `backend/app/domain/astrology/dominance/planet_dominance_engine.py` | modified | Accept projected chart-object inputs | AC12, AC17 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | Multi-pass dignity/dominance enrichment | AC9, AC10 |
| `backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` | added | Dignity runtime tests | AC1, AC4, AC6, AC7, AC8, AC13, AC21 |
| `backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` | added | Dominance runtime tests | AC2, AC5, AC17, AC18, AC19, AC20 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | modified | CS-220 guards | AC12, AC15, AC24 |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | modified | Payload/capability expectations | AC3, AC14, AC23 |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | modified | Natal integration evidence | AC9, AC10 |
| Dominance tests/fixtures | modified | Renamed engine argument | AC11, AC12 |
| CONDAMAD files | added | Capsule/evidence | AC16 |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `. .\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; ruff check .; Pop-Location` | repo root | PASS | 0 | Backend format/lint passed: 1522 files unchanged, all checks passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | PASS | 0 | 1 test passed; AC10 targeted contract evidence. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_dignity_runtime.py` | repo root | PASS | 0 | 9 tests passed after strict brief-alignment fixes. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_dominance_runtime.py` | repo root | PASS | 0 | 10 tests passed after strict brief-alignment fixes. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | PASS | 0 | 19 tests passed after review fixes. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | PASS | 0 | 22 historical regression tests passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/dignities` | repo root | PASS | 0 | 12 tests passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py` | repo root | PASS | 0 | 1 test passed. |
| `. .\.venv\Scripts\Activate.ps1; pytest -q` | repo root | PASS | 0 | Final rerun passed: 3000 passed, 1 skipped, 1177 deselected in 261.81s. |
| `. .\.venv\Scripts\Activate.ps1; Push-Location backend; python -c "from app.main import app; print(app.title)"; Pop-Location` | repo root | PASS | 0 | Backend app imports successfully and reports `horoscope-backend`. |

## Review findings resolved

| Finding | Source | Resolution | Validation |
|---|---|---|---|
| Runtime payloads carried free-text `reason` values | Subagent story conformance + source closure | Removed reason fields from CS-220 dignity/dominance payload breakdowns and projectors | Targeted runtime tests + full `pytest -q` |
| Unknown dignity/dominance result targets were silently ignored | All review layers | Added consumed-code checks and explicit `ValueError`; tests cover ghost target | Runtime tests + full `pytest -q` |
| Nominal-code eligibility guard was incomplete | Technical risk review | Added AST guard against equality/membership comparisons on code fields in CS-220 modules | Architecture guard + full `pytest -q` |
| Validation evidence did not prove venv activation | Re-review story conformance | Reran Ruff, targeted tests, full `pytest -q` and backend import after `. .\.venv\Scripts\Activate.ps1`; updated evidence commands | Commands table above |
| AC10 targeted command was missing from evidence | Re-review technical risk | Added `test_natal_result_contract.py` to validation plan and reran it in venv | 1 test passed |
| Nominal-code/list scan was missing and hits were unclassified | Re-review story conformance | Reran scan and classified hits as historical calculator logic, not CS-220 selector/projector eligibility | Static guard evidence below |
| Bare historical `pytest -q` command remained in evidence | Re-review story conformance | Removed the non-compliant command row from validation evidence; only venv-backed final validation remains authoritative | Commands table above |
| Narrative-payload scan evidence did not match validation plan | Re-review technical risk | Reran the broad planned scan and classified all hits as pre-existing interpretation runtime/reference surfaces or non-payload imports | Static guard evidence below |
| Selectors delegated minimal-data and uniqueness checks downstream | Brief-alignment review | Added selector-level uniqueness and minimum-data validation without nominal-code branching | Dignity/dominance runtime tests + architecture guard |
| Dominance projector exposed only a minimal historical input shape | Brief-alignment review | Extended `DominanceChartObjectInput` with classifications and runtime dignity/motion/visibility payloads; dominance selector and enricher now require dignity payload when applicable | Dominance runtime tests + full pytest |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- No compatibility wrapper, alias, fallback or duplicate calculator introduced.
- New modules project and enrich only; scores remain owned by historical calculators.
- Type/object eligibility scan: zero active hits.
- Nominal-code/list scan: classified hits only:
  - `accidental_dignity_calculator.py:129` checks calculated match types against solar condition types inside the historical accidental dignity calculator.
  - `essential_dignity_calculator.py:58` filters rulership rows by sect in the historical essential dignity calculator.
  - `planet_dominance_engine.py:55` iterates projected candidate codes already selected from chart objects.
  - `planet_dominance_engine.py:267` scores the historical luminary-emphasis factor from runtime reference data; it is not CS-220 eligibility.
- Direct `planet_positions` scan in dignity/dominance packages: zero hits.
- Forbidden builder scan: zero hits.
- Broad narrative-payload scan:
  - `dominance/planet_dominance_engine.py:16` imports the pre-existing `DominantAspectEvaluator`; it is not a CS-220 payload field or narrative projection.
  - `runtime/aspect_modifiers.py`, `runtime/aspect_runtime_data.py`, `runtime/house_runtime_data.py` and `runtime/runtime_reference.py` are pre-existing interpretation/reference runtime surfaces outside the CS-220 dignity/dominance payload path.
  - `chart_object_runtime_data.py:79` is the pre-existing `supports_interpretation` capability flag; CS-220 `DignityRuntimePayload` and `DominanceRuntimePayload` do not expose narrative/prompt/meaning fields.

## Remaining risks

- No remaining implementation risk identified after full validation.

## Suggested reviewer focus

- Verify that phase validation is strict enough without reintroducing construction cycles.
- Verify that `DominanceRuntimePayload` remains a contribution projection and does not replace `DominantPlanetsResult`.
