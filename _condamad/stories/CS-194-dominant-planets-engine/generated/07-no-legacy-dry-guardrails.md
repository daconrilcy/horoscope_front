<!-- Gardes No Legacy / DRY specifiques a CS-194. -->

# No Legacy / DRY Guardrails

## Canonical Truth

- Factor vocabulary and weights: `astral_dominance_factor_types` loaded into `AstrologyRuntimeReference.dominance_factor_types`.
- Domain computation: `backend/app/domain/astrology/dominance/PlanetDominanceEngine`.
- Public serialization: `backend/app/services/chart/json_builder.py` projects `NatalResult.planet_dominance` only.

## Forbidden

- Local factor/weight maps named or equivalent to `DOMINANCE_FACTORS`, `DOMINANCE_WEIGHTS`, `CHART_RULER_WEIGHT`, `ANGULARITY_WEIGHT`.
- `SIGN_RULERS` or `PLANET_RULERS` in the dominance engine.
- Imports from `app.infra`, `app.services`, `app.api`, `app.domain.prediction`, `app.services.prediction` inside `backend/app/domain/astrology/dominance/**`.
- `Session`, `select(`, `OpenAI`, `AIEngineAdapter`, `prompt`, `narration`, `micro_note` in the dominance domain.
- Recalculation of `condition_profiles`, `condition_signals` or dominance scoring inside `json_builder.py`.
- Frontend or LLM changes.

## Required Guards

- Unit guard for immutable dominance contracts.
- Runtime repository guard for exactly eight active factors ordered by `sort_order`.
- Architecture guard in `test_astrology_runtime_reference_guard.py` for imports, local weights, narrative/LLM symbols.
- Negative `rg` scans recorded in final evidence.

## Applicable Regression Guardrails

- `RG-101`, `RG-107`, `RG-108`, `RG-112`, `RG-118`, `RG-119`, `RG-120`.
- `RG-121` must be added by this story for the new canonical dominance engine.
