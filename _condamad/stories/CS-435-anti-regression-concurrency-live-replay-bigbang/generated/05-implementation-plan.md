# Implementation Plan

## Initial repository findings

- Product-action route, Basic runtime, public slot service, rejected-public boundary, and quota-on-acceptance behavior already exist.
- Missing surface for this story was a dedicated CS-435 proof suite and persisted evidence artifacts.
- `RG-173` was already present in the guardrail registry from drafting.
- Existing `generated/11-code-review.md` was a drafting review and not valid implementation evidence.

## Implemented changes

- Added replay proof for one Free preview and one Basic full reading per chart/variant.
- Added concurrency proof for shared slot, serialized claim and single quota debit.
- Added entitlement freshness proof for Basic `generate_full` without `plan=free`.
- Added TestClient proof for public GET/list accepted-only behavior.
- Added runtime owner legacy-extinction guard.
- Strengthened frontend no short-generation and public DOM denylist tests.
- Persisted OpenAPI, replay, concurrency, entitlement, public-read, scan and validation evidence.

## Files modified

- Backend tests under `backend/tests/integration`, `backend/tests/llm_orchestration`, and `backend/tests/unit`.
- Frontend tests under `frontend/src/tests`.
- Story capsule/evidence under `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang`.
- Story registry `_condamad/stories/story-status.md`.

## Files deleted

- `_condamad/stories/cs-435/**`, created accidentally by helper inference and removed before implementation after path verification.

## Tests added or updated

- `test_theme_natal_bigbang_replay.py`
- `test_theme_natal_concurrency.py`
- `test_theme_natal_entitlement_freshness.py`
- `test_theme_natal_public_reads.py`
- `test_llm_legacy_extinction.py`
- `test_natal_chart_long_quota_on_acceptance.py`
- `natalInterpretation.test.tsx`
- `natalPublicDomGuard.test.tsx`

## Risk assessment

- Scan evidence is classified rather than zero-hit because historical readonly/admin/test surfaces retain old symbols.
- Live Stripe checkout is not invoked; Basic entitlement is proven through deterministic service simulation, which the story allows.

## Rollback strategy

- Remove the CS-435 test additions and story-local evidence updates.
- Revert story/status readiness from `ready-to-review` to `ready-to-dev` if a reviewer rejects the evidence classification.
