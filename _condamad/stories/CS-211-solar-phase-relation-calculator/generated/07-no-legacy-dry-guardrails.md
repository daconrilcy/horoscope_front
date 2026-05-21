# No Legacy / DRY Guardrails

## Canonical owners

- Threshold contract: `backend/app/domain/astrology/planetary_conditions/contracts.py`
- Solar phase relation calculator:
  `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- Public package exports:
  `backend/app/domain/astrology/planetary_conditions/__init__.py`
- Unit tests:
  `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`

## Forbidden changes

- No compatibility shim, alias, fallback or second owner.
- No API, DB, service, frontend, JSON public or `NatalResult` integration.
- No scoring, narration, prompt, heliacal or advanced visibility responsibility.

## Guard evidence

- `RG-135`, `RG-136`, `RG-137` remain applicable and unchanged.
- `RG-138` exists for CS-211 and is satisfied by focused unit tests, zero-hit
  scans and empty adjacent diff.
