# No Legacy / DRY Guardrails

## Canonical Responsibility

- Contract owner: `backend/app/domain/astrology/planetary_conditions/contracts.py`
- Calculator owner: `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
- Public export owner: `backend/app/domain/astrology/planetary_conditions/__init__.py`
- Test owner: `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`

## Forbidden Patterns

- Compatibility wrapper, alias, fallback, shim or duplicate moon phase implementation.
- Recreated contracts outside `contracts.py`.
- API, infra, services, DB, Pydantic, FastAPI, OpenAI or LLM dependency.
- Scoring, interpretation, narration, prompt, dominance, dignity or profile logic.
- Integration into `NatalResult`, chart JSON, frontend, migrations, transits, progressions, eclipses or ephemerides.

## Required Negative Evidence

- Zero-hit scans for forbidden imports and forbidden symbols in `moon_phase_calculator.py`.
- Zero-hit adjacent scan for `calculate_moon_phase_condition` outside `planetary_conditions` and tests.
- Diff review proving no adjacent production surface changed.

## Exceptions

No exception is authorized for CS-212.
