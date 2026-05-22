# Implementation Plan

## Repository findings

- `PlanetVisibilityCondition` and `PlanetVisibilityKey` already existed in `contracts.py`.
- `PlanetVisibilityKey.CONJUNCT_SOLAR` and `PlanetVisibilityThresholds` were absent.
- Existing calculators CS-209, CS-211 and CS-212 are pure domain modules using package contracts and package exports.
- No existing `planetary_visibility_calculator.py` or targeted test file existed.

## Selected approach

- Add the missing visibility threshold contract to `contracts.py`.
- Add the enum value required by CS-213 without removing existing placeholders.
- Create one pure calculator module that composes precomputed solar proximity and solar phase relation facts.
- Export the new contract and functions from `planetary_conditions.__init__`.
- Add targeted unit tests for priority, thresholds, batch behavior, explicit missing relation failure and placeholder exclusion.

## No Legacy stance

- No compatibility shim, alias, fallback or duplicate owner.
- No adjacent integration into `NatalResult`, JSON, API, DB, migrations or frontend.
- Missing batch relation fails through `KeyError`; it does not return `UNKNOWN`.

## Rollback strategy

- Revert the five backend files added/modified for CS-213 and the generated evidence files.
