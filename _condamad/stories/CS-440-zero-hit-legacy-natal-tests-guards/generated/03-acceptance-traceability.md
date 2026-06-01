# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Allowlists reject runtime old-symbol hits. | CS-440 audit owns exact readonly/admin/guard classifications; CS-441, CS-442, and CS-443 are `done` with clean reviews. | Story tracker rows for CS-441 to CS-443; architecture guard suite `54 passed`. | PASS |
| AC2 | No nominal backend test uses `natal_interpretation_short`. | Remaining hits are classified as readonly historical, admin-only metadata, rejection guards, or extinction tests; no positive runtime test preserves old generation. | Positive mock scan for old adapter and fake generator names -> `PASS: no matches`; architecture guard suite `54 passed`. | PASS |
| AC3 | No nominal backend test uses `natal_long_free`. | Remaining hits are classified in `evidence/legacy-natal-zero-hit-audit.md`; no Basic/free positive generation path remains. | Backend theme natal suite `24 passed, 22 deselected`; architecture guard suite `54 passed`. | PASS |
| AC4 | No nominal test mocks old generation success. | Old adapter/service positive mocks are absent after CS-441 to CS-443 corrections. | Positive mock scans for `AIEngineAdapter.generate_natal_interpretation`, `fake_generate_natal_interpretation`, and `patch.object(...)` -> `PASS: no matches`. | PASS |
| AC5 | Public app scans are zero-hit for old natal control symbols. | Public runtime surfaces exclude old public URLs and refresh controls; readonly/admin residuals remain classified outside public command surfaces. | Route/OpenAPI assertions PASS; public URL scan PASS; frontend tests `136 passed`. | PASS |
| AC6 | `variant_code` never constructs a theme natal generation command. | Product-action contract remains the public generation owner. | Backend product-action and public-read suites `24 passed, 22 deselected`; frontend DOM guard included in `136 passed`. | PASS |
| AC7 | Extinction tests use explicit anti-return names. | Retained tests are absence/rejection/readonly guards, not nominal old generation tests. | Architecture guard suite and frontend DOM guard PASS. | PASS |
| AC8 | The architecture guard fails on new unauthorized hits. | `test_legacy_natal_runtime_hits_are_explicitly_authorized` remains the reintroduction guard for RG-174. | `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short` -> `54 passed`. | PASS |
| AC9 | The durable zero-hit invariant is tracked. | `RG-174` remains strict and allows only readonly historical, admin-only, rejection guard, or explicit extinction-test hits. | Targeted RG-174 registry scan found line 217. | PASS |
| AC10 | The final zero-hit report is persisted. | CS-440 report and audit record full closure with classified residuals. | CS-444 validation evidence and report/audit checks PASS. | PASS |
| AC11 | The old public route is removed or gone. | Public legacy natal interpretation routes remain absent from loaded routes and OpenAPI. | Runtime `app.routes` and `app.openapi()` assertions PASS; public URL scan PASS. | PASS |

Status values: `PENDING`, `PASS`, `FAIL`, `BLOCKED`.
