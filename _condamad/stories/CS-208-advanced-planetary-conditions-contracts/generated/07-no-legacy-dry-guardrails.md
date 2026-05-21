# No Legacy / DRY Guardrails - CS-208

## Forbidden

- Compatibility wrappers, aliases, fallback branches or legacy re-exports.
- Calculators or functions named `calculate_`, `compute_`, `resolve_`,
  `detect_`.
- Scoring, prompt, interpretation, LLM, API, DB, services, migrations,
  Pydantic/FastAPI/SQLAlchemy imports.
- `Any` and `dict[str, Any]` annotations in the production package.
- Mutable public list fields.

## Canonical Owner

`backend/app/domain/astrology/planetary_conditions/contracts.py` is the only
owner of the CS-208 contracts.

## Reintroduction Guards

- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  introspects public dataclasses and annotations.
- `RG-135` protects the package against calculation and dependency drift.
- Required scans in `generated/06-validation-plan.md` must remain zero-hit.
