# Final Evidence — CS-434-physical-delete-active-legacy-natal-generation-paths

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-434-physical-delete-active-legacy-natal-generation-paths
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` was already dirty.
- Story tracker row matched `Path` and source brief.
- Capsule was repaired with `condamad_prepare.py` and validated with `condamad_validate.py`.
- Pre-implementation `generated/11-code-review.md` is obsolete as implementation evidence.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated during capsule repair. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC10 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Public routes closed; `interpret()` rejects non-cached short generation before gateway. | routes/OpenAPI/architecture PASS. | PASS | No public short generation. |
| AC2 | `natal_long_free` removed from catalog and `_generate_free_short` deleted. | catalog check, service branch scan, and orchestration PASS. | PASS | Historical reads allowlisted only. |
| AC3 | Basic blocked in legacy service and adapter; seed Basic legacy removed. | product-action and runtime convergence tests PASS. | PASS | Basic uses product-action runtime. |
| AC4 | Basic prompt payload removed from legacy DTO/adapter/gateway. | negative scan and architecture PASS. | PASS | Modern theme-astral builder remains. |
| AC5 | Public fallback keys removed. | catalog/registry checks PASS. | PASS | No fallback owner for deleted keys. |
| AC6 | Obsolete active seeds removed or classified. | removal audit PASS. | PASS | Residual scripts classified. |
| AC7 | Nominal legacy tests converted. | `llm_orchestration` and adapter unit tests PASS. | PASS | Guards enforce rejection/fixture use. |
| AC8 | Public compatibility is readonly/provider-free. | TestClient mocks assert service not called. | PASS | 410 controlled response. |
| AC9 | Residual hits allowlisted. | `legacy-allowlist.md` exists and scan after persisted. | PASS | Reviewer can inspect exceptions. |
| AC10 | Anti-return guards added. | architecture/runtime/scans PASS. | PASS | Deleted paths cannot re-enter public runtime. |

## Files changed

- Public API: `backend/app/api/v1/routers/public/users.py`, `backend/app/api/v1/routers/public/natal_interpretation.py`, `backend/app/services/api_contracts/public/natal_interpretation.py`.
- Runtime/gateway/catalog: `backend/app/domain/llm/runtime/{adapter.py,contracts.py,gateway.py}`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/domain/llm/configuration/canonical_use_case_registry.py`.
- Legacy service/bootstrap: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/main.py`, `backend/app/ops/llm/bootstrap/{seed_29_prompts.py,seed_66_20_taxonomy.py}`.
- Tests/guards: `backend/tests/architecture/test_llm_legacy_extinction.py`, `backend/tests/integration/test_theme_natal_public_api_product_actions.py`, `backend/tests/llm_orchestration/{test_context_quality.py,test_resolved_execution_plan.py,test_runtime_convergence.py}`, `backend/app/tests/unit/test_ai_engine_adapter.py`, `backend/app/tests/unit/test_natal_interpretation_service_v2.py`.
- Evidence: `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/**`, generated traceability/final evidence.

## Files deleted

- No filesystem file was deleted.

## Tests added or updated

- Updated: `backend/tests/architecture/test_llm_legacy_extinction.py`.
- Updated: `backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
- Updated: `backend/tests/llm_orchestration/test_context_quality.py`, `test_resolved_execution_plan.py`, `test_runtime_convergence.py`.
- Updated: `backend/app/tests/unit/test_ai_engine_adapter.py`.
- Updated: `backend/app/tests/unit/test_natal_interpretation_service_v2.py`.

## Commands run

See `evidence/validation.txt` for exact commands and results.

- `ruff check backend`: PASS.
- `python -B -m pytest -q backend/tests/llm_orchestration --tb=short`: PASS, 270 passed, 1 skipped.
- `python -B -m pytest -q backend/tests/llm_orchestration backend/tests/integration -k "theme_natal or legacy or gateway" --tb=short`: PASS, 62 passed, 501 deselected.
- Architecture and public API TestClient guards: PASS.
- Runtime `app.routes`, `app.openapi()`, catalog checks: PASS.
- Review fix validation: `python -B -m pytest -q backend/tests/architecture/test_llm_legacy_extinction.py backend/app/tests/unit/test_natal_interpretation_service_v2.py --tb=short`: PASS, 13 passed.
- Review fix validation: zero-hit scan for `_generate_free_short`, `use_case_key = "natal_long_free"`, and short legacy use-case assignment in `interpretation_service.py`.

## Commands skipped or blocked

- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py -m integration` selected 0 tests under repository selection rules; compensated by product-action integration tests, route/OpenAPI runtime checks, and architecture guards.
- Full `python -B -m pytest -q` was not run because the capsule validation plan scopes this story to `llm_orchestration`, selected `integration`, route/OpenAPI checks, and scans.

## DRY / No Legacy evidence

- No compatibility generator, wrapper, alias, or fallback was added.
- Deleted keys are absent from prompt runtime data and fallback configs.
- Basic cannot execute via `natal_interpretation`; product-action runtime remains canonical.
- Remaining legacy hits are classified in `evidence/legacy-allowlist.md`.
- Before/after artifacts: `openapi-before.json`, `openapi-after.json`, `legacy-scan-before.txt`, `legacy-scan-after.txt`.

## Diff review

- `git diff --check -- backend _condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths _condamad/stories/story-status.md`: PASS.
- `git diff --stat -- ...`: reviewed; scoped to backend and CS-434 evidence/status.

## Final worktree status

- `git status --short`: story/backend files modified and CS-434 generated/evidence files untracked as expected; pre-existing `_condamad/run-state.json` remains dirty and was not modified for this story.

## Remaining risks

- Historical/admin `natal_interpretation` premium residues remain allowlisted and should be reviewed for a future premium cutover story.
- Some historical scripts outside startup auto-heal still mention deleted symbols; they are classified as bootstrap/script cleanup follow-up, not public runtime.

## Suggested reviewer focus

- Verify that the remaining `natal_interpretation` premium/admin allowlist is acceptable and that no public route can reach it.

## Feedback loop routing

- no-propagation: failures were local story implementation issues, resolved by tests/guards and evidence updates.
