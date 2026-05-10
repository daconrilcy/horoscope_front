# Implementation Plan

## Current findings

- The profile hero uses a fixed `390px` avatar column and decorative absolute/fixed elements, making the avatar/orbit likely overflow candidates at narrow widths.
- The primary consultation CTA exists only in the bottom final CTA, below the hero and metrics.
- Empty public reviews currently display a non-zero average rating together with `(0 avis)` when the payload has rating but no reviews.
- Method steps render labels only.

## Selected approach

1. Add a hero consultation CTA that reuses `handleConsultationCta`.
2. Split badge groups into primary identity badges, secondary metadata and default action.
3. Adjust profile CSS locally with `minmax(0, ...)`, `max-width`, responsive avatar sizing and grid rhythm instead of global overflow masking.
4. Extend method section props to support helper text without duplicating rendering.
5. Branch reviews when `reviewCount === 0` or no public review exists.
6. Add/update tests and guards for the exact story invariants.
7. Persist after evidence and validation results.

## Frontend subagent assignment

- Owner: `frontend/**`
- Evidence files: main session owns `_condamad/**`.
- Validation expected: targeted Vitest, e2e, lint/build and scans from `generated/06-validation-plan.md`.

## Rollback strategy

- Revert only story-owned frontend hunks and generated evidence if a blocker is reached.
- Preserve pre-existing `_condamad` registry/status changes not authored by this execution.
