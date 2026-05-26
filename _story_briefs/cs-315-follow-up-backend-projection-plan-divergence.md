<!-- Commentaire global: ce brief archive la divergence CS-315 et la reoriente vers la specification de differenciation LLM/front sans bloquer les calculs backend. -->

# CS-315 Follow-up Plan Differentiation Without Backend Blocking

Status: ready-to-dev

## Source

- Source story: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- Closure story: `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/00-story.md`
- Decision artifact: `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- Runtime evidence: `backend/tests/api/test_projection_real_conditions.py`

## Decision Update

Product decision update:

- All calculations and interpretations must be executed for every B2C plan.
- `beginner_summary_v1` remains available for `free`, `basic` and `premium`.
- `client_interpretation_projection_v1` remains available for `free`, `basic` and `premium`.
- Differentiation happens after calculation: LLM input selection, editorial depth, precision, detail level and frontend section visibility vary by plan.
- React must not own access policy; it may render plan-differentiated sections only from backend/projection contracts.

The backend runtime suite already matches the access part of this decision:

- `backend/tests/api/test_projection_real_conditions.py::test_projection_endpoint_accepts_supported_b2c_plans`
  parametrizes `free`, `basic` and `premium`.
- The test posts `client_interpretation_projection_v1` to `/v1/astrology/projections`.
- The expected status is `200` for all three plans.
- Validation run on 2026-05-26: `9 passed in 2.66s`.

## Required Owner Decision

Backend, product and frontend owners must now define:

- which structured facts, evidence refs and interpretation inputs are passed to the LLM for each plan;
- which editorial depth profile applies to `free`, `basic` and `premium`;
- which frontend sections are visible or hidden by plan;
- how tests prove that all plans still execute full calculations while exposing different levels of interpretation.

No backend access restriction should be added for `client_interpretation_projection_v1` as part of this decision.

## Guardrails

- Do not add a React-owned entitlement matrix.
- Do not change backend authorization to block calculations or interpretation generation by plan.
- Do not remove full calculation execution for lower plans.
- Keep differentiation in explicit backend/projection/LLM/front contracts, not in ad hoc UI branching.

## Follow-up Story Shape

Create a new implementation brief to define plan-aware interpretation shaping:

- canonical contract for LLM input subsets by plan;
- editorial depth profile per plan;
- frontend section visibility contract per plan;
- tests proving full calculation execution for all plans;
- tests proving plan-differentiated output and display.
