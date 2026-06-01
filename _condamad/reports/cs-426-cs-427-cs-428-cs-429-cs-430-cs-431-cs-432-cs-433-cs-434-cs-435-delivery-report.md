# Delivery Report - CS-426 to CS-435

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | 2026-06-01 14:25:56 +02:00 |
| Repository | `C:\dev\horoscope_front` |
| Branch | `main` |
| Current commit | `10ea38b6` |
| Commit range | Not evidenced |
| Stories covered | CS-426, CS-427, CS-428, CS-429, CS-430, CS-431, CS-432, CS-433, CS-434, CS-435 |
| Source documents | `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`; `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`; `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`; `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`; `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`; `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`; `_story_briefs/cs-432-public-api-cutover-product-actions.md`; `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`; `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md`; `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md` |
| Story capsules | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang`; `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver`; `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs`; `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas`; `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider`; `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow`; `_condamad/stories/CS-432-public-api-cutover-product-actions`; `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls`; `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths`; `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang` |
| Diff source | Story final evidence and implementation reviews; exact full commit range Not evidenced |
| Validation source | Story-time `generated/10-final-evidence.md`, `generated/11-code-review.md`, persisted `evidence/` files, and `_condamad/codex-runs/cs-426-final-validation.log` through `_condamad/codex-runs/cs-435-final-validation.log` |
| Audits in this series | None. User instruction says `Aucun audit dans cette serie`; no audit story directory was provided for CS-426 to CS-435. |
| Report-time validation | NOT RUN. Report generation only; no applicative code was modified or revalidated. |
| Worktree note | `git status --short` at report time showed `M _condamad/run-state.json` before this report was written. |

## 1. Executive summary

The CS-426 to CS-435 series is delivered from repository evidence. It implements the natal Big Bang transition from inventory and product-action contracts through slot/run persistence, strict generation contracts, fake-provider runtime, contract-bound gateway validation, public API cutover, frontend removal of technical generation controls, physical closure of active legacy public generation paths, and anti-regression replay/concurrency guards.

All ten stories are marked `done` in `_condamad/stories/story-status.md` with last update `2026-06-01`. Each story has `generated/10-final-evidence.md`; each story has `generated/11-code-review.md` with a final `CLEAN` verdict; and each `_condamad/codex-runs/cs-426-final-validation.log` through `cs-435-final-validation.log` records CONDAMAD story validation and strict story lint as `PASS`.

Final initiative status: `Delivered`.

Material residual gaps remain documented: no initiative commit range is evidenced; no CI run is evidenced; report-time lint/tests/build are NOT RUN; some broad default/full suites and `test:e2e` were skipped or not run in story evidence; live provider and live Stripe checkout were not invoked; and some legacy scans intentionally retain classified historical/admin/test hits rather than zero hits.

## 2. Initial context and trigger

The initiative was triggered by the need to prevent the natal Big Bang from becoming a new compatibility layer over legacy natal generation. Evidence anchors:

- CS-426 brief states the objective to freeze and classify legacy generation surfaces before destructive work: `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`.
- CS-427 through CS-432 then define product actions, persistence slots/runs, strict generation contracts, fake-provider runtime, contract-bound gateway rejection workflow, and public API cutover through their respective briefs and capsules.
- CS-433 removes frontend technical LLM generation controls from the public natal UI: `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`.
- CS-434 closes active legacy public natal generation paths and classifies residual historical/admin/script hits: `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/generated/10-final-evidence.md`.
- CS-435 adds replay, concurrency, entitlement freshness, public GET/list, frontend DOM, and No Legacy regression guards, including `RG-173`: `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/generated/10-final-evidence.md`; `_condamad/stories/regression-guardrails.md`.

No audits were performed in this series. Therefore there are no audit findings, audit risks, or audit candidates to link to implemented stories. Review/fix findings did occur and are linked below as implementation-review evidence, not audit evidence.

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| CS-426 | Freeze an inventory and classification of legacy natal generation surfaces without changing runtime behavior. | `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/00-story.md`; `generated/10-final-evidence.md` AC1-AC10 | Physical deletion and runtime behavior changes explicitly not performed; frontend/backend runtime roots unchanged. |
| CS-427 | Define the pure `theme_natal` product contract and action resolver. | `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/00-story.md`; `generated/10-final-evidence.md` AC1-AC14 | No public endpoint cutover, provider call, DB migration, or frontend edit. |
| CS-428 | Add public reading slots and LLM generation runs persistence with accepted-only public reads and concurrency/idempotency behavior. | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/00-story.md`; `generated/10-final-evidence.md` AC1-AC12 | Public API cutover intentionally out of scope; `UserNatalInterpretationModel` remains historical persistence. |
| CS-429 | Define strict generation contracts and schemas for Free preview, Basic full and Premium full. | `_condamad/stories/CS-429-theme-natal-generation-contracts-strict-schemas/00-story.md`; `generated/10-final-evidence.md` AC1-AC13 | No API, DB provider, migration, or frontend change. |
| CS-430 | Implement Basic full-reading runtime with a fake provider and slot publication path. | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/00-story.md`; `generated/10-final-evidence.md` AC1-AC18 | No local app server startup; no live provider call. |
| CS-431 | Bind the LLM gateway to resolved generation snapshots and enforce one-repair rejection workflow. | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/00-story.md`; `generated/10-final-evidence.md` AC1-AC22 | No live provider smoke, no migration, no public endpoint cutover, no frontend change. |
| CS-432 | Cut public API over to product actions and make the old public POST non-generative. | `_condamad/stories/CS-432-public-api-cutover-product-actions/00-story.md`; `generated/10-final-evidence.md` AC1-AC12 | No frontend, migration, auth, live provider QA, or dependency change. |
| CS-433 | Remove frontend technical generation controls and use product-action command bodies. | `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/00-story.md`; `generated/10-final-evidence.md` AC1-AC14 | `test:e2e` not run; backend runtime behavior not changed by this story. |
| CS-434 | Physically close active legacy public natal generation paths and classify remaining hits. | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/00-story.md`; `generated/10-final-evidence.md` AC1-AC10 | No filesystem file deleted; premium/admin/historical residues remain allowlisted for future work. |
| CS-435 | Add Big Bang anti-regression replay, concurrency, entitlement freshness, public read, frontend DOM and legacy scans. | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/00-story.md`; `generated/10-final-evidence.md` AC1-AC16 | Live Stripe checkout not invoked; app server startup not run. |

## 4. Implementation summary

CS-426 established the source inventory:

- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-generation-map.md`: maps backend route/profile/internal QA/service/runtime/seed/script surfaces and frontend trigger/API client surfaces.
- `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/evidence/legacy-surface-classification.md`: classifies prompt, seed, use-case, schema, test, script, runtime adapter, cache and persistence surfaces.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`: added as the architecture guard named in CS-426 final evidence.

CS-427 and CS-429 created the product/generation contract layer:

- `backend/app/domain/theme_natal/product_contract.py` and `product_action_resolver.py`: final evidence says these own strict product contract fields, closed actions/statuses, persona separation, and product decisions.
- `backend/app/domain/theme_natal/generation_contracts.py` and `generation_schemas.py`: final evidence says these own Free/Basic/Premium generation contracts, versioned engine profiles, prompt/validation/audit split, strict raw/public schemas, and snapshot metadata.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`: CS-429 final evidence says public projected schemas and use-case contracts were registered.

CS-428 added persistence:

- `backend/app/infra/db/models/theme_natal_reading_slot.py`, `llm_generation_run.py`, and migration `backend/migrations/versions/20260601_0142_create_theme_natal_reading_slots.py`: final evidence says these provide public reading slots, generation runs, indexes and constraints.
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`: final evidence says it implements app-lock claims, accepted-only publication, accepted-only public reads and `client_request_id` run idempotency.

CS-430 and CS-431 implemented contract-bound runtime behavior:

- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`: CS-430 final evidence says it handles accepted/rejected fake-provider modes, slot persistence, quota side effect, and terminal rejected idempotency.
- `backend/app/domain/llm/runtime/contracts.py` and `gateway.py`: CS-431 final evidence says they add `ResolvedGenerationContractSnapshot`, `ContractRepairPolicy`, `ContractBoundGenerationResult`, and `LLMGateway.execute_resolved_snapshot()`.
- CS-431 evidence also says contract metadata is persisted in `llm_generation_runs.raw_provider_response["contract_metadata"]`, while rejected attempts remain out of public slot reads.

CS-432 and CS-433 cut over public API and frontend:

- `backend/app/api/v1/routers/public/theme_natal_readings.py`, `backend/app/services/api_contracts/public/theme_natal_readings.py`, and `backend/app/services/llm_generation/natal/theme_natal_product_actions.py`: CS-432 final evidence says these expose `POST /v1/theme-natal/readings`, reject old technical fields, project controlled public states, and return old `POST /v1/natal/interpretation` as `410`.
- `frontend/src/api/natal-chart/index.ts` and `frontend/src/features/natal-chart/NatalInterpretation.tsx`: CS-433 final evidence says these omit `use_case_level`, `variant_code`, `forceRefresh`, use `action` commands, and consume controlled slot states.

CS-434 and CS-435 closed and guarded the legacy surface:

- `backend/app/api/v1/routers/public/natal_interpretation.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, and bootstrap seed files: CS-434 final evidence says active public legacy generation paths and public fallback keys were closed or classified.
- `backend/tests/integration/test_theme_natal_bigbang_replay.py`, `test_theme_natal_concurrency.py`, `test_theme_natal_entitlement_freshness.py`, `test_theme_natal_public_reads.py`, `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`, and frontend guard tests: CS-435 final evidence says these prove replay, concurrency, entitlement freshness, public accepted-only reads, DOM denylist, and legacy classification.
- `_condamad/stories/regression-guardrails.md`: contains `RG-173`, protecting Big Bang natal public LLM generation through product and LLM contracts with no raw old `use_case`.

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| CS-426 | AC1-AC10: inventory all legacy generation surfaces, classify exposure/owner/decision, persist scans, do not change runtime. | `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` | `legacy-generation-map.md`; `legacy-surface-classification.md`; `source-alignment.md`; `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` | Guard pytest PASS; `ruff check .` PASS; `git diff --check` PASS; runtime delta `NONE`; CS-426 `generated/10-final-evidence.md` | Delivered |
| CS-427 | AC1-AC14: strict product contract, closed action/status matrix, pure resolver, no technical input keys in new roots. | `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` | `product_contract.py`; `product_action_resolver.py`; unit and architecture tests | `ruff check .` PASS; product resolver tests 16 PASS; architecture test 1 PASS; technical/legacy scans PASS; final review CLEAN | Delivered |
| CS-428 | AC1-AC12: slot/run persistence, unique keys, accepted-only public reads, rejected run isolation, `client_request_id` idempotency, quota on first acceptance. | `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` | DB models, migration, `theme_natal_reading_slots.py`, integration tests, schema evidence | `ruff check .` PASS; slot integration 8 PASS; quota 5 PASS; rejected boundary 8 PASS; 42 guardrail tests PASS; Alembic head PASS | Delivered |
| CS-429 | AC1-AC13: Free/Basic/Premium contracts, strict raw/public schemas, immutable snapshot metadata, canonical registry wiring. | `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` | `generation_contracts.py`; `generation_schemas.py`; `canonical_use_case_registry.py`; tests | `ruff check .` PASS; targeted selector 48 PASS; contract test 7 PASS; orchestration test 5 PASS; guardrail suites 61 PASS; app import 230 routes | Delivered |
| CS-430 | AC1-AC18: Basic full fake-provider runtime, invalid-mode rejections, slot publication, accepted/rejected idempotency and no raw public fields. | `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` | `theme_natal_basic_full_runtime.py`; `interpretation_service.py`; integration runtime tests | `ruff check .` PASS; Basic runtime 12 PASS; integration selector 20 PASS; slots 8 PASS; invalid modes 7 PASS; final review CLEAN | Delivered |
| CS-431 | AC1-AC22: gateway executes resolved snapshot, uses snapshot engine/prompt/schema/data contracts, repair once, reject leaks/invalid facts, store contract metadata, keep public slots accepted-only. | `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md` | `contracts.py`; `gateway.py`; Basic runtime integration; orchestration helper/tests | `ruff check .` PASS; gateway/rejection 11 PASS; integration rejection 3 PASS; Basic runtime 13 PASS; selected gateway/rejection suite 82 PASS; guardrails 31 PASS; app import 230 routes | Delivered |
| CS-432 | AC1-AC12: new product-action public route, old technical fields rejected, old public POST non-generative `410`, centralized errors, OpenAPI cleaned. | `_story_briefs/cs-432-public-api-cutover-product-actions.md` | Public router, API contracts, product action service, legacy endpoint tests | `ruff check .` PASS; product-action API 6 PASS; legacy contract suite 14 PASS; routes/OpenAPI guards PASS; targeted old-field scan PASS; final review CLEAN | Delivered |
| CS-433 | AC1-AC14: frontend sends only product action commands, removes short/force technical controls, uses controlled slot states and public-only data path. | `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md` | `frontend/src/api/natal-chart/index.ts`; `NatalInterpretation.tsx`; frontend tests and scans | Targeted Vitest 135 PASS; frontend lint PASS; build PASS; router PASS; full Vitest 1308 PASS / 8 skipped; Vite HTTP 200; scans PASS | Delivered |
| CS-434 | AC1-AC10: public legacy generation paths closed, deleted keys absent from runtime/fallback configs, residual hits allowlisted, anti-return guards added. | `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md` | Public API/runtime/catalog/registry/bootstrap/test changes; `legacy-allowlist.md`; before/after OpenAPI and scans | `ruff check backend` PASS; llm orchestration 270 PASS / 1 skipped; selected legacy/gateway 62 PASS; architecture/runtime/OpenAPI/catalog checks PASS; review fix 13 PASS | Delivered |
| CS-435 | AC1-AC16: replay, concurrency, entitlement freshness, accepted-only GET/list, frontend DOM denylist, old endpoint proof, quota-on-accepted, `RG-173`. | `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md` | Backend replay/concurrency/entitlement/public-read tests; frontend DOM tests; `legacy-scan-results.md`; `RG-173` | `ruff check backend` PASS; targeted backend tests 8 PASS; selector 6 PASS; quota 6 PASS; frontend targeted 118 PASS; lint PASS; routes/OpenAPI PASS; VS scans classified PASS | Delivered |

## 6. Evidence of completion

### Code evidence

- `backend/app/domain/theme_natal/product_contract.py` / `product_action_resolver.py`: CS-427 final evidence says these are the canonical product contract and resolver owners, with closed output variants and no technical legacy keys.
- `backend/app/infra/db/models/theme_natal_reading_slot.py` / `llm_generation_run.py`: CS-428 final evidence says these define slot/run persistence and uniqueness.
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`: CS-428 final evidence says accepted-only public reads and locked publication are implemented there.
- `backend/app/domain/theme_natal/generation_contracts.py` / `generation_schemas.py`: CS-429 final evidence says these own versioned generation contracts and strict raw/public schemas.
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`: CS-430 and CS-431 final evidence say it runs Basic full fake-provider/contract-bound paths and keeps terminal rejected runs stable.
- `backend/app/domain/llm/runtime/gateway.py`: CS-431 final evidence says `execute_resolved_snapshot()` validates snapshot-bound provider output with bounded repair.
- `backend/app/api/v1/routers/public/theme_natal_readings.py`: CS-432 final evidence says it exposes the product-action public API route.
- `frontend/src/api/natal-chart/index.ts` and `frontend/src/features/natal-chart/NatalInterpretation.tsx`: CS-433 final evidence says they emit product-action command bodies and remove technical controls.
- `backend/app/api/v1/routers/public/natal_interpretation.py` and `backend/app/services/llm_generation/natal/interpretation_service.py`: CS-434 final evidence says active legacy public generation is blocked and old POST is non-generative.

### Test evidence

- CS-427: `backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py` PASS 16; `test_product_action_resolver_architecture.py` PASS 1.
- CS-428: `backend/tests/integration/test_theme_natal_reading_slots.py --long` PASS 8; `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` PASS 5; guardrail bundle PASS 42.
- CS-429: contract/orchestration selector PASS 48; dedicated contract test PASS 7; dedicated orchestration test PASS 5; guardrail suites PASS 61.
- CS-430: `test_theme_natal_basic_full_reading_runtime.py --long` PASS 12; selected integration PASS 20; slots PASS 8; invalid modes PASS 7.
- CS-431: gateway/rejection PASS 11; integration rejection PASS 3; Basic runtime PASS 13; selected gateway/rejection suite PASS 82; legacy guardrail selection PASS 31.
- CS-432: product-action API PASS 6; legacy endpoint contract suites PASS 14; OpenAPI/routes guards PASS.
- CS-433: targeted Vitest PASS 135; full Vitest PASS 1308 / 8 skipped; frontend lint/build PASS; Vite reachable HTTP 200.
- CS-434: llm orchestration PASS 270 / 1 skipped; selected integration/orchestration PASS 62; review fix guard PASS 13.
- CS-435: targeted backend tests PASS 8; selector PASS 6; quota PASS 6; frontend targeted PASS 118; route/OpenAPI guards PASS.

### Documentation evidence

- `_condamad/stories/story-status.md`: CS-426 through CS-435 rows are `done`, last update `2026-06-01`.
- `_condamad/stories/regression-guardrails.md`: contains `RG-173` for the Big Bang natal invariant.
- Each story capsule contains `generated/03-acceptance-traceability.md`, `generated/06-validation-plan.md`, `generated/10-final-evidence.md`, and `generated/11-code-review.md`.

### Operational evidence

- `_condamad/codex-runs/cs-426-final-validation.log` through `_condamad/codex-runs/cs-435-final-validation.log`: each records `CONDAMAD story validation: PASS` and `CONDAMAD story lint: PASS`.
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-after.txt`: schema inspection after Alembic upgrade, cited by CS-428 final evidence.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-after.json` and `routes-after.txt`: product-action public API/OpenAPI proof.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` and `legacy-scan-after.txt`: classified legacy-hit closure proof.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/concurrency-proof.md`, `entitlement-freshness-proof.md`, `public-get-list-accepted-only.md`, `replay-free-basic-generate-full.md`, and `legacy-scan-results.md`: replay/concurrency/public-read/legacy evidence.

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `condamad_story_validate.py` and `condamad_story_lint.py --strict` for CS-426 through CS-435 | targeted | PASS | `_condamad/codex-runs/cs-426-final-validation.log` through `cs-435-final-validation.log` | Story-time final validation logs. |
| CS-426 runtime delta and architecture guard | targeted | PASS | CS-426 `generated/10-final-evidence.md`; `evidence/initial-scans.txt` | Runtime delta `NONE`; guard added and passed. |
| CS-427 backend lint and product resolver tests | targeted | PASS | CS-427 `generated/10-final-evidence.md`; `evidence/validation.txt` | `ruff check .`, 16 product tests, 1 architecture test. |
| CS-428 backend lint, migration/schema, slot/run tests and guardrails | targeted | PASS | CS-428 `generated/10-final-evidence.md`; `evidence/validation.txt`; `evidence/schema-after.txt` | Includes Alembic head and app import. |
| CS-428 full backend `python -B -m pytest -q --tb=short` | full suite | NOT RUN | CS-428 `generated/10-final-evidence.md` | Compensated by targeted story tests, migration proof, rejected-boundary suite and RG guardrail suites. |
| CS-429 backend lint, contract/orchestration tests and scans | targeted | PASS | CS-429 `generated/10-final-evidence.md`; `evidence/validation.txt` | Full backend suite not required by capsule; no API/DB/provider/frontend surface changed. |
| CS-430 backend lint, Basic runtime tests, integration selectors and scans | targeted | PASS | CS-430 `generated/10-final-evidence.md`; `evidence/validation.txt` | Final review CLEAN. |
| CS-430 full default pytest | full suite | SKIPPED | CS-430 `generated/10-final-evidence.md` | Prior attempt timed out at 244s in Codex shell; targeted story validations passed. |
| CS-431 backend lint, gateway/rejection/integration/guardrail tests | targeted | PASS | CS-431 `generated/10-final-evidence.md`; evidence files | Integration test without `--long` deselected, rerun with `--long` passed. |
| CS-431 live provider smoke | external | SKIPPED | CS-431 `generated/10-final-evidence.md` | Explicitly excluded by story. |
| CS-432 backend lint, product-action API, legacy endpoint, OpenAPI/routes and scans | targeted | PASS | CS-432 `generated/10-final-evidence.md`; `evidence/openapi-after.json`; `evidence/routes-after.txt` | Broad old-field scans are `PASS_WITH_LIMITATIONS` because unrelated old/public billing/admin matches remain classified. |
| CS-432 full backend `pytest -q --long` | full suite | NOT RUN | CS-432 `generated/10-final-evidence.md` | Focused integration/contract/OpenAPI checks were run. |
| CS-433 frontend targeted/full Vitest, lint, build, Vite reachability and scans | targeted | PASS | CS-433 `generated/10-final-evidence.md`; `evidence/vite-dev.out.log`; `evidence/frontend-control-scan-after.txt` | Full Vitest: 1308 passed, 8 skipped. |
| CS-433 `pnpm --dir frontend test:e2e` | manual | NOT RUN | CS-433 `generated/10-final-evidence.md` | Residual browser-only PDF/menu risk documented. |
| CS-434 backend lint, orchestration, API/runtime/OpenAPI/catalog checks and scans | targeted | PASS | CS-434 `generated/10-final-evidence.md`; `evidence/validation.txt`; `evidence/legacy-scan-after.txt` | Some integration selections selected 0 tests and were compensated by product-action integration, runtime and architecture guards. |
| CS-434 full `python -B -m pytest -q` | full suite | NOT RUN | CS-434 `generated/10-final-evidence.md` | Capsule validation plan scoped to affected surfaces. |
| CS-435 backend/frontend targeted tests, lint, route/OpenAPI and scans | targeted | PASS | CS-435 `generated/10-final-evidence.md`; `evidence/validation-output.txt` | VS scans returned classified hits. |
| CS-435 live Stripe checkout | external | SKIPPED | CS-435 `generated/10-final-evidence.md` | Entitlement freshness proven by deterministic Basic gate simulation. |
| Report-time lint/tests/build | targeted | NOT RUN | This report | Report-only phase; no applicative code changed. |
| Combined CI for CS-426 through CS-435 | full suite | Not evidenced | No CI artifact provided | Local/story-time evidence only. |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- None evidenced as unresolved in final reviews. Each `generated/11-code-review.md` for CS-426 through CS-435 has final verdict `CLEAN`.
- CS-434 did not delete filesystem files, despite the story title using "physical delete"; its final evidence records "No filesystem file was deleted" and instead proves active public legacy generation closure plus classified residuals. This is treated as a documented implementation limit, not hidden completion evidence.

### Known limits

- Exact commit range is Not evidenced; only current branch `main` and current commit `10ea38b6` were observed at report time.
- Report-time validation is NOT RUN by design; this phase only writes the delivery report.
- Full backend/default suites were NOT RUN or SKIPPED for CS-428, CS-430, CS-432 and CS-434 according to their final evidence.
- CS-433 `pnpm --dir frontend test:e2e` is NOT RUN; final evidence documents browser-only PDF/menu residual risk.
- CS-431 did not run a live provider smoke; CS-435 did not invoke live Stripe checkout.
- CS-432, CS-434 and CS-435 retain classified legacy or broad-scan hits in unrelated/historical/admin/test surfaces rather than zero hits across the whole repository.
- `_condamad/run-state.json` was dirty before this report and remains outside story/report ownership.

### Assumptions

- Story-time final evidence and implementation reviews are treated as authoritative because the user constrained this phase to report generation only.
- `Delivered` is assigned at initiative level because each story is `done`, each final review is `CLEAN`, required scoped validations passed, and skipped/external validations are explicitly documented as gaps, external checks, or out-of-scope story decisions.

## 9. Residual risks

- Combined-release validation risk: there is no evidenced CI run or full initiative test pass across CS-426 to CS-435. Impact: integration issues outside targeted story surfaces may be missed. Evidence: report metadata and validation table. Mitigation: run CI or a release validation suite before deployment.
- Full-suite coverage gap: CS-428, CS-430, CS-432 and CS-434 document full/default backend suites as NOT RUN/SKIPPED. Impact: broader regressions outside the touched surfaces are less strongly evidenced. Mitigation: run full backend pytest in a stable environment.
- Browser e2e gap: CS-433 did not run `pnpm --dir frontend test:e2e`. Impact: PDF/menu or browser-only behavior can regress despite component coverage. Mitigation: run frontend e2e before release.
- Live provider gap: CS-431 excludes live provider smoke. Impact: contract-bound gateway logic is tested with deterministic providers, not real provider variability. Mitigation: run a controlled provider smoke when credentials/environment are available.
- Live entitlement/Stripe gap: CS-435 does not invoke live Stripe checkout. Impact: entitlement freshness is proven by deterministic Basic gate simulation, not by the live checkout loop. Mitigation: run live/prod-like entitlement QA separately.
- Legacy residual risk: CS-434 and CS-435 preserve classified historical/admin/test/script hits. Impact: future work could accidentally treat allowlisted residue as nominal. Evidence: `legacy-allowlist.md` and `legacy-scan-results.md`. Mitigation: review allowlists and plan premium/admin/script cleanup if those surfaces become product-critical.

## 10. Evidence gaps

- Full initiative commit range: Not evidenced.
- Combined CI validation: Not evidenced.
- Report-time rerun of lint/tests/build: NOT RUN.
- Report-time local app startup: NOT RUN.
- Full backend pytest for CS-428, CS-432 and CS-434: NOT RUN in story evidence.
- Full default backend pytest for CS-430: SKIPPED after a prior timeout.
- Frontend e2e for CS-433: NOT RUN.
- Live provider validation for CS-431: SKIPPED / EXTERNALLY REQUIRED.
- Live Stripe checkout validation for CS-435: SKIPPED / EXTERNALLY REQUIRED.
- Audit-to-story traceability: Not applicable. User instruction states no audit in this series; no audit artifacts were provided.

## 11. Recommended next actions

1. Run a release-grade validation pass: backend full pytest, frontend lint/build/full test/e2e, and any CI job used for merge/release gates.
2. Review CS-434 `evidence/legacy-allowlist.md` and CS-435 `evidence/legacy-scan-results.md` before new natal generation work, especially premium/admin/read-only residues.
3. If environment credentials are available, add a follow-up live smoke for the contract-bound provider path and entitlement/Stripe freshness loop.
4. If release traceability is required, provide base/head commits and generate a commit-range appendix for CS-426 to CS-435.

## 12. Final delivery status

`Delivered`

CS-426 through CS-435 are evidenced as delivered because `_condamad/stories/story-status.md` marks all ten stories `done`, each capsule contains AC-level final evidence, each implementation review ends `CLEAN`, and story-time validations cover targeted backend and frontend tests, lint, builds, OpenAPI/routes checks, Alembic/schema proof, strict contract/schema tests, public API cutover checks, replay/concurrency/public-read guards, and No Legacy scans. The delivery is not a full release certification: combined CI, exact commit range, report-time revalidation, some broad suites, frontend e2e, live provider and live Stripe checks remain explicit gaps.
