# CONDAMAD Code Review - CS-443

## Review target

- Story: `CS-443-retirer-api-publique-natal-interpretations-legacy`
- Story file: `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/00-story.md`
- Source brief: `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`
- Tracker row: source/path match verified in `_condamad/stories/story-status.md`.
- Review type: implementation review + fix + fresh re-review.
- Final brief/code alignment pass: rerun on 2026-06-01 after timeout resume.
- Subagents: not used.

## Inputs reviewed

- `generated/10-final-evidence.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `route-consumption-audit.md`
- `evidence/validation.txt`
- `evidence/forbidden-scan-after.txt`
- Applicable guardrail: `RG-174`.
- Touched backend/frontend implementation and tests listed in final evidence.

## Review/fix iterations

- Iteration 1: implementation review found stale tests preserving the removed legacy public route as `410 Gone`.
- Fix batch: converted stale tests to strict route/OpenAPI absence guards.
- Iteration 2: fresh review after validations found no remaining actionable implementation issue.

## Findings

### CR-1 High - Stale tests still preserved the removed public endpoint as a 410 facade

- Bucket: patch
- Location:
  - `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
  - `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
  - `backend/app/tests/integration/test_natal_free_short_variant.py`
  - `backend/app/tests/integration/test_natal_interpretations_history.py`
  - `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
  - `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py`
- Source layer: acceptance / no-legacy / validation
- Evidence: tests asserted `410` or OpenAPI presence for `/v1/natal/interpretation` and success for `/v1/natal/interpretations*`.
- Impact: future regression suites could reintroduce the public compatibility facade forbidden by AC1-AC3 and the source brief.
- Fix applied: tests now assert `404`, no backend side effects, and absence from `app.routes` and OpenAPI.
- Validation: targeted backend review suite reran clean after fix.
- Status: resolved.

## Acceptance audit

| AC | Review result |
|---|---|
| AC1 | PASS - `/v1/natal/interpretation` is absent from runtime and OpenAPI; stale tests now enforce absence. |
| AC2 | PASS - `/v1/natal/interpretations*` is absent from runtime/OpenAPI; history tests now enforce unmounted routes. |
| AC3 | PASS - public OpenAPI omits historical paths; runtime assertion passed. |
| AC4 | PASS - `/v1/theme-natal/readings` remains mounted and covered by integration tests. |
| AC5 | PASS - public mapping scan remains bounded; RG-174 classifies remaining non-public/internal symbols. |
| AC6 | PASS - frontend targeted tests and lint pass; no production frontend historical URL calls found. |
| AC7 | PASS - PDF/delete/list disposition remains covered by frontend tests; no frontend fix was needed in this cycle. |
| AC8 | PASS - route consumption audit exists and remains aligned with removal. |
| AC9 | PASS - route/OpenAPI absence was rechecked from loaded app. |
| AC10 | PASS - architecture guard plus converted stale tests protect reintroduction. |

## Validation audit

Commands run during this review/fix cycle:

- Backend review/fix pytest suite from `backend`: PASS, 38 passed after one expected fix cycle.
- Backend targeted `ruff format` from `backend`: PASS, 1 file reformatted.
- `ruff check .` from `backend`: PASS.
- `pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx`: PASS, 4 files / 136 tests.
- `pnpm --dir frontend lint`: PASS.
- Runtime route/OpenAPI assertion for removed paths and `/v1/theme-natal/readings`: PASS.
- Production URL scan excluding tests: PASS, no matches; `rg` exit 1 expected.
- Production legacy symbol scan excluding tests: REVIEWED, hits are RG-174 allowed internal/admin-only or readonly persisted-row surfaces.
- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
- `git diff --check`: PASS with CRLF warnings only.
- Final brief/code alignment rerun: PASS for runtime/OpenAPI absence, production scans, backend 38-test suite,
  backend `ruff check`, frontend 136-test suite, frontend lint, story validation, and strict story lint.

Exact long commands are recorded in `evidence/validation.txt`.

Initial failed validation in this cycle:

- The first targeted backend run failed because
  `test_runtime_route_and_openapi_remove_old_public_endpoint` still expected schemas formerly exposed by the removed endpoint.
- The test was corrected to assert the modern `/v1/theme-natal/readings` operation, then the same backend command passed.

## DRY / No Legacy audit

- No compatibility route remains mounted for `/v1/natal/interpretation`.
- No route or OpenAPI path remains under `/v1/natal/interpretations`.
- No public `/v1/natal/pdf-templates` route remains.
- Stale tests no longer normalize a public `410 Gone` facade for the removed routes.
- Remaining `410` assertions target `/v1/users/me/...` routes, outside the CS-443 forbidden route list.
- RG-174 remains applicable and covered by `test_legacy_natal_generation_inventory_guard.py`.

## Feedback loop routing

- `no-propagation`: the issue was local stale test evidence for this story. It does not require a new durable guardrail, AGENTS.md update, or skill update.

## Residual risks

- Full backend and full frontend suites were not run; targeted backend/frontend suites and lint cover the changed story surface.
- `_condamad/run-state.json` was dirty before this review and remained out of scope.

## Verdict

CLEAN
