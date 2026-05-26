# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The non-sensitive profile set covers five categories. | `evidence/profile-set.json` contains `precise_time`, `missing_time`, `foreign_location`, `controlled_incomplete`, and `standard`. | Python evidence assertion checks category coverage. | PASS |
| AC2 | Every profile has a traced `/natal` result. | `evidence/manual-qa-ledger.json` contains one entry per profile with `visible_result`, `execution_mode`, `evidence_path`, and `execution_trace`. | Python evidence assertion checks ledger/profile ID equality, route `/natal`, and non-empty execution traces. | PASS |
| AC3 | Missing birth time shows degraded UI. | Ledger row `cs310-missing-time-paris`; existing tests cover `degraded_mode=no_time`, `missing_birth_time=true`, and projection `state=degraded`. | Targeted Vitest command includes `NatalChartPage` and `natalInterpretation`; backend pytest covers `birth_input` without time. | PASS |
| AC4 | Controlled incomplete data does not crash UI. | Ledger row `cs310-controlled-incomplete`; existing tests cover incomplete data alerts, 422 handling, projection API error state, and null/absent `astro_profile`. | Targeted Vitest command includes `NatalChartPage`, `natalInterpretation`, and `natalChartApi`; backend pytest covers missing chart public error. | PASS |
| AC5 | Sensitive internal surfaces are not visible. | `evidence/sensitive-surface-ledger.json` records pass for prompt, provider, replay, admin, debug, internal payload, and raw runtime. | Sensitive-surface `rg` scan plus direct-client and inline-style scans recorded in `evidence/validation.txt`. | PASS |
| AC6 | Reproducible anomalies are closed or tracked. | `evidence/anomalies.md` records no reproducible anomaly and follow-up rule. | Python evidence assertion checks anomaly artifact exists. | PASS |
| AC7 | Frontend targeted validation passes. | No frontend code change; existing targeted tests remain the runtime proof. | `pnpm lint` and `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` recorded in validation evidence. | PASS |
| AC8 | Backend projection validation passes. | No backend code change; existing backend projection endpoint tests remain the runtime proof. | `python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short` recorded in validation evidence. | PASS |
| AC9 | QA evidence is persisted. | `evidence/baseline-summary.md`, `profile-set.json`, `manual-qa-ledger.json`, `sensitive-surface-ledger.json`, `anomalies.md`, `browser-equivalent-notes.md`, and `validation.txt`. | Capsule validation and Python evidence assertion recorded in validation evidence. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
