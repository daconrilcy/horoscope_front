# No Legacy / DRY Guardrails - CS-209

## Canonical ownership

- `SolarProximityThresholds`: `backend/app/domain/astrology/planetary_conditions/contracts.py`
- Solar proximity calculator: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- Public exports: `backend/app/domain/astrology/planetary_conditions/__init__.py`
- Tests: `backend/tests/unit/domain/astrology/planetary_conditions/`

## Forbidden outcomes

- No shim, alias, compatibility wrapper, fallback or second active owner.
- No integration in `NatalResult`, chart JSON, API, infra, DB, migrations or frontend.
- No scoring, interpretation, narration, prompt or LLM surface in the calculator.
- No duplicate threshold object outside `contracts.py`.

## Regression guardrails

- `RG-135`: `contracts.py` remains immutable contracts only, with no calculators, forbidden dependencies, free `Any`, or `dict[str, Any]`.
- `RG-136`: `solar_proximity_calculator.py` remains a pure deterministic domain calculator returning `SolarProximityCondition`.

## Evidence required

- Targeted tests for thresholds and calculator behavior.
- Full pytest and Ruff.
- Zero-hit scans for forbidden imports/dependencies/scoring/text in calculator.
- Zero-hit scans for forbidden imports/calculation/free annotations in contracts.
- Empty diff on adjacent forbidden surfaces.
