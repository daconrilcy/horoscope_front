# Plan matrix before - CS-309

audit_date: 2026-05-26
route: /natal

| plan_code | projection_type | expected_state | content_visibility | backend_source | frontend_test | decision | evidence_path |
|---|---|---|---|---|---|---|---|
| free | beginner_summary_v1 | available | visible | response | frontend/src/tests/natalInterpretation.test.tsx | verified | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |
| free | client_interpretation_projection_v1 | forbidden + upgrade | hidden | 403 | frontend/src/tests/natalInterpretation.test.tsx | corrected | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |
| basic | beginner_summary_v1 | available | visible | response | frontend/src/tests/natalInterpretation.test.tsx | verified | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |
| basic | client_interpretation_projection_v1 | forbidden + upgrade | hidden | 403 | frontend/src/tests/natalInterpretation.test.tsx | corrected | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |
| premium | beginner_summary_v1 | available | visible | response | frontend/src/tests/natalInterpretation.test.tsx | verified | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |
| premium | client_interpretation_projection_v1 | available | visible | response | frontend/src/tests/natalInterpretation.test.tsx | verified | _condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-before.md |

Baseline finding: the frontend already renders available projection cards and full entitlement refusals, but a mixed success plus 403 state must keep authorized content visible while showing a readable locked upgrade state for the refused projection.
