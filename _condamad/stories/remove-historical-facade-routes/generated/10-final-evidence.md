# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: remove-historical-facade-routes
- Source story: `_condamad/stories/remove-historical-facade-routes/00-story.md`
- Capsule path: `_condamad/stories/remove-historical-facade-routes/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/remove-historical-facade-routes/00-story.md`
- Initial `git status --short`: `M backend/horoscope.db`, `?? _condamad/stories/remove-historical-facade-routes/`
- Pre-existing dirty files: `backend/horoscope.db`; capsule directory was untracked before implementation.
- AGENTS.md files considered: root `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC11. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Story-specific validations added. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific forbidden symbols added. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Added `route-consumption-audit.md` and audit validator. | Validator PASS; route scan classified in audit. | PASS | Historical docs kept as external-active. |
| AC2 | Removed `/v1/ai` app/evaluation registration and deleted dedicated modules. | Router architecture tests PASS. | PASS | No repointing. |
| AC3 | Added `scripts/validate_route_removal_audit.py`. | Audit validator PASS. | PASS | No external-active delete. |
| AC4 | Added OpenAPI absence test. | OpenAPI test PASS. | PASS | Canonical chat/guidance paths remain. |
| AC5 | Deleted removed Python modules. | Import check PASS; architecture tests PASS. | PASS | Removed module is not importable. |
| AC6 | First-party clients remain on `/v1/chat/*` and `/v1/guidance/*`. | Removed-route scan returned no hits. | PASS | No first-party `/v1/ai` consumer. |
| AC7 | Removed admin export compat field/headers and front notice. | Field scan returned no hits. | PASS | Export uses canonical dimensions only. |
| AC8 | Removed nominal admin legacy audit states from backend/front types. | State scan returned no hits. | PASS | Historical route tests skipped. |
| AC9 | Removed frontend route/subnav mapping and fixed wildcard redirect. | Route scan returned no hits; routing tests PASS. | PASS | Unknown prompt segments redirect to catalog. |
| AC10 | Added architecture guards for route/module/string reintroduction. | Architecture tests PASS. | PASS | No wrapper or fallback added. |
| AC11 | Updated backend/front tests and ran lint/regression layers. | Targeted backend PASS, frontend full PASS, backend full confirmed by user. | PASS | Full regression confirmed before commit. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/remove-historical-facade-routes/route-consumption-audit.md` | added | Deletion audit. | AC1, AC3 |
| `_condamad/stories/remove-historical-facade-routes/generated/*` | added/modified | Execution and evidence capsule. | AC1-AC11 |
| `scripts/validate_route_removal_audit.py` | added | Audit validation. | AC3 |
| `backend/app/main.py` | modified | Remove historical router registration. | AC2, AC4 |
| `backend/tests/evaluation/__init__.py` | modified | Align evaluation route table. | AC2 |
| `backend/app/api/v1/routers/admin/exports.py` | modified | Remove export compat field and deprecation headers. | AC7 |
| `backend/app/api/v1/router_logic/admin/exports.py` | modified | Remove unused compat constants. | AC7 |
| `backend/app/domain/llm/configuration/admin_models.py` | modified | Remove nominal legacy audit states. | AC8 |
| `backend/app/services/llm_observability/consumption_service.py` | modified | Remove public export field. | AC7 |
| `backend/app/tests/integration/test_api_openapi_contract.py` | added | OpenAPI absence guard. | AC4 |
| `backend/app/tests/unit/test_api_router_architecture.py` | modified | Route/module/string guards. | AC2, AC5, AC10 |
| Backend tests | modified | Convert legacy-positive assertions to canonical-negative assertions. | AC7, AC8, AC11 |
| Frontend API/routes/pages/tests | modified | Remove legacy route/field consumption and update tests. | AC7, AC8, AC9 |

## Files deleted

| File | Purpose |
|---|---|
| `backend/app/api/v1/routers/public/ai.py` | Historical `/v1/ai` route facade. |
| `backend/app/api/v1/router_logic/public/ai.py` | Helpers dedicated to removed facade. |
| `backend/app/api/v1/schemas/ai.py` | Schemas dedicated to removed facade. |

## Tests added or updated

- Added `backend/app/tests/integration/test_api_openapi_contract.py`.
- Updated `backend/app/tests/unit/test_api_router_architecture.py`.
- Updated admin export/config/contract/consumption tests.
- Updated frontend routing/settings/admin prompts tests.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python scripts\validate_route_removal_audit.py _condamad\stories\remove-historical-facade-routes\route-consumption-audit.md` | repo root after venv activation | PASS | 0 | Audit OK. |
| `ruff format .` | `backend/` after venv activation | PASS | 0 | 9 files reformatted. |
| `ruff check .` | `backend/` after venv activation | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_openapi_contract.py app/tests/integration/test_admin_exports_api.py app/tests/integration/test_admin_llm_config_api.py app/tests/integration/test_contract_api.py` | `backend/` after venv activation | PASS | 0 | 36 passed. |
| `pytest -q app/tests/integration/test_chat_api.py app/tests/unit/test_llm_canonical_consumption_service.py` | `backend/` after venv activation | PASS | 0 | 39 passed. |
| Python import check for `app.api.v1.routers.public.ai` | `backend/` after venv activation | PASS | 0 | Module is not importable. |
| `rg -n "/v1/ai|ai_engine_router|app\.api\.v1\.routers\.public\.ai" frontend/src backend/app` | repo root | PASS | 1 | No hits. |
| `rg -n "use_case_compat" backend/app backend/tests frontend/src` | repo root | PASS | 1 | No hits. |
| `rg -n "legacy_maintenance|legacy_alias|legacy_registry_only" backend/app frontend/src` | repo root | PASS | 1 | No hits. |
| `rg -n "/admin/prompts/legacy" frontend/src` | repo root | PASS | 1 | No hits. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript checks passed. |
| `npm run test -- --run src/tests/AdminPromptsRouting.test.tsx src/tests/AdminSettingsPage.test.tsx src/tests/adminPromptsApi.test.ts` | `frontend/` | PASS | 0 | 10 passed. |
| `npm run test -- --run src/tests/AdminPromptsPage.test.tsx src/tests/HelpPage.test.tsx` | `frontend/` | PASS | 0 | 26 passed, 8 skipped. |
| `npm run test -- --run` | `frontend/` | PASS | 0 | 109 files passed; 1221 passed, 8 skipped. |
| `pytest -q` | `backend/` after venv activation | PASS | n/a | Full backend suite confirmed by user before commit. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | n/a | No blocked command remains after user-confirmed full test pass. | n/a | Targeted suites, frontend full suite, and user-confirmed backend full suite passed. |

## DRY / No Legacy evidence

- Deleted historical facade modules instead of preserving redirects, aliases, wrappers, or re-exports.
- Negative scans found no active `/v1/ai`, `ai_engine_router`, removed import path, removed export field, removed admin legacy states, or removed frontend route in scoped paths.
- Historical docs and story files retain references only as classified evidence.
- Unknown prompt subroutes now redirect to `/admin/prompts/catalog`.

## Diff review

- `git diff --check`: PASS.
- Expected story files changed; no dependencies, migrations, `requirements.txt`, or inline styles introduced.
- `backend/horoscope.db` was already dirty at preflight and remains dirty.

## Final worktree status

Final `git status --short` includes story changes, untracked capsule files, untracked `scripts/validate_route_removal_audit.py`, added `backend/app/tests/integration/test_api_openapi_contract.py`, and pre-existing `M backend/horoscope.db`. The status command also reports permission warnings for existing pytest artifact directories.

## Remaining risks

- Eight removed legacy-tab tests are skipped; reviewer should decide whether to delete them outright before merge.
- External clients still calling `/v1/ai/*` will receive 404.

## Suggested reviewer focus

- Confirm external deletion of `/v1/ai/*`.
- Review admin export contract removal of the historical field.
- Review whether skipped legacy-tab tests should be deleted in this same change.
