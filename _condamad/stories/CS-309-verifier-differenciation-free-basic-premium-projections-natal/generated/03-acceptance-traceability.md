# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The expected plan matrix is documented. | `evidence/plan-matrix-before.md`, `evidence/plan-matrix-after.md` | Capsule validation PASS | PASS |
| AC2 | Free `/natal` projection states are tested. | `frontend/src/tests/natalInterpretation.test.tsx` CS-309 free test | Targeted Vitest: 122 passed | PASS |
| AC3 | Basic `/natal` projection states are tested. | `frontend/src/tests/natalInterpretation.test.tsx` CS-309 basic test | Targeted Vitest: 122 passed | PASS |
| AC4 | Premium `/natal` projection states are tested. | `frontend/src/tests/natalInterpretation.test.tsx` CS-309 premium test | Targeted Vitest: 122 passed | PASS |
| AC5 | Backend 403 projection refusal is user-readable. | 403 is not treated as generic API error; locked alert + CTA is rendered | Targeted Vitest + backend pytest 5 passed | PASS |
| AC6 | React does not own entitlement policy. | React renders backend success/403 states; no authorization table added | Static guard `PASS_WITH_REVIEW`; no `plan_code ===` branch | PASS |
| AC7 | Upgrade CTAs use supported paths. | Projection locked state uses `UpgradeCTA` with `to="/settings/subscription"` | CS-309 free/basic tests assert CTA href | PASS |
| AC8 | Premium content is not leaked to lower plans. | Free/basic tests assert premium fixture text absent; premium test asserts content only on success | Targeted Vitest: 122 passed | PASS |
| AC9 | Backend authorization tests pass. | No backend source changed | Backend pytest: 5 passed | PASS |
| AC10 | QA evidence is persisted. | `evidence/qa-ledger.md`, `product-ambiguities.md`, `static-guards.md`, `validation.txt` | Capsule validation PASS | PASS |
