# Public JSON Projection Audit Before

## Field Mapping

| Public block | Source in `NatalResult` | Before CS-201 state | Notes |
|---|---|---|---|
| `dignities` | `dignities`, `dignity_sect` | projected | `dignities.sect` is the CS-197 object. |
| `dignities.planets[*].sect_condition` | `dignities[*].sect_condition` | projected | Missing new-result condition raises instead of recalculating. |
| `planet_condition_profiles` | `condition_profiles` | projected with metadata envelope before CS-201 | CS-201 converges it to a direct map keyed by planet code. |
| `planet_condition_signals` | `condition_signals` | projected with metadata envelope before CS-201 | CS-201 converges it to a direct map keyed by planet code. |
| `advanced_conditions` | `advanced_conditions` | projected | Empty input serializes `[]`. |
| `dominant_planets` | `dominant_planets` | projected/neutralized | `null` when absent or no-time. |
| `interpretation_adapter` | `interpretation_adapter` | projected/neutralized | `null` when absent or no-time. |
| `astral_points` | `astral_points` | dropped | Added by CS-201 as projection only. |
| `signs_runtime` | `signs_runtime` | dropped | Added by CS-201 as projection only. |
| `houses` | `houses` | projected/neutralized | Empty in no-time mode. |
| `angles` | `houses` cusps | projected/neutralized | Existing angle projection derives public angle coordinates from already calculated houses. |
| `house_rulers` | runtime house `ruler` | projected/neutralized | Public historical field is derived from projected runtime houses. |
| `chart_balance` | `chart_balance` | projected when available | No score recalculation in projection. |

## Neutralization

- No-time mode already neutralizes `houses`, `house_rulers`, `dominant_planets` and `interpretation_adapter`.
- CS-201 extends neutralization to nested `house` fields inside `astral_points` and `signs_runtime`.
- No-location mode keeps time-derived structures only when the runtime produced them, while angles stay unavailable.

## Import / Calculation Audit

- `json_builder.py` does not import sect, dignity, condition, dominance or interpretation engines for the CS-201 blocks.
- `json_builder.py` validates object contracts and serializes fields already present on the result.
- Existing `_serialize_aspect_runtime()` may build aspect runtime metadata for aspect projection; this is outside the CS-201 advanced dignity/sect surface and remains pre-existing behavior.
- No old persisted payload support path recalculates missing sect, condition, dominance or adapter facts.

## Old Payload Policy

- Missing blocks from old stored `NatalResult` payloads are handled by Pydantic defaults during read (`[]` or `None`), not by mutating persisted JSON.
- The projection must not invent `dignities.sect` or `sect_condition` for old payload gaps.
