# No Legacy / DRY Guardrails

## Canonical paths

- Runtime reference contract: `app.domain.astrology.runtime.runtime_reference`.
- DB/JSON confinement and mapping: `app.infra.db.repositories.astrology_runtime_reference_mapper`.
- Runtime loading and integrity: `app.infra.db.repositories.astrology_runtime_reference_repository`.
- Natal orchestration: `app.services.natal.calculation_service`.
- Pure natal calculation: `app.domain.astrology.natal_calculation`.

## Forbidden active paths

- `ReferenceDataService.get_active_reference_data` in natal/domain runtime.
- `reference_data: dict` as a business-domain input.
- `dict[str, Any]` as a public astrology business contract.
- Compatibility wrappers, aliases, feature flags, dual run, or transitional fallback.
- `PLANET_KEYWORDS`, `SIGN_RULERS`, `DEFAULT_ORB`, `ASPECT_WEIGHTS`, `HOUSE_MEANINGS`.
- `UNKNOWN_SIGN`, `ZODIAC_SIGNS`, `EXACT_ORB_DEG`, `TIGHT_RATIO`, `MODERATE_RATIO`.
- SwissEph-to-simplified implicit fallback.
- Prediction or LLM imports in `backend/app/domain/astrology`.

## Required evidence

- Guard test: `app/tests/unit/test_astrology_runtime_reference_guard.py`.
- Repository integrity test: `app/tests/unit/test_astrology_runtime_reference_repository.py`.
- Runtime contract tests under `tests/unit/domain/astrology`.
- Negative scans listed in `06-validation-plan.md`.
- RG-107 registry row in `_condamad/stories/regression-guardrails.md`.

## Search classification

| Pattern | Result | Classification | Action | Status |
|---|---|---|---|---|
| `ReferenceDataService.get_active_reference_data|reference_data: dict` in natal/domain runtime | zero hits | active legacy removed | none | PASS |
| DB-backed constants in natal/domain runtime | zero hits | active legacy removed | none | PASS |
| `UNKNOWN_SIGN|EXACT_ORB_DEG|TIGHT_RATIO|MODERATE_RATIO` in natal/domain runtime | zero hits | active legacy removed | none | PASS |
| SwissEph simplified fallback patterns | zero hits | active legacy removed | none | PASS |
| prediction/LLM imports in astrology domain | zero hits | boundary preserved | none | PASS |

## Reviewer checklist

- Confirm there is no nominal `dict` reference payload crossing service/domain.
- Confirm runtime DB incompleteness fails explicitly.
- Confirm tests do not preserve legacy dict input as nominal behavior.
- Confirm no compatibility path was introduced.
