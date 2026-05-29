# Final Evidence — CS-379-stabiliser-contrat-public-generation-theme-natal

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-379-stabiliser-contrat-public-generation-theme-natal
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/run-state.json`
- Pre-existing dirty files: `_condamad/run-state.json`
- AGENTS.md files considered: root `AGENTS.md`; no `backend/AGENTS.md` present.
- Capsule generated: repaired with `condamad_prepare.py --repair-generated-only`; validation PASS.
- Story registry source alignment: `CS-379` row matched story path and source brief path.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story source unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by capsule script. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC1-AC9 evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Repaired by capsule script. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Repaired by capsule script. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Repaired by capsule script. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Current file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | POST result uses public planet-keyed `traditional_conditions` with boolean `hayz.is_hayz` and `rejoicing.is_rejoicing`. | Integration POST test PASS; `evidence/post-after.json`. | PASS |
| AC2 | Latest reload uses the same service serializer/projection. | Integration latest test PASS; `evidence/latest-after.json`. | PASS |
| AC3 | Projection has no plan input/branching. | Integration plan test PASS. | PASS |
| AC4 | No-time neutralization unchanged. | Unit no-time/projection tests PASS. | PASS |
| AC5 | Existing route paths remain in runtime `app.routes` and `app.openapi()`. | Runtime route/OpenAPI check PASS; before/after OpenAPI artifacts persisted. | PASS |
| AC6 | Provider payload enrichment boundary unchanged. | Provider payload builder tests PASS. | PASS |
| AC7 | No prompt carrier was added to touched prompt runtime path. | Scoped negative `rg` PASS: no matches. | PASS |
| AC8 | Invalid traditional public contract maps to `invalid_natal_chart_public_contract`, not HTTP success. | Integration contract-error test PASS; unit missing-boolean test PASS. | PASS |
| AC9 | Required story evidence artifacts persisted. | Evidence files present; capsule validation PASS. | PASS |

## Files changed

- `backend/app/services/chart/json_builder.py`
- `backend/app/services/user_profile/natal_chart_service.py`
- `backend/app/services/api_contracts/public/users.py`
- `backend/app/tests/integration/test_user_natal_chart_api.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added public traditional contract assertions to POST/latest integration tests.
- Added plan-independent public contract integration test.
- Added invalid public contract integration test.
- Added unit tests for missing boolean rejection and public result projection.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | repo root | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | repo root | PASS |
| `ruff format <modified python files>` | `backend` | PASS |
| `python -B -m pytest -q app/tests/unit/test_chart_json_builder.py -k "traditional_conditions or no_time or public_natal_result_contract" --tb=short` | `backend` | PASS |
| `python -B -m pytest --long -q app/tests/integration/test_user_natal_chart_api.py::<4 targeted tests> --tb=short` | `backend` | PASS |
| `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short` | `backend` | PASS |
| `ruff check .` | `backend` | PASS |
| Runtime `app.routes` / `app.openapi()` assertion | `backend` | PASS |
| Scoped prompt-carrier `rg` on provider builder/test | repo root | PASS: no matches |

## Commands skipped or blocked

- Full `python -B -m pytest -q --tb=short` not run: integration suite is large and project marks integration/regression/slow tests behind `--long`; story-specific runtime/API/provider checks were run instead.
- Frontend checks not run: story explicitly scoped frontend as witness-only and no frontend files changed.

## DRY / No Legacy evidence

- One projection owner added/reused in `backend/app/services/chart/json_builder.py`.
- POST and latest share the same service serializer path; no router-side duplicate shaping.
- No compatibility endpoint, shim, alias, prompt carrier, React masking, or fallback route added.
- Existing broad repository matches for `legacy`, `chart_json`, and `natal_data` remain outside the touched provider builder path.

## Diff review

- `git diff --stat` reviewed for story paths.
- `git diff --check` PASS for story paths.

## Final worktree status

- Modified: `_condamad/stories/story-status.md`
- Modified: backend public contract/projection/test files listed above.
- Untracked story evidence/generated files under `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/**`
- Pre-existing untracked: `_condamad/run-state.json`

## Remaining risks

- Full backend test suite not run; risk limited by targeted API/unit/provider coverage and `ruff check .`.

## Suggested reviewer focus

- Verify that the public response schema intentionally accepts the projected `result: dict` while internal service data remains typed as `NatalResult`.

## Feedback loop routing

- no-propagation: no reusable CONDAMAD process issue beyond this story's local contract evidence.
