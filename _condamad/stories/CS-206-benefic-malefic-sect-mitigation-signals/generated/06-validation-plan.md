# Validation Plan

## Environment Assumptions

- All Python commands run from repository root after `.\.venv\Scripts\Activate.ps1`.
- Frontend commands are conditional because CS-206 is expected to avoid frontend changes.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Detector tests | `pytest -q backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py` | repo root | yes | all pass |
| Advanced engine integration | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | yes | all pass |
| Traditional golden cases | `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | yes | all pass or snapshot intentionally updated for additive facts |
| Natal result contract | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | yes | all pass |
| JSON projection | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | yes | all pass |
| Runtime seed loading if seeds change | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | repo root | yes | all pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden nature constants | `rg -n "BENEFIC_PLANETS|MALEFIC_PLANETS|MIXED_PLANETS|NEUTRAL_PLANETS|DIURNAL_MALEFICS|NOCTURNAL_MALEFICS|SECT_MITIGATED_PLANETS|MARS_SECT_RULE|SATURN_SECT_RULE|JUPITER_SECT_RULE|VENUS_SECT_RULE" backend/app frontend -g "*.{py,ts,tsx,js,jsx}"` | repo root | yes | no production hits |
| Forbidden planet branches | `rg -n "if .*planet_code.*mars|if .*planet_code.*saturn|if .*planet_code.*jupiter|if .*planet_code.*venus|planet_code\s+in" backend/app/domain/astrology frontend -g "*.{py,ts,tsx,js,jsx}"` | repo root | yes | no unclassified production hits |
| Projection/frontend recalculation | `rg -n "SectCalculator|PlanetSectConditionCalculator|SectNatureMitigationDetector|AdvancedConditionEngine" backend/app/services/chart frontend -g "*.{py,ts,tsx,js,jsx}"` | repo root | yes | no hits |
| Legacy fields | `rg -n "sect_mitigation_legacy|legacy_sect_mitigation|benefic_code|malefic_code|planet_nature_code_legacy" backend/app backend/tests frontend -g "*.{py,ts,tsx,js,jsx}"` | repo root | yes | no hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | formatted without errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Evidence Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Evidence files exist | `Test-Path ...` commands from story section 20 | repo root | yes | all true |
| JSON evidence valid | `python -m json.tool <before/after snapshot>` | repo root | yes | valid JSON |

## Conditional Frontend Checks

Run `npm test -- NatalExpertPanel`, `npm run typecheck`, `npm run lint`, and `npm run build` only if files under `frontend/**` change.
