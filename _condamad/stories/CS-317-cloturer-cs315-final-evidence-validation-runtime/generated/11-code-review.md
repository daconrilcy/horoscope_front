<!-- Commentaire global: cette revue verifie l'implementation CS-317, ses preuves runtime et la cloture CS-315. -->

# CS-317 Implementation Review

Verdict: CLEAN_WITH_ROUTED_DIVERGENCE

Review date: 2026-05-26

## Scope reviewed

- Story: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`
- Source brief: `_story_briefs/cs-317-cloturer-cs315-final-evidence-validation-runtime.md`
- Tracker row: `_condamad/stories/story-status.md`
- CS-315 final evidence: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
- CS-315 implementation review: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/11-code-review.md`
- Runtime transcript: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- Delivery report: `_condamad/reports/CS-312-CS-316-delivery-report.md`
- Divergence brief: `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`

## Findings

No actionable implementation finding remains.

Issues corrected during this review/fix loop:

- The previous CS-317 review artifact was an editorial contract review, not an implementation review.
- CS-317 remained `ready-to-review` after passing capsule validation and after CS-315 closure evidence was produced.
- CS-317 final evidence still described `00-story.md` as `ready-to-review` and left an obsolete reviewer prompt about CS-315 closure.
- CS-317 capsule validation then required the `Suggested reviewer focus` section to remain present in final evidence.

Non-blocking routed divergence:

- The CS-315 product decision expects `client_interpretation_projection_v1` to be premium-only.
- Backend runtime evidence accepts that projection for `free`, `basic` and `premium`.
- The mismatch is explicitly routed to `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`.
- This is not a CS-317 blocker because AC9 requires separate divergence routing instead of React or backend behavior changes.

## AC alignment

| AC | Review result |
|---|---|
| AC1 | CS-315 final evidence exists and maps closure evidence. |
| AC2 | CS-315 `generated/11-code-review.md` is an implementation review with `CLEAN_WITH_ROUTED_DIVERGENCE`. |
| AC3 | Backend authorization and endpoint pytest evidence is persisted: 5 tests passed. |
| AC4 | Backend `app.openapi()` and `app.routes` neutrality evidence is persisted. |
| AC5 | Frontend lint and logged natal Vitest evidence is persisted: 123 tests passed. |
| AC6 | React-owned matrix scans are recorded; broad matches are existing type/test false positives. |
| AC7 | CS-315 story and tracker status are `done`. |
| AC8 | CS-315 and CS-317 capsule validation pass. |
| AC9 | Product/backend divergence is routed to a separate backend brief. |
| AC10 | Delivery report removes the CS-315 evidence gap and records routed backend follow-up. |

## Fresh validation evidence

- `condamad_story_validate.py ...CS-317...\00-story.md`: PASS.
- `condamad_story_lint.py --strict ...CS-317...\00-story.md`: PASS.
- `condamad_validate.py ...CS-317...`: PASS.
- `condamad_validate.py ...CS-315...`: PASS.
- `ruff check .`: PASS.
- `git diff --check`: PASS with CRLF normalization warnings only.

## Propagation Decision

no-propagation: the corrections are local to CS-317 review/status evidence. The product/backend divergence is already captured as a follow-up brief.

## Residual Risk

Backend/product owners still need to decide whether to change backend entitlement behavior or revise the CS-315 product matrix.
