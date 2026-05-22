# Implementation Plan - CS-216

## Findings

- `AdvancedPlanetaryConditionsResult` already contains immutable planet bundles and moon phase facts.
- `NatalResult.advanced_planetary_conditions` is already excluded from JSON schema and model dumps.
- No existing `interpretation/advanced_conditions` package exists.

## Approach

1. Add immutable interpretation contracts and a static catalog.
2. Add a pure runtime that extracts condition keys from existing fact contracts and resolves profiles using the required priority.
3. Add an excluded `NatalResult.interpretation_profiles_by_planet` field and populate it after advanced conditions are calculated.
4. Add focused unit tests for contracts/catalog/runtime and extend natal integration tests.
5. Record validation evidence and run the required checks.

## Rollback

Remove the new package, remove the `NatalResult` field/imports/injection, and remove the added tests/evidence.
