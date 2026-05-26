# QA ledger - CS-309

audit_date: 2026-05-26
route: /natal

| plan_code | projection_type | expected_state | visible_message | content_visibility | backend_source | frontend_test | decision | evidence_path |
|---|---|---|---|---|---|---|---|---|
| free | beginner_summary_v1 | available | `Repère free visible` | visible | response | `frontend/src/tests/natalInterpretation.test.tsx` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
| free | client_interpretation_projection_v1 | forbidden + upgrade | `Cette lecture demande une formule plus avancée.` + CTA | hidden | 403 | `frontend/src/tests/natalInterpretation.test.tsx` | corrected | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
| basic | beginner_summary_v1 | available | `Repère basic visible` | visible | response | `frontend/src/tests/natalInterpretation.test.tsx` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
| basic | client_interpretation_projection_v1 | forbidden + upgrade | `Cette lecture demande une formule plus avancée.` + CTA | hidden | 403 | `frontend/src/tests/natalInterpretation.test.tsx` | corrected | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
| premium | beginner_summary_v1 | available | `Résumé premium disponible` | visible | response | `frontend/src/tests/natalInterpretation.test.tsx` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
| premium | client_interpretation_projection_v1 | available | `Lecture premium réservée` | visible | response | `frontend/src/tests/natalInterpretation.test.tsx` | verified | `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/qa-ledger.md` |
