# CS-198 Final Evidence

Status: done.

## AC validation

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `PlanetSectCondition` added and contract tests pass. |
| AC2 | PASS | Scoring service reuses one `ChartSectResult`; tests assert object sharing and per-planet condition. |
| AC3 | PASS | Day chart maps diurnal Sun to `in_sect`. |
| AC4 | PASS | Night chart maps nocturnal Moon/Mars to `in_sect`. |
| AC5 | PASS | Night chart maps diurnal Jupiter to `out_of_sect`. |
| AC6 | PASS | Day chart maps nocturnal Moon to `out_of_sect`. |
| AC7 | PASS | Mercury runtime `all` returns `common` / `variable_by_condition`; Uranus missing profile returns `unknown`. |
| AC8 | PASS | Public JSON projects `sect_condition`. |
| AC9 | PASS | Downstream calculator import scan zero-hit. |
| AC10 | PASS | Before/after snapshots and validation note present. |

## Files changed

- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/advanced_condition_test_helpers.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `docs/db_seeder/astrology/astral_accidental_dignity_rules.json`
- `_condamad/stories/CS-198-planet-sect-condition-normalization/generated/*`
- `_condamad/stories/CS-198-planet-sect-condition-normalization/evidence/*`

## Commands run

- `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS, 58 passed.
- `ruff format .` - PASS, 1473 files left unchanged.
- `ruff check .` - PASS, all checks passed.
- `git diff --check` - PASS.
- `python -c "from app.main import app; print(app.title)"` from `backend/` after venv activation - PASS, `horoscope-backend`.
- Required scans recorded in `evidence/planet-sect-validation.md` - PASS or classified allowed hits.

## Commands not run yet

- Full `pytest -q` not run; story validation requires targeted backend suites.

## DRY / No Legacy

- No local planet sect constants introduced.
- No frontend change.
- No downstream import of `PlanetSectConditionCalculator`.
- No public legacy field introduced.
- Pre-CS-198 persisted `PlanetDignityResult` payloads remain model-valid with
  `sect_condition=None`; public JSON projection still rejects missing
  precomputed `sect_condition`.

## Remaining risks

- None identified for the implemented scope.

## Reviewer focus

- Verify that deriving intrinsic sect from `in_sect` runtime rules, including
  `chart_sect_code=all` for Mercury, is the intended canonical interpretation.
