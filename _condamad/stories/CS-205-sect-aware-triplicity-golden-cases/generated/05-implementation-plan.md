<!-- Plan d'implementation CONDAMAD pour CS-205. -->

# CS-205 Implementation Plan

## Current architecture finding

The story is test/evidence-only. Existing production code already routes
triplicity through `EssentialDignityCalculator` and `PlanetDignityScoringService`.

## Selected approach

1. Inspect current runtime contracts and tests.
2. Add a dedicated test module that builds case inputs from runtime assignments.
3. Reuse `PlanetDignityScoringService` for integration proof.
4. Capture curated before/after snapshots and validation markdown.
5. Run the exact validation plan in the venv.

## Files to modify

- `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/*`
- `_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/generated/*`
- `_condamad/stories/story-status.md`

## No Legacy stance

No compatibility, fallback, local doctrine table, seed update, migration or
frontend/public JSON change is allowed.

## Rollback strategy

Remove the dedicated test/evidence files and status/evidence updates. No
production rollback should be necessary.

