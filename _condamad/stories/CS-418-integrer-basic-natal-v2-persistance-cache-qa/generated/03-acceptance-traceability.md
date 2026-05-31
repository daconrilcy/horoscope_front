# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic complete builds a reading plan. | `interpretation_service.py` builds `BasicNatalReadingPlan` before gateway for Basic complete. | `python -B -m pytest -q --long backend/tests/integration/test_basic_natal_v2_pipeline.py` | PASS |
| AC2 | Basic provider payload comes from the plan. | `build_basic_natal_prompt_payload` is passed through `NatalExecutionInput.basic_natal_prompt_payload`; gateway uses it instead of raw natal data. | `test_basic_natal_v2_pipeline.py`; `test_basic_natal_prompt_payload_builder.py`; payload boundary guard. | PASS |
| AC3 | Invalid Basic narrative is rejected. | Basic complete always enters `_validate_basic_natal_draft_output`; rejected path remains audit-only. | `test_natal_interpretation_rejected_public_boundary.py`; validator unit suite. | PASS |
| AC4 | Accepted Basic rows persist engine version. | `BasicNatalInterpretationV2` persisted under `basic_natal_interpretation_v2`. | `test_basic_natal_v2_pipeline.py` asserts `basic-natal-reading-v1`. | PASS |
| AC5 | Accepted Basic rows persist schema version. | Contract default `basic_natal_interpretation_v2` is persisted and returned. | `test_basic_natal_v2_pipeline.py`. | PASS |
| AC6 | Incompatible Basic cache is not served. | Cache invalidity includes missing/incompatible Basic V2 contract for Basic complete rows. | `test_basic_natal_v2_cache_invalidation.py`. | PASS |
| AC7 | Incompatible Basic cache regenerates by policy. | Incompatible rows are classified invalid so existing regeneration path is used. | `test_basic_natal_v2_cache_invalidation.py`. | PASS |
| AC8 | Quota is consumed after valid acceptance. | Route/gate unchanged; Basic acceptance returns before quota consumption remains impossible. | `test_natal_chart_long_quota_on_acceptance.py`. | PASS |
| AC9 | Fake gateway proves a valid complete reading. | Integration fake returns a plan-valid Basic draft; service persists public V2. | `test_basic_natal_v2_pipeline.py`. | PASS |
| AC10 | Rejected Basic output remains non-public. | Generic rejection/public boundary still excludes audit/rejected payloads. | `test_natal_interpretation_rejected_public_boundary.py`. | PASS |
| AC11 | Frontend renders public narrative only. | No frontend production change; existing `NatalNarrativeReading` path retained. | `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard`; `pnpm --dir frontend lint`. | PASS |
| AC12 | QA report is persisted. | `evidence/qa-report.md`; before/after runtime artifacts. | Capsule evidence paths present. | PASS |
| AC13 | Older short Basic logic is inactive for complete. | Complete Basic uses `natal_interpretation` + Basic V2 plan/payload; short key remains only short/free branches. | Targeted scans and integration assertions. | PASS |
| AC14 | Story evidence artifacts are persisted. | `generated/10-final-evidence.md`, traceability and `evidence/*`. | `condamad_validate.py --final`: PASS. | PASS |
| AC15 | Accepted Basic rows persist supporting metadata. | Added `taxonomy_version`, `salience_version`, `prompt_version`, `validator_version` to Basic V2 contract. | `test_basic_natal_v2_pipeline.py`; contract unit tests. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
