# Implementation Plan

## Repository findings

- `SectCalculator` returned only `"day"` / `"night"` but already read the runtime `above_horizon` and `below_horizon` rules.
- `PlanetDignityResult` carried only the string `sect`.
- `NatalResult` exposed dignity results as a list without chart-level sect metadata.
- `json_builder.py` copied a string sect from the latest dignity result.
- `AccidentalDignityCalculator` still had local horizon house constants for horizon-position conditions.

## Selected approach

- Add immutable `ChartSectResult`.
- Keep existing string `sect` for already delivered downstream contracts.
- Attach the shared `ChartSectResult` to every `PlanetDignityResult` and expose it once as `NatalResult.dignity_sect`.
- Serialize `dignities.sect` from the precomputed contract.
- Replace local horizon constants in `AccidentalDignityCalculator` with runtime horizon rule lookup.

## Tests to update

- Sect calculator contract and negative cases.
- Dignity scoring shared object propagation.
- Dignity DTO immutability.
- Natal result contract field.
- Chart JSON public projection.
- Chart result persistence payload.

## Rollback strategy

Revert the DTO, calculator and projection changes together; the change is contract-shaped and should not be partially rolled back.
