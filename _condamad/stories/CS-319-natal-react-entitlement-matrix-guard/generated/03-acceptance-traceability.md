# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The frontend guard detects local natal plan policy. | `frontend/src/tests/component-architecture-guards.test.ts` adds `hasLocalNatalPlanPolicy`, branch-set classification examples, and a dedicated natal projection architecture test. | `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards` PASS, 7 tests. | PASS |
| AC2 | The guard scopes active natal projection owners. | Guard roots are limited to `features/natal-chart`, `components/natal-interpretation`, and `pages/NatalChartPage`. | Bounded scan evidence in `evidence/guard-scan-after.txt`; architecture guard PASS. | PASS |
| AC3 | Backend-shaped fixture data remains allowed. | The guard asserts `tests/natalInterpretation.test.tsx` keeps backend-shaped `ProjectionPlanCode` and `plan_code` fixtures outside active source scanning. | `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi` PASS, 123 tests. | PASS |
| AC4 | React does not own the plan matrix. | No runtime React source was changed; only a test guard was added to reject local matrix/policy/branch-set patterns. | `evidence/guard-scan-after.txt` classifies remaining hits as payload type, guard code, admin API-owner wording, or allowed fixtures. | PASS |
| AC5 | Existing natal rendering tests still pass. | No natal rendering implementation files changed. | Targeted natal Vitest PASS and full `pnpm --dir frontend test` PASS, 116 files / 1278 passed / 8 skipped. | PASS |
| AC6 | No backend or product decision file changes. | Only frontend guard and CS-319 evidence/generated files changed. | `git diff --name-only -- backend docs/architecture/natal-projection-plan-matrix-product-decision.md` produced no changed files. | PASS |
| AC7 | Story evidence artifacts are persisted. | `evidence/guard-scan-before.txt`, `evidence/guard-scan-after.txt`, `evidence/validation.txt`, and `evidence/source-alignment.md` are present. | Python path existence checks PASS; capsule validation PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
