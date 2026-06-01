# Acceptance Traceability - CS-425

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Accepted Basic rows persist editorial version. | PASS | `BasicNatalInterpretationV2.basic_editorial_contract_version`; persisted via `basic_natal_interpretation_v2.model_dump()` | `test_compatible_basic_cache_is_served_without_gateway_call`; `test_basic_versions_are_centralized_and_serialized` |
| AC2 | The minimum editorial version is enforced. | PASS | `BASIC_NATAL_MIN_EDITORIAL_CONTRACT_VERSION`; storage compatibility compares exact version | `test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row[old_editorial_version]` |
| AC3 | No editorial version invalidates cache. | PASS | `load_basic_natal_interpretation_v2_from_payload` rejects missing version before Pydantic validation | `test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row[missing_editorial_version]` |
| AC4 | Older editorial version invalidates cache reuse. | PASS | Same compatibility gate rejects `basic-natal-editorial-legacy` | `test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row[old_editorial_version]` |
| AC5 | Degraded baseline tokens invalidate cache reuse. | PASS | `BASIC_NATAL_DEGRADED_BASELINE_TOKENS`; `contains_degraded_basic_natal_baseline_token`; provider/validator reuse canonical tokens | `test_degraded_baseline_tokens_make_basic_payload_incompatible`; scoped token `rg` |
| AC6 | Compatible clean Basic cache is served. | PASS | Compatible Basic V2 cache still returns `meta.cached=True` without gateway call | `test_compatible_basic_cache_is_served_without_gateway_call` |
| AC7 | Eligible degraded cache regenerates. | PASS | Incompatible Basic cache rows are skipped and regenerated through existing interpret flow | `test_incompatible_basic_cache_regenerates_instead_of_serving_stale_row` parametrized cases |
| AC8 | Non-regenerable degraded cache returns a controlled state. | PASS | Corrective pending use case hides degraded rows; quota exhaustion remains controlled when no corrective claim exists | `test_corrective_regeneration_claim_is_idempotent_and_hidden`; `test_check_access_for_complete_generation_raises_when_not_corrective` |
| AC9 | Corrective regeneration preserves quota timing. | PASS | Existing entitlement gate still uses `check_access_for_complete_generation` then `consume_on_acceptance` only after accepted non-cached output | `test_natal_chart_long_quota_on_acceptance.py`; zero-hit `check_and_consume` scan |
| AC10 | Rejected outputs remain hidden. | PASS | Rejected/audit rows remain hidden from public get/list | `test_natal_interpretation_rejected_public_boundary.py --long` |
| AC11 | Before-after degraded cache evidence is persisted. | PASS | Before/after snapshots persisted under `evidence/` | `basic-cache-degraded-before.json`; `basic-cache-degraded-after.json` |
| AC12 | No batch migration path is introduced. | PASS | No migration/batch path added | zero-hit `rg "batch.*basic|migration.*basic|alembic.*basic" app tests` |
| AC13 | Story validation evidence is persisted. | PASS | Validation artifact persisted | `evidence/validation.txt`; capsule final validation |

## Guardrails

- Applicable: `RG-150`, `RG-152`, `RG-155`, `RG-157`, `RG-164`, `RG-165`, `RG-166`, `RG-167`, `RG-168`, `RG-169`, `RG-171`, `RG-172`.
- Primary new executable guard: `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`.
- No frontend surface changed.
