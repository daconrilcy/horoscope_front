# Implementation Plan

## Repository findings

- `PlanetarySolarPhaseRelation` and `SolarPhaseRelationKey` already exist in
  `contracts.py`.
- No `solar_phase_relation_calculator.py` existed before implementation.
- Existing calculators are pure modules with stdlib + contract imports.
- `RG-138` already exists and matches this story.

## Proposed changes

- Add `SolarPhaseRelationThresholds` as a frozen slotted dataclass.
- Add a pure calculator using `(planet_longitude_deg - sun_longitude_deg) %
  360.0`.
- Treat `planet_key == "sun"` as `CONJUNCT_SOLAR` with `0.0` distance.
- Treat exact `180.0` as `OCCIDENTAL`.
- Add a batch helper and package exports.
- Add focused unit tests for thresholds, normalization, tolerance, relation
  conventions, non-finite longitude rejection and batch behavior.

## Rollback strategy

Remove the new calculator, exports, threshold contract and tests. No migration,
API, DB, frontend or adjacent runtime integration is involved.
