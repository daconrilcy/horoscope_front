<!-- Commentaire global: ce brief route la divergence CS-315 vers le backend sans introduire de politique React locale. -->

# CS-315 Follow-up Backend Projection Plan Divergence

Status: ready-to-dev

## Source

- Source story: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- Closure story: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`
- Decision artifact: `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- Runtime evidence: `backend/tests/api/test_projection_real_conditions.py`

## Divergence

The CS-315 product decision states that `client_interpretation_projection_v1`
is visible for `premium` and refused with upgrade for `free` and `basic`.

The backend runtime suite currently proves a different behavior:

- `backend/tests/api/test_projection_real_conditions.py::test_projection_endpoint_accepts_supported_b2c_plans`
  parametrizes `free`, `basic` and `premium`.
- The test posts `client_interpretation_projection_v1` to `/v1/astrology/projections`.
- The expected status is `200` for all three plans.
- Validation run on 2026-05-26: `9 passed in 2.66s`.

## Required Owner Decision

Backend and product owners must decide whether:

- the backend entitlement behavior should change to match the CS-315 product matrix; or
- the CS-315 product decision should be revised to accept the current backend behavior.

## Guardrails

- Do not add a React-owned entitlement matrix.
- Do not change backend authorization inside the CS-317 closure story.
- Keep CS-315 closure evidence explicit that this divergence is routed here.
