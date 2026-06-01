# Acceptance Traceability

<!-- Commentaire global: cette matrice relie chaque AC CS-440 aux preuves code, tests et scans. -->

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Allowlists reject runtime old-symbol hits. | CS-434 allowlist closed; CS-435 broad classified scan superseded; CS-440 audit now owns explicit readonly/admin/guard classifications. | `test_legacy_natal_runtime_hits_are_explicitly_authorized`; `app.routes`/OpenAPI import check. | PASS_WITH_LIMITATIONS |
| AC2 | No nominal backend test uses `natal_interpretation_short`. | Remaining hits are extinction, readonly historical, prompt governance or persisted-read tests; no public generator success path added. | Architecture guard + `rg` classified-hit evidence in final report. | PASS_WITH_LIMITATIONS |
| AC3 | No nominal backend test uses `natal_long_free`. | Remaining hits are adapter rejection, readonly historical, admin metadata, or extinction proof. | `test_llm_legacy_extinction.py`; architecture guard. | PASS_WITH_LIMITATIONS |
| AC4 | No nominal test mocks old generation success. | Old public route test renamed to anti-return; modern adapter mocks are classified as theme-natal/current runtime tests, not old raw use-case success. | `test_old_public_route_is_removed_or_gone`; backend integration tests. | PASS_WITH_LIMITATIONS |
| AC5 | Public app scans are zero-hit for old natal control symbols. | `forceRefresh`, `shouldRefreshShortAfterBasicUpgrade`, and public `use_case_level` are absent from runtime public paths; old key hits are classified readonly/admin/guard-only. | Runtime bounded scans PASS for refresh controls and public `use_case_level`; architecture guard classifies old-key hits. | PASS_WITH_LIMITATIONS |
| AC6 | `variant_code` never constructs a theme natal generation command. | CS-440 audit classifies `variant_code` as entitlement, prediction/daily, astrology calculation or historical data; public product-action contract rejects it. | `test_runtime_route_and_openapi_expose_product_action_contract`; `test_new_route_rejects_legacy_generation_fields`. | PASS |
| AC7 | Extinction tests use explicit anti-return names. | Backend old public route test renamed `test_old_public_route_is_removed_or_gone`; frontend DOM guard includes `test_theme_natal_contract_is_only_public_generation_path`. | Backend and frontend targeted tests PASS. | PASS |
| AC8 | The architecture guard fails on new unauthorized hits. | `test_legacy_natal_runtime_hits_are_explicitly_authorized` scans backend/app and frontend/src from repo-root paths with explicit owner allowlist. | `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short` PASS. | PASS |
| AC9 | The durable zero-hit invariant is tracked. | Added `RG-174` to `_condamad/stories/regression-guardrails.md`; story references guardrail. | Architecture guard checks `RG-174` and report presence. | PASS |
| AC10 | The final zero-hit report is persisted. | Added `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` and story audit. | Architecture guard checks report and audit content. | PASS |
| AC11 | The old public route is removed or gone. | Existing route remains documented as `410 Gone`; test name now states removed-or-gone contract. | `test_old_public_route_is_removed_or_gone`; structured route/OpenAPI check. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
