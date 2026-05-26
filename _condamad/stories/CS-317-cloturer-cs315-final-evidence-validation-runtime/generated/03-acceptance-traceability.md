<!-- Commentaire global: cette trace relie chaque AC CS-317 aux preuves de cloture CS-315. -->

# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | CS-315 final evidence exists. | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md` | Python status/evidence check PASS; CS-315 capsule validation PASS. | PASS |
| AC2 | CS-315 implementation review exists. | `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md` | Review verdict `CLEAN_WITH_ROUTED_DIVERGENCE`; no editorial-only review remains. | PASS |
| AC3 | Backend projection runtime suite passes. | Existing backend projection tests unchanged. | `python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short` PASS, 5 tests. | PASS |
| AC4 | Backend app runtime contract is neutral. | No backend app source changed. | `app.openapi()` and `app.routes` check PASS; `/v1/astrology/projections` present. | PASS |
| AC5 | Frontend natal projection validation passes. | Existing frontend tests unchanged. | `pnpm --dir frontend lint` PASS; Vite logged Vitest target PASS, 123 tests. | PASS |
| AC6 | React has no local plan matrix policy. | No `frontend/src/**` file changed. | Targeted scans found no CS-315 `accepted_matrix`, `frontend_policy`, `implementation_source` or `natal_projection_plan_matrix` owner in React. | PASS_WITH_LIMITATIONS |
| AC7 | CS-315 status reflects proven closure. | CS-315 `00-story.md` and `story-status.md` set to `done`. | Python status check PASS. | PASS |
| AC8 | Capsule validation passes. | CS-315 and CS-317 required generated files present. | `condamad_validate.py` PASS for CS-315; CS-317 final validation run after this trace. | PASS |
| AC9 | Product divergence is routed separately. | `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md` created. | Real-conditions backend suite PASS and documents free/basic/premium acceptance divergence. | PASS |
| AC10 | Delivery report has no residual CS-315 gap. | `_condamad/reports/CS-312-CS-316-delivery-report.md` reclassified CS-315 closure gap. | Targeted report search confirms CS-315 no longer lists missing final evidence or unrun runtime checks. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
