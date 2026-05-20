# Golden Cases Validation

Date: 2026-05-20

## Summary

- Outcome: PASS
- Python commands were run after `.\\.venv\\Scripts\\Activate.ps1`.
- No production file, frontend file, API route, migration, seed, dependency or
  LLM file was changed.
- Review fix converged the duplicated test-local sect runtime fixture into
  `tests.factories.astrology_runtime_reference_factory.complete_reference_with_planet_sect_rules`.
- Follow-up verification fix expanded G7/G8 so hayz is locked through advanced
  conditions, condition profile breakdown and governed condition signals.
- `golden-cases-before.json` is a valid marker for no prior golden suite.
- `golden-cases-after.json` is the first curated runtime snapshot for G1-G12.

## Commands

| Command | Result | Summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | PASS | 9 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | PASS | 5 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | PASS | 4 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | PASS | 6 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py` | PASS | 2 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` | PASS | 4 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | PASS | 7 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | PASS | 2 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | PASS | 1 passed |
| `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | PASS | 17 passed |
| `pytest -q backend/app/tests/unit/test_chart_result_service.py` | PASS | 7 passed |
| `ruff format .` | PASS | 1477 files left unchanged on final run |
| `ruff check .` | PASS | all checks passed |
| `ruff check backend/tests/factories/astrology_runtime_reference_factory.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | PASS | all checks passed after import-order fix |
| `ruff check backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | PASS | all checks passed after G7/G8 coverage fix |
| `python -m json.tool .../golden-cases-before.json` | PASS | valid JSON |
| `python -m json.tool .../golden-cases-after.json` | PASS | valid JSON |
| `Test-Path .../golden-cases-index.md; ...before.json; ...after.json; ...validation.md` | PASS | all returned `True` |
| `rg -n "G1|G2|G3|G4|G5|G6|G7|G8|G9|G10|G11|G12" .../golden-cases-index.md` | PASS | all case IDs are documented |
| `git diff --check` | PASS | no whitespace or conflict-marker errors |

## Scan Classifications

| Scan | Result | Classification |
|---|---|---|
| Legacy sect names: `sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect` | Hits found | Allowed canonical runtime/test references. `sect_code` and `chart_sect_code` are existing runtime reference keys used by repositories, mappers, calculators and the shared test runtime fixture; no public JSON legacy alias was introduced. |
| Forbidden local constants: `DIURNAL_PLANETS|NOCTURNAL_PLANETS|...|PLANETARY_JOYS` | Zero hits | PASS. |
| Horizon tuple scan | Zero hits | PASS; no local horizon tuple was introduced in production or CS-200 helpers. |
| Downstream `SectCalculator` imports | Zero hits | PASS; no downstream recalculation owner was added. |
| Downstream `PlanetSectConditionCalculator` imports | Zero hits | PASS; no downstream recalculation owner was added. |
| Forbidden domain dependencies / prompt scan | Existing hits: `prompt_hint` in condition signal contract and builder | Allowed CS-193 signal contract field; not an LLM prompt dependency and not touched by CS-200. |

## Snapshot Notes

- G1-G11 are synthetic domain cases with explicit fixture inputs and runtime
  outputs.
- G12 uses `build_natal_result` with the simplified deterministic engine and
  a compact downstream adapter fixture to keep JSON evidence stable.
- G12 public JSON evidence stores only contract fields, not full payloads.
- G1-G12 now consume a single shared test runtime fixture for planet sect rules
  instead of duplicating that fixture table in each test module.
- G7 snapshot includes `profile_breakdown` with advanced `hayz` and
  `condition_signals`; G8 snapshot proves no advanced `hayz` profile
  contribution remains when only the sect prerequisite is true.
