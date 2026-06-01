# CS-432 Implementation Review

<!-- Commentaire global: cet artefact consigne la review d'implementation CONDAMAD de CS-432. -->

Verdict: CLEAN after review/fix iteration 2.

Implementation evidence classification: final implementation review evidence.

## Scope Reviewed

- Story: `_condamad/stories/CS-432-public-api-cutover-product-actions/00-story.md`
- Source brief: `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- Tracker row: `_condamad/stories/story-status.md` entry `CS-432`
- Guardrails reviewed: `RG-002`, `RG-004`, `RG-005`, `RG-006`, `RG-150`, `RG-157`
- Non-applicable guardrail: `RG-170`, because no frontend `/natal` DOM, sources, legal mentions, or CSS surface is touched.

## Iteration 1 Findings

- FAIL - Existing legacy endpoint integration tests still expected `POST /v1/natal/interpretation` to generate, consume quota,
  or return old runtime errors. This contradicted AC9 and the brief cutover objective.
- FAIL - Old POST OpenAPI still exposed a `200` success response and legacy request body instead of documenting the endpoint as gone.

## Fixes Applied

- `backend/app/api/v1/routers/public/natal_interpretation.py` now rejects old POST calls before any chart, entitlement, gateway,
  provider, or legacy interpretation service access.
- Old POST OpenAPI now documents `410` only for the gone command surface and exposes no legacy request body.
- Historical old-endpoint tests under `backend/app/tests/integration` now assert `410` and no-call behavior.
- Existing public contract/runtime OpenAPI tests now assert the old POST is gone while keeping read/list routes loadable.
- Evidence artifacts were refreshed: `openapi-after.json`, `routes-after.txt`, `old-endpoint-after.txt`, scan files, and `validation.txt`.

## Fresh Review

- AC1-AC3: PASS. Runtime route and OpenAPI expose `POST /v1/theme-natal/readings` with product command fields.
- AC4/AC11: PASS. The new route/schema reject or omit `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh`.
- AC5/AC6: PASS. Basic `generate_full` reaches `basic_full_reading`; `preview` returns a controlled state without short generation.
- AC7/AC8: PASS. Accepted responses project public slot payload only; rejected runs return sanitized controlled state.
- AC9: PASS. Old `POST /v1/natal/interpretation` returns centralized `410` and no longer exposes a success request/response contract.
- AC10: PASS. `invalid_request_payload` and `natal_interpretation_endpoint_gone` use the centralized error envelope/status catalog.
- AC12: PASS. Final evidence artifacts are persisted under the CS-432 capsule.
- Guardrails: PASS. Route adapter stays thin (`RG-002`, `RG-005`), errors stay centralized (`RG-004`), non-API layers do not import
  API (`RG-006`), rejected payloads remain non-public (`RG-150`), and quota timing remains after accepted publication (`RG-157`).

## Validation Results

- `ruff format <scoped files>`: PASS.
- `ruff check .`: PASS.
- `python -B -m pytest -q --long tests\integration\test_theme_natal_public_api_product_actions.py --tb=short`: PASS, 6 passed.
- `python -B -m pytest -q --long tests\integration -k "theme_natal and api" --tb=short`: PASS, 6 passed, 284 deselected.
- Old-endpoint regression suites: PASS, 14 passed.
- Runtime route guard: PASS.
- Runtime OpenAPI guard: PASS.
- Targeted forbidden field scan: PASS, no matches in the new product-action route/schema.
- `git diff --check`: PASS with line-ending warnings only.
- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
- `condamad_validate.py --final`: PASS.

## Propagation Decision

No-propagation: the corrected issue was local to CS-432 implementation tests and OpenAPI evidence. No guardrail, AGENTS.md,
or owning skill update is required.

## Residual Risk

No remaining implementation review risk identified for the CS-432 acceptance criteria.
