# CS-206 Runtime Audit Before

## Runtime Sources

- `docs/db_seeder/astrology/astral_planet_natures.json` exposes `benefic` for `venus`, `jupiter` and `malefic` for `mars`, `saturn`.
- `AstrologyRuntimeReference.planet_natures.nature_for_planet()` is the canonical lookup used by the detector.
- `PlanetSectCondition` is already present on `PlanetDignityResult.sect_condition`.

## Existing Advanced Condition Support Before Implementation

- `astral_advanced_condition_types.json` did not include `sect_nature_mitigation`.
- `astral_advanced_condition_weights.json` did not include weights for `sect_nature_mitigation`.
- No `SectNatureMitigationCondition` contract existed.
- No public `traditional_conditions[*].sect_nature_mitigation` projection existed.

## Seed Decision

CS-206 requires one new runtime parent type and one runtime weight row:

- `sect_nature_mitigation` in `astral_advanced_condition_types.json`.
- `sect_nature_mitigation` in `astral_advanced_condition_weights.json`.

The precise mitigation polarity remains in runtime-backed calculated `condition_code` values, not in local planet lists.
