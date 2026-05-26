# CS-315 Source Alignment Evidence

alignment_date: `2026-05-26`
story: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
report: `docs/architecture/natal-projection-plan-matrix-product-decision.md`

## Alignment Summary

- `observed`: the source brief asks for a product-owned `/natal` matrix decision, not a code implementation.
- `decision`: the report uses CS-309 as the accepted matrix source and keeps backend authorization as runtime source.
- `decision`: the report keeps React as renderer of backend-shaped success and 403 responses.
- `blocker`: no formal audit `F-*` or `SC-*` IDs exist for this brief-direct story; the report cites story Evidence 1-9 and source paths instead.
- `open question`: the accountable role is known, but the named product owner is not supplied.

## Source Coverage

| Source | Covered by report section |
|---|---|
| `_story_briefs/cs-315-faire-valider-matrice-produit-plans-projections-natal.md` | Executive summary, roadmap, validation plan |
| `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md` | accepted_matrix, capability matrix |
| `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md` | blockers, operational rules |
| `docs/architecture/b2c-projection-entitlement-policy.md` | registry and ownership decisions |
| `docs/architecture/official-product-primitives-public-projections.md` | projection registry decisions |
| `backend/tests/api/test_projection_authorization.py` | validation plan and runtime source |
| `frontend/src/tests/natalInterpretation.test.tsx` | frontend policy and validation plan |
