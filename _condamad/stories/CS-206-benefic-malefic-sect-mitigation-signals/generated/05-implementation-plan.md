# Implementation Plan

## Current Architecture Finding

`AdvancedConditionEngine` already owns advanced condition emission and profile enrichment. `TraditionalConditionNormalizer` already converts advanced facts into explicit traditional contracts. `json_builder.py` already serializes traditional facts without importing calculators.

## Selected Approach

1. Add `SectNatureMitigationCondition` beside existing advanced/traditional contracts.
2. Add a pure `SectNatureMitigationDetector` that consumes runtime natures plus `PlanetSectCondition`.
3. Add runtime condition type and weight `sect_nature_mitigation`.
4. Integrate detector into `AdvancedConditionEngine` through the existing emitter.
5. Attach the precomputed mitigation contract in `TraditionalConditionNormalizer`.
6. Serialize the contract from `json_builder.py`.
7. Add focused tests and evidence snapshots.

## No Legacy Stance

No compatibility field, no frontend derivation, no local planet doctrine list, no score recalculation.

## Rollback Strategy

Revert the detector, contract, seed rows, engine call, normalizer serialization and tests as one coherent story slice.
