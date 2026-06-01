# Final Evidence - CS-440-zero-hit-legacy-natal-tests-guards

<!-- Commentaire global: cette preuve finale documente l'implementation CS-440 prete pour review. -->

## Story status

- Validation outcome: BLOCKED_BY_REVIEW_FINDINGS
- Ready for review: yes
- Story key: CS-440-zero-hit-legacy-natal-tests-guards
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards`
- Status tracker: `ready-to-review`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Source brief verified in `story-status.md`: `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`
- Initial `git status --short`: `_condamad/run-state.json` was already modified before this run and stayed out of scope.
- Capsule: missing generated files repaired with `condamad_prepare.py --repair-generated-only`; `condamad_validate.py` PASS.
- Applicable guardrails: `RG-001`, `RG-010`, `RG-012`, `RG-014`, `RG-018`, `RG-021`, `RG-149`, `RG-153`, `RG-154`, `RG-170`, `RG-173`; new `RG-174`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired generated capsule file. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC11 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Story validation commands refined in final evidence. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No legacy stance applied. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## Implementation evidence

- Added `RG-174` durable invariant for "Legacy natal deleted: zero public/runtime hit".
- Closed CS-434 broad allowlist and superseded CS-435 classified scan with CS-440 audit/report ownership.
- Added architecture guards `test_legacy_natal_runtime_hits_are_explicitly_authorized` and `test_legacy_natal_test_hits_are_explicitly_authorized`.
- Renamed legacy-named evaluation fixture directories to generic structured-output fixtures.
- Renamed anti-return tests: `test_old_public_route_is_removed_or_gone` and frontend `test_theme_natal_contract_is_only_public_generation_path`.
- Fixed `tests/integration/test_theme_natal_public_reads.py` to use `tests.integration.app_db.open_app_db_session()` and a valid persisted payload under `TestClient`.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | CS-434/CS-435 allowlists closed or superseded by CS-440 audit. | Architecture guard + OpenAPI/routes import evidence. | PASS | Runtime old-key strings remain only in classified readonly/admin/guard owners. |
| AC2 | No new nominal short prompt test; remaining hits classified by exact test owner. | Architecture guard + bounded scans. | BLOCKED | Residual Basic/readonly tests remain while CS-436/CS-438 are not done. |
| AC3 | No new nominal long-free prompt test; remaining hits classified by exact test owner. | `test_llm_legacy_extinction.py`; architecture guard. | BLOCKED | Residual free/admin/readonly tests remain while CS-436/CS-437 are not done. |
| AC4 | Old public route test renamed anti-return; modern mocks classified. | Backend integration tests; adapter mock scan. | BLOCKED | Positive adapter/service mocks remain in Basic/runtime tests. |
| AC5 | Public refresh controls and public `use_case_level` absent. | Bounded scans PASS; architecture guard classifies old keys. | PASS | Classified backend old-key strings are readonly, admin-only, or rejection guards. |
| AC6 | `variant_code` rejected as public command field. | Product-action OpenAPI and rejection tests. | PASS | |
| AC7 | Anti-return names added. | Backend/frontend targeted tests PASS. | PASS | |
| AC8 | Unauthorized runtime hit guard added. | Architecture tests PASS. | PASS | |
| AC9 | `RG-174` added. | Architecture guard checks registry. | PASS | |
| AC10 | Final report and audit persisted. | Architecture guard checks report/audit. | PASS | |
| AC11 | Old public route returns gone. | `test_old_public_route_is_removed_or_gone`. | PASS | |

Review note for AC1-AC5: old key string hits are now guarded by exact runtime and test/fixture owner classification.
Closure still blocks because CS-436, CS-437, and CS-438 are not `done`, and positive legacy service/adapter tests still exist.

## Files changed

- Backend tests: `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`, `backend/app/tests/unit/test_eval_harness_natal.py`.
- Backend fixtures: renamed old natal eval fixture directories to `generic_structured_short` and `generic_structured_complete`.
- Evidence: CS-440 audit, acceptance traceability, final evidence, and code review artifact.

## Files deleted

- None intentionally deleted; old fixture paths were renamed to neutral generic paths.

## Tests added or updated

- Added runtime, test-hit, and fixture-directory architecture assertions in `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`.
- Updated integration route/read tests in `backend/tests/integration/test_theme_natal_public_api_product_actions.py` and `backend/tests/integration/test_theme_natal_public_reads.py`.
- Updated frontend DOM guard test name in `frontend/src/tests/natalPublicDomGuard.test.tsx`.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --repair-generated-only` | repo root | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py <capsule>` | repo root | PASS |
| `ruff format tests\architecture\test_legacy_natal_generation_inventory_guard.py tests\integration\test_theme_natal_public_api_product_actions.py tests\integration\test_theme_natal_public_reads.py` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py app/tests/unit/test_eval_harness_natal.py --tb=short` | `backend` | PASS, 13 passed |
| `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short` | `backend` | PASS, rerun in final validation |
| `python -B -m pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short` | `backend` | PASS, 33 passed |
| `python -B -m pytest -q --long tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_public_reads.py --tb=short` | `backend` | PASS, 9 passed |
| `python -B -m pytest -q --long tests/unit/domain/theme_natal tests/integration/test_theme_natal_basic_full_reading_runtime.py --tb=short` | `backend` | PASS, 37 passed |
| `pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx` | repo root | PASS, 136 passed |
| `pnpm --dir frontend lint` | repo root | PASS |
| Bounded runtime scans for refresh controls and public `use_case_level` | repo root | PASS no matches |
| Bounded old key scan over backend/app + frontend/src excluding tests | repo root | CLASSIFIED matches only, enforced by architecture guard |

## Commands skipped or blocked

- Full backend `python -B -m pytest -q --tb=short` not run: story validation plan is targeted and integration tests require `--long`; targeted backend suites covering the story passed.
- Full frontend test suite not run: capsule required natal-specific tests; targeted frontend suite and lint passed.
- Local dev server not started: this story changes tests, guards and evidence only; FastAPI import, OpenAPI, route and `TestClient` checks were executed.

## DRY / No Legacy evidence

- No shim, alias, compatibility wrapper or fallback generation path added.
- Remaining legacy strings are classified by exact owner and fail the architecture guard if they appear in any new unauthorized runtime path.
- Public theme natal contract continues to reject `use_case_level`, `variant_code`, `plan`, and `forceRefresh`.

## Diff review

- `_condamad/run-state.json` remains a pre-existing dirty file and was not touched intentionally.
- No unrelated source refactor performed.

## Final worktree status

- Modified by this review/fix pass: backend architecture guard, eval harness test/fixtures, and CS-440 evidence.
- Pre-existing dirty file: `_condamad/run-state.json`.

## Remaining risks

- CS-440 cannot be marked `done` while CS-436, CS-437 and CS-438 remain `ready-to-dev`.
- Positive Basic/free tests still exercise `NatalInterpretationService.interpret` or `AIEngineAdapter.generate_natal_interpretation`.

## Review result

- Fresh implementation review iteration 2: BLOCKED by unresolved prerequisite stories and residual positive legacy tests.

## Suggested reviewer focus

- Do not close CS-440 until CS-436, CS-437, and CS-438 are implemented or explicitly recut out of scope.
- Re-review positive Basic/free tests around `NatalInterpretationService.interpret` and `AIEngineAdapter.generate_natal_interpretation`.
