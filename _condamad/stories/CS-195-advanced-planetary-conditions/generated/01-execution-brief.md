# Execution Brief - CS-195-advanced-planetary-conditions

## Primary objective

Implement CS-195 exactly from `../00-story.md`: add backend-only advanced
planetary conditions as runtime-backed, factual domain data, integrate them into
condition profiles, condition signals, dominance scoring and public chart JSON.

## Boundaries

- Scope is backend astrology runtime, pure domain calculators, natal result,
  dominance and chart JSON projection.
- Frontend is out of scope.
- No new dependency is allowed.
- `advanced_conditions/**` must stay pure: no DB, API, services, prediction or
  LLM imports.
- Runtime type/profile/weight data must come from `astral_advanced_condition_*`
  reference tables and JSON seeds.

## Required preflight

- `CS-192`, `CS-193` and `CS-194` must be `done` in `story-status.md`.
- `NatalResult` must already expose condition profiles, condition signals and
  dominant planets.
- `json_builder.py` must already project those surfaces.
- `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`, `RG-118`, `RG-119`,
  `RG-120`, `RG-121` and `RG-122` apply.

## Done when

- AC1-AC15 have implementation and validation evidence.
- Runtime repository loads advanced condition types, profile and weights.
- Pure calculators emit only mapped runtime condition types.
- `NatalResult.advanced_conditions` and JSON `advanced_conditions` are
  projections, not serializer-side calculations.
- Final review is clean and status is synchronized.
