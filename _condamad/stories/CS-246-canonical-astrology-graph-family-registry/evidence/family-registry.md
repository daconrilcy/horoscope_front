# CS-246 Registry Snapshot

Canonical source: `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.

| Family code | Status | Owner | Cache boundary |
|---|---|---|---|
| `natal_chart_v1` | `active` | `astrology-runtime-natal` | birth data, coordinates, house system, zodiac mode, runtime reference |
| `transit_chart_v1` | `blocked-by-astronomical-proof` | `astrology-runtime-temporal` | blocked until cache policy is approved |
| `synastry_chart_v1` | `blocked-by-multi-chart-decision` | `astrology-runtime-relationship` | blocked until cache policy is approved |
| `solar_return_v1` | `blocked-by-astronomical-proof` | `astrology-runtime-temporal` | blocked until cache policy is approved |
| `lunar_return_v1` | `blocked-by-astronomical-proof` | `astrology-runtime-temporal` | blocked until cache policy is approved |
| `progressed_chart_v1` | `blocked-by-astronomical-proof` | `astrology-runtime-temporal` | blocked until cache policy is approved |
| `composite_chart_v1` | `blocked-by-multi-chart-decision` | `astrology-runtime-relationship` | blocked until cache policy is approved |
| `profection_v1` | `blocked-by-astronomical-proof` | `astrology-runtime-temporal` | blocked until cache policy is approved |
| `forecasting_v1` | `blocked-by-product-decision` | `astrology-runtime-forecasting` | blocked until cache policy is approved |
| `ai_scoring_v1` | `blocked-by-trace-decision` | `astrology-runtime-ai-scoring` | blocked until cache policy is approved |
| `narrative_generation_v1` | `blocked-by-product-decision` | `astrology-runtime-text-generation` | blocked until cache policy is approved |

## Deterministic queries

- Owner lookup for `transit_chart_v1`: `astrology-runtime-temporal`.
- Required input lookup for `synastry_chart_v1`: includes `secondary_birth_data`.
- Astronomical blocker filter: includes `transit_chart_v1`, `solar_return_v1`, `lunar_return_v1`, `progressed_chart_v1`, and `profection_v1`.
- Cache boundary lookup for `natal_chart_v1`: `birth data, coordinates, house system, zodiac mode, runtime reference`.
- Cache blocker evidence: every non-active family includes `cache policy approval required`.
- Unknown family code lookup: raises `AstrologyGraphFamilyRegistryError`.
- Duplicate family declaration: raises `AstrologyGraphFamilyRegistryError`.
