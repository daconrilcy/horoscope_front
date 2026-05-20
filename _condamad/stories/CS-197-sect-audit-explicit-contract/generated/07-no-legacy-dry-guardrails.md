# No Legacy / DRY Guardrails

## Canonical paths

- Sect calculation: `backend/app/domain/astrology/dignities/sect_calculator.py`
- Sect DTO: `backend/app/domain/astrology/dignities/contracts.py::ChartSectResult`
- Runtime horizon source: `PlanetDignityReferenceSet.accidental_rules`
- Public projection: `backend/app/services/chart/json_builder.py`

## Forbidden for CS-197

- Local horizon house lists in dignity or chart projection application code.
- `SectCalculator` usage from `json_builder.py`.
- Per-planet `PlanetSectCondition` / `planet_sect_condition`.
- Public compatibility aliases: `sect_legacy`, `legacy_sect`, `sect_code`, `chart_sect_code`.
- New frontend contracts.
- Dignity domain imports from infra, services, API, prediction or LLM providers.

## Required evidence

- Targeted tests for day, night, missing Sun and missing horizon runtime rule.
- Shared object propagation test in dignity scoring.
- JSON projection test proving `dignities.sect` is the explicit object.
- Persistence test proving `dignity_sect` and per-result `chart_sect` are stored.
- Scans listed in `06-validation-plan.md`.

## Hit classification

- `sect_code` and `chart_sect_code` hits in runtime reference models, repository mapping, seed factories and existing dignity condition evaluation are classified as runtime reference internals, not public compatibility aliases introduced by CS-197.
