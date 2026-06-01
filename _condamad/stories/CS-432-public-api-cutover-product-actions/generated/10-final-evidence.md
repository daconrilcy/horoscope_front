# Final Evidence — CS-432-public-api-cutover-product-actions

## Story status

- Validation outcome: passed after implementation review/fix
- Ready for review: clean
- Story key: CS-432-public-api-cutover-product-actions
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-432-public-api-cutover-product-actions`
- Source finding closure status: full-closure for the public API cutover surface in this story.
- Final implementation review: CLEAN after 2 review/fix iterations.

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-432-public-api-cutover-product-actions/00-story.md`
- Tracker row: `CS-432` matched the story path and `_story_briefs/cs-432-public-api-cutover-product-actions.md`.
- Initial `git status --short`: dirty worktree already contained CS-432 files plus unrelated `_condamad/run-state.json`, router audit, and SQL allowlist markdown changes.
- AGENTS.md considered: repository root `AGENTS.md` from `C:\dev\horoscope_front`.
- Capsule validation before implementation evidence update: PASS.

## Capsule validation

| Check | Result | Notes |
|---|---|---|
| Required generated files present | PASS | `01`, `03`, `04`, `06`, `07`, and `10` are present. |
| Pre-implementation capsule validation | PASS | `condamad_validate.py _condamad/stories/CS-432-public-api-cutover-product-actions`. |
| Final evidence validation | PASS | Initial final check found missing section metadata and stale-review wording; both were corrected, then `condamad_validate.py --final` passed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | New public router registered in `registry.py`. | `app.routes` PASS; `evidence/routes-after.txt`. | PASS |
| AC2 | OpenAPI request schema exposes product command fields. | `app.openapi()` PASS; `evidence/openapi-after.json`. | PASS |
| AC3 | Route accepts product command body and delegates to product service. | `test_theme_natal_public_api_product_actions.py` PASS. | PASS |
| AC4 | Legacy technical fields are rejected. | 422 centralized envelope test PASS. | PASS |
| AC5 | Basic `generate_full` reaches `basic_full_reading`. | Accepted-slot test checks `output_variant == "basic_full_reading"`. | PASS |
| AC6 | Basic `preview` is non-generative. | Preview no-call test PASS. | PASS |
| AC7 | Accepted responses expose public slot payload only. | Accepted response excludes provider payload tokens. | PASS |
| AC8 | Rejected runs return controlled state only. | Rejected response excludes provider debug payload. | PASS |
| AC9 | Old public endpoint is non-generative. | 410 no-call test PASS; `evidence/old-endpoint-after.txt`. | PASS |
| AC10 | Public errors use centralized shape. | `invalid_request_payload` and `natal_interpretation_endpoint_gone` assertions PASS. | PASS |
| AC11 | New schema excludes old fields. | OpenAPI PASS; targeted route/schema `rg` returned no matches. | PASS |
| AC12 | Evidence artifacts persisted. | `evidence/openapi-after.json`, `routes-after.txt`, scans, old endpoint output, validation output. | PASS |

## Files changed

- `backend/app/api/errors/catalog.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/routers/public/theme_natal_readings.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/api_contracts/public/theme_natal_readings.py`
- `backend/app/services/llm_generation/natal/theme_natal_product_actions.py`
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`
- `backend/app/tests/integration/test_natal_free_short_variant.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py`
- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
- `_condamad/stories/CS-432-public-api-cutover-product-actions/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added `backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
- Updated legacy old-endpoint integration tests to assert `410` gone/no-call behavior instead of the retired generator path.
- Updated OpenAPI contract tests to assert the old POST has no `200` response and no legacy request body.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `ruff format app\api\errors\catalog.py app\api\v1\routers\public\natal_interpretation.py app\api\v1\routers\registry.py app\api\v1\routers\public\theme_natal_readings.py app\services\api_contracts\public\theme_natal_readings.py app\services\llm_generation\natal\theme_natal_product_actions.py tests\integration\test_theme_natal_public_api_product_actions.py` | `backend` | PASS | Scoped format; final rerun reformatted `natal_interpretation.py`. |
| `ruff check .` | `backend` | PASS | All checks passed. |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_public_api_product_actions.py --tb=short` | `backend` | PASS | `6 passed`. |
| `python -B -m pytest -q --long tests\integration -k "theme_natal and api" --tb=short` | `backend` | PASS | `6 passed, 284 deselected`. |
| `python -B -m pytest -q --long tests\integration\test_natal_interpretation_public_free_basic_contract.py tests\integration\test_natal_basic_complete_v3_runtime.py app\tests\integration\test_natal_interpretation_endpoint.py app\tests\integration\test_natal_free_short_variant.py app\tests\integration\test_natal_chart_long_entitlement.py --tb=short` | `backend` | PASS | `14 passed`; legacy endpoint suites now verify `410` and no-call behavior. |
| `python -B -c <app.routes guard>` | `backend` | PASS | Registered `POST /v1/theme-natal/readings`. |
| `python -B -c <app.openapi guard>` | `backend` | PASS | Product fields present, old fields absent, old endpoint `410` only, no `200`, no requestBody. |
| `rg -n "use_case_level|variant_code|forceRefresh|plan|use_case" backend\app\services\api_contracts\public\theme_natal_readings.py backend\app\api\v1\routers\public\theme_natal_readings.py` | repo root | PASS | No matches in new product-action route/schema. |
| `rg -n "use_case_level|variant_code|forceRefresh|plan|use_case" backend\app\services\api_contracts backend\app\api\v1\routers\public` | repo root | PASS_WITH_LIMITATIONS | Broad scan persisted; matches are unrelated public billing/admin contracts or old neutralized natal owner, not the new route/schema. |
| `rg -n "410|Gone|deprecated|readonly|client_request_id" backend\app\api\v1\routers\public backend\tests` | repo root | PASS_WITH_LIMITATIONS | Matches classify expected old endpoint state, idempotence, and existing unrelated deprecation tests. |
| `rg -n "POST /v1/theme-natal/readings|ThemeNatalReadingAction|generate_full" backend\app backend\tests` | repo root | PASS | Matches are canonical product contract/resolver/runtime/route/tests. |
| `git diff --check` | repo root | PASS | Only line-ending warnings, no whitespace errors. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-432-public-api-cutover-product-actions --final` | repo root | PASS | `CONDAMAD validation: PASS`. |

## Commands skipped or blocked

- `ruff format .` skipped in favor of scoped `ruff format <modified files>` per user instruction to avoid root formatting.
- Full backend `pytest -q --long` not run; capsule asked for focused integration and contract checks, and the touched API surface is covered by the targeted suite plus runtime/OpenAPI guards.
- Local long-running API server not started; app startup was validated by importing `app.main:app`, `app.routes`, `app.openapi()`, and `TestClient`.

## DRY / No Legacy evidence

- No compatibility alias or fallback accepts `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh` on the new route.
- Product decisions remain in `app.domain.theme_natal.product_action_resolver` and `theme_natal_product_actions.py`; the route adapter stays thin.
- Old `POST /v1/natal/interpretation` now exits before legacy generation orchestration and has a no-call integration test.
- Rejected provider payload details are sanitized before public response projection.
- No frontend, migration, auth, provider live QA, or dependency change was introduced.

## Diff review

- `git diff --stat` reviewed for CS-432 surfaces.
- `git diff --check`: PASS with line-ending warnings only.
- `generated/11-code-review.md` refreshed as final implementation review evidence.

## Review/fix loop

- Iteration 1 found stale legacy integration tests and old POST OpenAPI still exposing a success request/response contract.
- Fix batch removed the active old POST request body/success contract, added no-call tests, and refreshed evidence.
- Iteration 2 found no actionable implementation, AC, guardrail, or proof issue.

## Final worktree status

- CS-432 changed/untracked files remain under the backend API/test surface and `_condamad/stories/CS-432-public-api-cutover-product-actions/**`.
- `_condamad/stories/story-status.md` updated only for row `CS-432`.
- Pre-existing unrelated dirty files still present and not modified by this story: `_condamad/run-state.json`, `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`, `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`.

## Remaining risks

- Broad legacy-field scans still include expected old public natal schema and unrelated public billing/admin uses of `plan`/`use_case`; the new route/schema is separately proven clean by OpenAPI and targeted `rg`.

## Suggested reviewer focus

- Review the public response contract in `theme_natal_product_actions.py`, especially the `readonly`, `locked`, and `rejected` state projection.

## Feedback loop routing

- No-propagation: no reusable skill, AGENTS.md, or guardrail correction was identified beyond story-local evidence updates.
