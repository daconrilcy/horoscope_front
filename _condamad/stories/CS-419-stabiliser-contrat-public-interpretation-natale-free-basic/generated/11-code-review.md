# Review CS-419 - Implementation

Verdict: CLEAN
Date: 2026-05-31

## Scope

- Reviewed story: `_condamad/stories/CS-419-stabiliser-contrat-public-interpretation-natale-free-basic/00-story.md`.
- Source brief: `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`.
- Tracker row: `_condamad/stories/story-status.md`, path and source brief match CS-419.
- Implementation surface: backend public `/v1/natal/interpretation` contract, free short projection, Basic V2 public payload, tests and evidence.
- Guardrails checked: `RG-150`, `RG-152`, `RG-154`, `RG-155`, `RG-164`, `RG-165`, `RG-166`, `RG-167`, `RG-168`.

## Findings Fixed

- Replaced the obsolete pre-development review artifact with this implementation review.
- Added coverage for already-stabilized `natal_interpretation_short` rows still persisted as `COMPLETE`.
- Centralized free-short detection in `NatalInterpretationService` so formatting and persisted deserialization use the same branch rule.
- Expanded accepted-public-payload denylist assertions to include `chart_json` and `natal_data`.

## Review Result

- Free short responses expose `data.meta.level=short`, `data.use_case=natal_interpretation_short`, readable `AstroFreeResponseV1`,
  null `narrative_natal_reading_v1` and null `basic_natal_interpretation_v2`.
- Premium short rows that use `natal_interpretation_short` without the obsolete `COMPLETE` storage marker remain deserialized as `AstroResponseV1`.
- Basic complete responses keep non-null canonical `BasicNatalInterpretationV2` with the required version block and public synthesis body.
- Accepted public payload tests reject technical markers, audit markers and raw carriers.
- Route and OpenAPI registration remain stable.

## Validation Evidence

- `ruff format app/services/llm_generation/natal/interpretation_service.py tests/integration/test_natal_interpretation_public_free_basic_contract.py`: PASS.
- `ruff check app/services/llm_generation/natal/interpretation_service.py tests/integration/test_natal_interpretation_public_free_basic_contract.py`: PASS.
- `ruff check .`: PASS.
- `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short --long`: 4 passed.
- `python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short --long`: 18 passed.
- `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short --long`: 1 passed.
- `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short --long`: 2 passed.
- `python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short`: 18 passed.
- `python -B -m pytest -q app/tests/integration/test_natal_free_short_variant.py --tb=short --long`: 1 passed.
- Route assertion for `/v1/natal/interpretation`: PASS.
- OpenAPI assertion for `/v1/natal/interpretation`: PASS.
- Denylist scan: hits classified as guard definitions, validators or internal generation-only `chart_json`; public payload tests prove no accepted response leak.

## Status

- Fresh review after corrections: CLEAN.
- Propagation decision: no-propagation; fixes are local to CS-419 contract evidence and tests.
- Residual risk: full default backend pytest still has one unrelated pre-existing architecture failure documented in `generated/10-final-evidence.md`.
