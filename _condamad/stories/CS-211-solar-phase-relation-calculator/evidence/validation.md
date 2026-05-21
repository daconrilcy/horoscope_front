# Validation Evidence - CS-211

## Baseline

- `solar_phase_relation_calculator.py` did not exist before implementation.
- `PlanetarySolarPhaseRelation` and `SolarPhaseRelationKey` already existed in
  `contracts.py`.
- `RG-138` already existed for CS-211.

## Commands

| Command | Result | Summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` | PASS | 21 passed. |
| `ruff format .` | PASS | 2 files reformatted. |
| `ruff check .` | PASS after fix | Import order fixed; rerun passed. |
| `pytest -q` | PASS | 2862 passed, 1 skipped, 1177 deselected. |
| `Test-Path backend\app\domain\astrology\planetary_conditions\solar_phase_relation_calculator.py` | PASS | `True`. |
| Story validation and lint commands | PASS | validate, explain-contracts, lint and strict lint passed. |

## Static guards

- Forbidden import scan: zero hits.
- Forbidden dependency scan: zero hits.
- Forbidden scoring scan: zero hits.
- Forbidden narrative / heliacal / visibility scan: zero hits.
- Adjacent public-symbol scan: zero hits.
- Adjacent diff: empty.

## Guardrails

- `RG-135`: contracts remain pure dataclasses/enums.
- `RG-136`: solar proximity calculator unchanged.
- `RG-137`: planetary motion calculator/profiles unchanged.
- `RG-138`: solar phase relation calculator remains pure, deterministic and
  non-integrated.

## Review fixes

- Rejected `conjunction_tolerance_deg >= 180.0` to prevent a threshold that
  absorbs the full zodiacal circle.
- Added explicit governance and untracked-file evidence for the no-commit
  workflow.
