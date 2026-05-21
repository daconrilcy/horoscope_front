<!-- Garde No Legacy / DRY CONDAMAD pour CS-205. -->

# CS-205 No Legacy / DRY Guardrails

## Canonical owners

| Responsibility | Canonical owner |
|---|---|
| Chart sect | `ChartSectResult.chart_sect` |
| Runtime triplicity data | `AstrologyRuntimeReference.dignity_reference.triplicity_rulers` |
| Essential dignity calculation | `EssentialDignityCalculator` |
| Dignity scoring orchestration | `PlanetDignityScoringService` |
| Public JSON | CS-201 `json_builder.py` projection, unchanged by CS-205 |

## Forbidden patterns

- Production constants `TRIPLICITY_RULERS`, `DAY_TRIPLICITY_RULERS`,
  `NIGHT_TRIPLICITY_RULERS`, `PARTICIPATING_TRIPLICITY_RULERS`,
  `FIRE_TRIPLICITY`, `EARTH_TRIPLICITY`, `AIR_TRIPLICITY`,
  `WATER_TRIPLICITY`.
- Local element-to-ruler dictionaries in tests or production.
- Test helpers that recalculate triplicity instead of consuming runtime
  assignments.
- Compatibility wrappers, aliases, fallback doctrine, seed changes, migration
  changes, frontend derivation or public JSON changes.

## Required evidence

- Targeted tests for G1-G6.
- Runtime audit with exact field and participant status.
- Anti-constant scans over `backend/app`.
- Forbidden import scan over pure dignity code.
- Empty forbidden path diff for API, infra, prediction, migrations, seeds and
  frontend.

## Review checklist

- Each golden case reads expected rulers from runtime-backed assignments.
- Same-element day/night proof fails if `chart_sect` is ignored.
- Participant behavior is tested or explicitly documented from runtime/profile
  support.
- Non-ruler case proves no active `triplicity` item is awarded.
- No production file changed without explicit documented blocker.

