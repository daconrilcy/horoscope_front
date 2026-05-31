# QA Report CS-418

## Fixture data

- `tests.integration.basic_natal_v2_helpers.basic_runtime_plan` builds the same Basic plan as the service from `make_natal_result`.
- `valid_basic_draft` uses the Basic deterministic draft builder as a valid fake provider output.

## Cached read

- `test_compatible_basic_cache_is_served_without_gateway_call` proves a compatible `basic_natal_interpretation_v2` row is served without gateway invocation.

## Fake gateway regeneration

- `test_basic_complete_builds_plan_payload_validates_and_persists_versions` proves Basic complete builds the plan, passes a plan-derived prompt payload, validates the fake gateway draft and persists V2 metadata.
- `test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row` proves an older incompatible row is not served and triggers generation.

## Rejected boundary

- `test_natal_interpretation_rejected_public_boundary.py` remains green with Basic V2 changes.

## Controlled provider-live scope

- No provider-live call was run. This is intentional: the story forbids real provider calls in automated tests.
