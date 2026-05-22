# No Legacy / DRY Guardrails

## Canonical responsibilities

- Runtime payload contracts: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- Dignity input/payload projection: `backend/app/domain/astrology/dignities/chart_object_inputs.py`.
- Dominance input/payload projection: `backend/app/domain/astrology/dominance/chart_object_inputs.py`.
- Dignity scoring: `PlanetDignityScoringService`.
- Chart-level dominance ranking: `PlanetDominanceEngine`.

## Forbidden

- Eligibility by `object_type`, `ChartObjectType.PLANET`, `ChartObjectType.LUMINARY`, nominal planet code or traditional planet list.
- Direct `planet_positions` consumption in new dignity/dominance runtime consumers.
- Payload projectors recomputing total, essential, accidental or dominance scores.
- Payload fields with interpretation, narrative, prompt, llm, meaning or psychological text.
- Compatibility wrappers, aliases, fallback behavior or duplicate calculators.

## Required evidence

- Unit tests for selectors, input projectors, payload projectors and enrichers.
- Architecture guard for capability-driven CS-220 modules.
- Negative scans from `06-validation-plan.md`.
- Full diff review proving no API/frontend/DB/public JSON changes.
