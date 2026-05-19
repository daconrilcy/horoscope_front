# No Legacy / DRY Guardrails - CS-195

## Canonical owners

- Runtime tables/models: `backend/migrations/**`, `backend/app/infra/db/models/**`.
- Runtime loading: `backend/app/infra/db/repositories/**`.
- Runtime contracts: `backend/app/domain/astrology/runtime/runtime_reference.py`.
- Pure advanced calculators: `backend/app/domain/astrology/advanced_conditions/**`.
- Natal orchestration: `backend/app/domain/astrology/natal_calculation.py`.
- Public projection: `backend/app/services/chart/json_builder.py`.

## Forbidden

- DB/API/service/prediction/LLM imports in `advanced_conditions/**`.
- Local advanced type or weight maps named like `ADVANCED_CONDITION_TYPES`,
  `ADVANCED_CONDITION_WEIGHTS`, `HAYZ_RULES`, `MUTUAL_RECEPTION_RULES`,
  `PLANET_SPEED_THRESHOLDS`, `HELIACAL_PHASES`, `BENEFIC_PLANETS`,
  `MALEFIC_PLANETS`.
- Serializer-side calculation of advanced conditions or dominance.
- Compatibility shims, aliases, fallback rows, broad allowlists or TODOs.
- Deferred techniques explicitly excluded by the story.

## Required evidence

- Runtime inventory proves all active emitted parent types are loaded.
- Unit tests prove calculators emit subtype codes mapped to parent
  `condition_type_code`.
- Guard tests and scans prove the domain boundary and no-local-map constraints.
- JSON tests prove `advanced_conditions` is projected from `NatalResult`.
