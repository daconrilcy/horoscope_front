<!-- Evidence de validation CS-215. -->

# CS-215 Validation Evidence

## Baseline

- `contracts.py`, `accidental_dignity_calculator.py`,
  `planet_dignity_scoring_service.py`, `planetary_conditions/contracts.py`,
  `advanced_planetary_conditions_runtime.py` inspectes avant edition.
- `RG-135` a `RG-142` consultes dans
  `_condamad/stories/regression-guardrails.md`.

## Commands

| Command | Result | Summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py` | PASS | 9 passed |
| `pytest -q backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py` | PASS | 3 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` | PASS | 9 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py` | PASS | 5 passed |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | PASS | 5 passed |
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py` | PASS | 4 passed |
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | 14 passed |
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | PASS | 83 passed |
| `ruff format backend` | PASS | 1505 files left unchanged |
| `ruff check backend` | PASS | All checks passed |
| `ruff check .` | PASS | All checks passed |
| `pytest -q` | PASS | 2932 passed, 1 skipped, 1177 deselected |
| Backend smoke `/health` | PASS | Uvicorn lance dans le venv sur `127.0.0.1:8015`, endpoint `/health` repond 200, processus arrete |
| `condamad_story_validate.py` | PASS | story validation PASS |
| `condamad_story_lint.py --strict` | PASS | story lint PASS |

## Scans

- Forbidden deps scan: zero hits.
- Forbidden interpretation/surface scan: zero hits.
- Forbidden duplication scan: zero hits.
- Adjacent diff on `planetary_conditions`, `advanced_conditions`,
  `interpretation_adapters`, `json_builder.py`, API, infra, migrations and
  frontend: empty.
- Public symbol scan: hits limited to new modules, exports, scoring and tests.
- `RG-142`: present.
- Pydantic `TypeAdapter(PlanetDignityResult)` excludes
  `advanced_condition_modifiers` from dump and schema.
- `git diff --check`: PASS.

## Remaining Risk

Aucun risque restant identifie.
