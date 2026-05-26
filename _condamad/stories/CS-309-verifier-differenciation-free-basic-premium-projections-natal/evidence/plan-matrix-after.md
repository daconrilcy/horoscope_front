# Plan matrix after - CS-309

audit_date: 2026-05-26
route: /natal

| plan_code | projection_type | expected_state | content_visibility | backend_source | frontend_test | decision | evidence_path |
|---|---|---|---|---|---|---|---|
| free | beginner_summary_v1 | available | visible | response | `CS-309 free` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |
| free | client_interpretation_projection_v1 | forbidden + upgrade | hidden | 403 | `CS-309 free` | corrected | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |
| basic | beginner_summary_v1 | available | visible | response | `CS-309 basic` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |
| basic | client_interpretation_projection_v1 | forbidden + upgrade | hidden | 403 | `CS-309 basic` | corrected | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |
| premium | beginner_summary_v1 | available | visible | response | `CS-309 premium` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |
| premium | client_interpretation_projection_v1 | available | visible | response | `CS-309 premium` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` |

After state: mixed success plus backend 403 keeps authorized projection content visible, hides refused premium projection content, shows a readable locked state, and routes the upgrade CTA to `/settings/subscription`.
