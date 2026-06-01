# Story CS-435 anti-regression-concurrency-live-replay-bigbang: Anti Regression Concurrency And Live Replay Big Bang
Status: ready-to-dev

## Trigger / Source

- Mode selected: Repo-informed story.
- Source brief: `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md`.
- Source reports:
  - `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`.
  - `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`.
- Upstream story chain: CS-426, CS-427, CS-428, CS-429, CS-430, CS-431, CS-432, CS-433, CS-434.
- Problem statement: close the natal Big Bang with executable proof that Free, Basic, concurrency, entitlement, public API,
  frontend DOM, legacy scans, and SQL/API evidence stay aligned after the contract cutover.
- Source-alignment evidence: the objective, ACs, tasks, evidence artifacts, and validation commands map the brief's replay,
  concurrency, entitlement, public visibility, legacy scan, guardrail, and count-proof stakes without narrowing the closure.

## Objective

Create the blocking anti-regression proof suite for the natal Big Bang closure. The implementation must add deterministic
backend tests, focused frontend tests, bounded scans, local replay evidence, and persisted SQL/API proof artifacts showing
that the public theme natal flow is contract-bound, accepted-only, concurrency-safe, entitlement-fresh, and non-generative
through old public generation paths.

## Target State

- Free to Basic replay produces at most one Free preview public reading for one chart.
- Free to Basic replay produces at most one Basic full reading for the same chart.
- Basic full reading is persisted with contract key, version, hash, schema, and data hash evidence.
- Public GET/list surfaces return accepted readings only.
- Concurrent `generate_full` requests share one generating slot and one accepted result.
- Quota is consumed once after accepted persistence.
- Checkout Basic or the equivalent test simulation resolves paid Basic action without `plan=free` logs.
- Rejected runs remain absent from public GET/list output.
- The old public endpoint cannot trigger public generation.
- The public DOM contains no technical leak or public legacy fallback UI.
- Evidence artifacts are persisted under the CS-435 story directory.
- `RG-173` protects the durable Big Bang public natal generation invariant in the guardrail registry.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-435`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs resolved from the local scope, not copied wholesale.
- Evidence 4: `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live failure report read.
- Evidence 5: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang target read.
- Evidence 6: `backend`, `backend/app`, `backend/tests`, `frontend`, and `frontend/src` exist in this workspace.
- Evidence 7: resolver command used with operation `validate`, domains `backend-api`, `frontend-ui`, and `llm-generation`.
- Evidence 8: `RG-173` added to `_condamad/stories/regression-guardrails.md` for the Big Bang invariant.

## Brief Primitive Ledger

| Primitive | Mapping |
|---|---|
| Anti-regression scans | AC7, AC8, AC12, tasks 1 and 9, validation scans VS1 to VS4. |
| Concurrency two clicks | AC5, AC14, task 2, backend integration pytest. |
| Single generating slot | AC5, task 2, SQL/API proof artifact. |
| Single accepted reading | AC5, task 2, replay proof artifact. |
| No double quota | AC14, task 2, quota pytest. |
| Fresh Basic entitlement | AC6, AC13, task 3, entitlement pytest and log scan. |
| Free preview replay | AC1, task 4, replay artifact. |
| Basic generate_full replay | AC2, AC3, task 4, replay artifact. |
| No post-upgrade short reading | AC4, task 5, backend and frontend tests. |
| GET/list accepted-only | AC10, AC11, task 6, TestClient/API proof. |
| Old endpoint cannot generate | AC12, task 7, app.routes/app.openapi/TestClient proof. |
| SQL/API counts | AC9, AC10, AC11, AC13, AC14, task 8, evidence artifacts. |
| Guardrail registry invariant | AC15, task 10, `RG-173`, targeted `rg` proof. |
| No product feature | Non-goal 1. |
| No redesign UI | Non-goal 2. |
| No provider optimization | Non-goal 3. |
| `_condamad/run-state.json` untouched | Non-goal 4 and validation scan. |

## Domain Boundary

- Domain: bigbang-regression-validation
- In scope:
  - Backend tests for natal public generation replay, concurrency, entitlement freshness, accepted-only reads, and quota.
  - Frontend tests for product-action usage, no post-upgrade short generation, and public DOM denylist.
  - Bounded anti-return scans over `backend/app`, `backend/tests`, and `frontend/src`.
  - Story evidence artifacts under `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence`.
  - A durable guardrail registry row for the Big Bang public generation invariant.
- Out of scope:
  - New product features, UI redesign, provider optimization, and cleanup of `_condamad/run-state.json`.
  - Broad database migration design beyond evidence needed to prove the existing Big Bang closure.
  - Changing the commercial plan model or adding new payment behavior.
- Explicit non-goals:
  - No new frontend screen or visual redesign.
  - No new provider/model integration.
  - No broad refactor of unrelated natal rendering, auth, i18n, styling, build tooling, or migration history.
  - No cleanup of `_condamad/run-state.json`.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a cross-surface regression proof suite with replay artifacts.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only validation code, anti-return guards, evidence generation scripts, and guardrail registry coverage.
  - Preserve the product-action Big Bang runtime path delivered by CS-426 through CS-434.
  - Public user behavior may change only by blocking regressed old generation paths.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the upstream CS-426 to CS-434 implementation evidence is missing or contradictory.
- Additional validation rules:
  - Runtime proof must include `pytest`, `TestClient`, `app.routes`, or `app.openapi()` for public API behavior.
  - SQL/API evidence must include counts grouped by `chart_id` and `output_variant`.
  - Frontend proof must include Vitest coverage for no technical generation controls and a public DOM denylist.
  - Scan proof must document forbidden pattern, allowed fixture pattern, roots, and expected false positives.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient`, `pytest`, and Vitest prove live public behavior. |
| Baseline Snapshot | yes | Before/after route, scan, replay, and count artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Backend, frontend, evidence, and guardrail changes must stay in canonical owners. |
| Allowlist Exception | yes | Historical scan hits must be explicitly non-generative and bounded. |
| Contract Shape | yes | Evidence artifacts have exact count, replay, concurrency, entitlement, and scan shapes. |
| Batch Migration | no | No batch migration or multi-step conversion is in scope for this proof story. |
| Reintroduction Guard | yes | Old generation symbols and frontend controls must stay absent from public runtime paths. |
| Persistent Evidence | yes | Replay, concurrency, entitlement, GET/list, scan, and validation outputs must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Replay produces at most one Free preview. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_bigbang_replay.py`. |
| AC2 | Replay produces at most one Basic full reading. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_bigbang_replay.py`. |
| AC3 | Basic full reading stores contract metadata. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_bigbang_replay.py`. |
| AC4 | Post-upgrade short reading is not created. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/integration`; `pnpm --dir frontend test`. |
| AC5 | Concurrent `generate_full` keeps one generating slot. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_concurrency.py`. |
| AC6 | Paid Basic action resolves with Basic entitlement. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration`. |
| AC7 | Old natal symbols have no public generator hit. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `backend/app frontend/src`. |
| AC8 | Public DOM exposes no technical leak. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalPublicDomGuard`. |
| AC9 | Public count grouping uses chart-variant keys. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/replay-free-basic-generate-full.md`. |
| AC10 | Public GET returns accepted readings only. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration`; `TestClient`. |
| AC11 | Public list returns accepted readings only. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration`; `app.routes`. |
| AC12 | Old public endpoint cannot generate. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/integration`; `app.openapi()`; `rg`. |
| AC13 | Basic paid action logs no `plan=free`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_entitlement_freshness.py`. |
| AC14 | Quota is debited once after accepted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC15 | `RG-173` Big Bang guardrail is registered. | Evidence profile: reintroduction_guard; `rg` checks `_condamad/stories`. |
| AC16 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |

## Implementation Tasks

- [ ] Task 1: Add blocking anti-return scans with bounded allowlist documentation. (AC: AC7, AC12)
- [ ] Task 2: Add backend concurrency tests for two simultaneous `generate_full` actions. (AC: AC5, AC14)
- [ ] Task 3: Add entitlement freshness tests after Basic checkout or deterministic simulation. (AC: AC6, AC13)
- [ ] Task 4: Add local replay coverage for Free preview to Basic full reading. (AC: AC1, AC2, AC3)
- [ ] Task 5: Add backend and frontend guards against post-upgrade short reading creation. (AC: AC4, AC8)
- [ ] Task 6: Add TestClient/API tests proving public GET/list accepted-only behavior. (AC: AC10, AC11)
- [ ] Task 7: Add app route and OpenAPI proof that old public endpoint cannot generate. (AC: AC12)
- [ ] Task 8: Generate SQL/API count artifacts for public readings, rejected runs, logs, and quota. (AC: AC9, AC10, AC11, AC13, AC14)
- [ ] Task 9: Persist replay, concurrency, entitlement, public-read, legacy-scan, and validation artifacts. (AC: AC16)
- [ ] Task 10: Keep `RG-173` backed by executable Big Bang route, contract, and scan evidence. (AC: AC15)
- [ ] Task 11: Run backend lint, backend tests, frontend lint, frontend tests, scans, and artifact checks. (AC: AC1, AC8, AC16)

## Files to Inspect First

- `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md` - source closure contract.
- `_condamad/stories/regression-guardrails.md` - local guardrail registry and `RG-173` target.
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - observed live bug and SQL evidence model.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target Big Bang architecture.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - old endpoint boundary and GET/list surface.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - public generation orchestration boundary.
- `backend/app/services/entitlement/effective_entitlement_resolver_service.py` - paid action entitlement freshness boundary.
- `backend/app/services/quota/usage_service.py` - accepted-only quota debit boundary.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - frontend action and old short-generation guard.
- `frontend/src/api/natal-chart/index.ts` - product-action client boundary.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `app.routes`, `app.openapi()`, Vitest, and persisted SQL/API artifacts.
- Secondary evidence:
  - Targeted `rg` scans for old generation symbols, public DOM technical terms, and contract markers.
- Static scans alone are not sufficient for this story because:
  - Concurrency, entitlement freshness, public read filtering, route capability, and quota debit timing require runtime proof.

## Contract Shape

- Contract type:
  - Cross-surface regression proof contract for public theme natal generation.
- Fields:
  - `chart_id`: stable chart identifier used by replay and SQL/API counts.
  - `output_variant`: one of `free_preview`, `basic_full_reading`, or `legacy_readonly`.
  - `status`: public lifecycle status, with public output restricted to `accepted`.
  - `generation_contract_key`: contract key stored for Basic full reading.
  - `generation_contract_version`: immutable contract version stored for Basic full reading.
  - `generation_contract_hash`: contract hash stored for Basic full reading.
  - `schema_version`: public schema version stored for Basic full reading.
  - `data_hash`: input data hash stored for Basic full reading.
  - `rejected_count`: count of rejected runs absent from public GET/list.
  - `quota_debit_count`: count proving a single debit after accepted.
- Required fields:
  - `chart_id`, `output_variant`, `status`, `generation_contract_key`, `generation_contract_version`,
    `generation_contract_hash`, `schema_version`, `data_hash`.
- Optional fields:
  - `legacy_readonly_reason` for historical dev data explicitly marked non-generative.
- Status codes:
  - Existing public API status codes remain unchanged except old generator attempts return the contract-bound controlled error.
- Serialization names:
  - Evidence uses exact snake_case names from backend/API artifacts.
- Frontend type impact:
  - Public TypeScript generation controls stay removed from product-action UI surfaces.
- Generated contract impact:
  - `app.openapi()` must not expose old generator controls as accepted product-action inputs.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/openapi-before.json`
  - `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/openapi-after.json`
  - `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md`
- Expected invariant:
  - The only intended surface delta is the addition of blocking proof, persisted evidence, and the missing guardrail row.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public API runtime tests | `backend/tests/integration/**` | `frontend/src/**` |
| Quota unit guard | `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` | API router logic |
| LLM orchestration scans | `backend/tests/llm_orchestration/**` | ad hoc script without pytest coverage |
| Public DOM guard | `frontend/src/tests/**` | backend test fixtures |
| Replay evidence | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/**` | `_condamad/run-state.json` |
| Big Bang guardrail | `_condamad/stories/regression-guardrails.md` | story-local note only |

## Mandatory Reuse / DRY Constraints

- Reuse existing backend fixtures, TestClient setup, DB session helpers, and integration app helpers.
- Reuse existing frontend Testing Library and Vitest test helpers.
- Reuse existing product-action client types and public natal render guards.
- Do not duplicate entitlement resolver logic inside tests; call canonical service boundaries or API surfaces.
- Do not duplicate quota arithmetic in assertions; assert observed debit records through canonical test helpers.
- Do not create parallel scan scripts when a pytest guard or bounded `rg` command can own the evidence.

## No Legacy / Forbidden Paths

- No legacy public generation route may be reintroduced.
- No compatibility public generation route may be reintroduced.
- No fallback public reading may mask a rejected provider run.
- No shim may allow raw old `use_case` prompt calls from public endpoints.
- Forbidden public generation symbols:
  - `natal_interpretation_short`
  - `natal_long_free`
  - `use_case_level`
  - `variant_code`
  - `forceRefresh`
  - `shouldRefreshShortAfterBasicUpgrade`
  - `PROMPT_FALLBACK_CONFIGS`
  - `fallback_default`
  - `EXIGENCE PREMIUM`
  - `AstroResponse_v3`
- Historical references must be bounded to fixtures, reports, old migration data, or `legacy_readonly` evidence.

## Reintroduction Guard

- Guard target:
  - Public theme natal generation must flow through product action and generation contract boundaries only.
- Forbidden paths:
  - Public POST paths that trigger raw `natal_interpretation_short`, `natal_long_free`, or raw `natal_interpretation` Basic generation.
- Required guard commands:
  - `python` checks `app.routes` for public route capability.
  - `python` checks `app.openapi()` for accepted product-action inputs.
  - `pytest` covers old endpoint no-generation behavior.
  - `rg` scans old generation symbols across bounded roots.
- Reintroduction outcome:
  - Any unclassified public generator hit blocks completion.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | Public routes -> no old wrapper generator -> `app.routes`, `pytest`, `rg`. |
| RG-018 `block-supported-family-prompt-fallbacks` | Natal LLM -> no prompt fallback owner -> `pytest`, `rg PROMPT_FALLBACK_CONFIGS`. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | Prompt fallback keys -> exact decisions -> `pytest`, classification scan. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation tests -> collected pytest paths -> validation plan. |
| RG-149 `prompt-generation-current-implementation` | Prompt cartography -> no old prompt-visible carriers -> targeted `rg`. |
| RG-150 `rejected-public-boundary` | Rejected runs -> absent from public GET/list -> `pytest`, TestClient evidence. |
| RG-152 `narrative-public-boundary` | Public readings -> no technical data leak -> backend tests and scan. |
| RG-154 `public-dom-denylist` | `/natal` DOM -> no technical leak -> `pnpm --dir frontend test`. |
| RG-155 `semantic-integrity` | Invalid readings -> rejected outside public -> `pytest`, public-read proof. |
| RG-157 `quota-on-acceptance` | Basic full quota -> one debit after accepted -> `pytest` quota test. |
| RG-164 `basic-plan-owner` | Basic selection -> `BasicNatalReadingPlan` owner -> backend pytest and scan. |
| RG-167 `basic-runtime-engine` | Basic full -> Basic engine only -> orchestration pytest and scan. |
| RG-168 `basic-public-contract` | Basic public contract -> strict public schema -> unit and architecture pytest. |
| RG-171 `basic-final-prompt-guard` | Basic prompt -> no old natal keys -> integration pytest and scan. |
| RG-172 `basic-cache-version` | Basic cache -> current editorial version -> cache pytest and scan. |
| RG-173 `bigbang-natal-contract-generation` | Public generation -> product+LLM contracts only -> pytest, routes, OpenAPI, rg. |

Notes:

- Resolver output also mentioned generic frontend/style guardrails; they are not selected because this story has no CSS migration or style delta.
- `RG-173` covers `ThemeNatalReadingProductContract` plus `LLMGenerationContract` for public natal generation.
- Non-applicable examples: i18n copy drift, visual token migration, and Stripe webhook retry semantics are outside this story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Replay proof | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/replay-free-basic-generate-full.md` | Prove Free to Basic replay results. |
| Concurrency proof | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/concurrency-proof.md` | Prove concurrency. |
| Entitlement proof | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/entitlement-freshness-proof.md` | Prove Basic plan. |
| Public read proof | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/public-get-list-accepted-only.md` | Prove public reads. |
| Legacy scan proof | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/legacy-scan-results.md` | Prove scans. |
| OpenAPI before | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/openapi-before.json` | Capture route/API baseline. |
| OpenAPI after | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/openapi-after.json` | Capture route/API proof after implementation. |
| Validation output | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/validation-output.txt` | Keep lint, tests, scans, and artifact checks. |
| Review output | `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: required
- Allowed residual hit classes:
  - Historical reports named in References.
  - Story briefs named in References.
  - Fixtures proving rejection, old-path blocking, or `legacy_readonly` behavior.
  - Non-runtime migration history that cannot call a provider or public route.
- Required fields for each residual hit:
  - file path, symbol, owner, classification, reason, runtime reachability proof, and planned disposition.
- Broad wildcard allowlists are forbidden.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` | old generator symbols | Denylist guard strings. | Permanent test fixture evidence. |
| `frontend/src/tests/natalPublicDomGuard.test.tsx` | old frontend controls | Guards proving controls stay absent may keep denylist strings. | Permanent test fixture evidence. |
| `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` | old live-test symbols | Historical evidence remains read-only. | Permanent report evidence. |
| `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md` | old Big Bang symbols | Source brief remains read-only. | Permanent source evidence. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/integration/test_theme_natal_bigbang_replay.py` - replay Free to Basic to full reading.
- `backend/tests/integration/test_theme_natal_concurrency.py` - concurrent generate_full guard.
- `backend/tests/integration/test_theme_natal_entitlement_freshness.py` - Basic entitlement freshness.
- `backend/tests/integration/test_theme_natal_public_reads.py` - GET/list accepted-only proof.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - quota after accepted guard.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - old generation symbol guard.
- `frontend/src/tests/natalInterpretation.test.tsx` - no post-upgrade short generation.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM denylist.
- `_condamad/stories/regression-guardrails.md` - add the Big Bang durable invariant.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/*.md` - persisted evidence.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/*.json` - OpenAPI snapshots.
- `_condamad/stories/CS-435-anti-regression-concurrency-live-replay-bigbang/evidence/validation-output.txt` - command output.

Likely tests:

- `backend/tests/integration/test_theme_natal_bigbang_replay.py`
- `backend/tests/integration/test_theme_natal_concurrency.py`
- `backend/tests/integration/test_theme_natal_entitlement_freshness.py`
- `backend/tests/integration/test_theme_natal_public_reads.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

Files not expected to change:

- `_condamad/run-state.json` - out of scope; must remain untouched.
- Provider clients under `backend/app/infra/providers/llm/**` - out of scope; no provider optimization.
- Frontend CSS files - out of scope; no visual redesign.
- Payment provider integration internals - out of scope unless existing checkout simulation helpers are reused by tests.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend commands:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
python -B -m pytest -q backend/tests/integration backend/tests/llm_orchestration -k "theme_natal or basic_full_reading or concurrency or entitlement" --tb=short
python -B -m pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
```

Frontend commands:

```powershell
pnpm --dir frontend test -- natalInterpretation NatalChartPage natalPublicDomGuard
pnpm --dir frontend lint
```

Runtime API proof commands:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from backend.app.main import app; assert app.routes"
python -B -c "from backend.app.main import app; assert app.openapi().get('paths')"
```

Scan commands:

- VS1 forbidden pattern: `natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation`.
- VS1 allowed fixture pattern: rejected-path tests, legacy-readonly fixtures, source briefs, and reports.
- VS1 roots: `backend/app`, `backend/tests`, `frontend/src`.
- VS1 expected false positives: tests proving blocked old paths and non-runtime evidence.

```powershell
rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation" backend/app backend/tests frontend/src
```

- VS2 forbidden pattern: `shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh`.
- VS2 allowed fixture pattern: tests proving rejected old controls and historical reports.
- VS2 roots: `frontend/src`, `backend/app`.
- VS2 expected false positives: validation tests and explicit rejection schema tests only.

```powershell
rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src backend/app
```

- VS3 forbidden pattern: `PROMPT_FALLBACK_CONFIGS|fallback_default|EXIGENCE PREMIUM|AstroResponse_v3`.
- VS3 allowed fixture pattern: denylist tests, rejected fixtures, and prompt-extinction tests.
- VS3 roots: `backend/app`, `backend/tests`.
- VS3 expected false positives: test denylist strings and non-runtime classification artifacts only.

```powershell
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_default|EXIGENCE PREMIUM|AstroResponse_v3" backend/app backend/tests
```

- VS4 required pattern: `ThemeNatalReadingProductContract|LLMGenerationContract|basic_full_reading|generation_contract_hash`.
- VS4 allowed fixture pattern: none for contract owner files; test references must map to runtime proof.
- VS4 roots: `backend/app`, `backend/tests`, `frontend/src`, `_condamad/stories/regression-guardrails.md`.
- VS4 expected false positives: story or test evidence strings only.

```powershell
rg -n "ThemeNatalReadingProductContract|LLMGenerationContract|basic_full_reading|generation_contract_hash" `
  backend/app backend/tests frontend/src _condamad/stories/regression-guardrails.md
```

Persistent artifact checks:

```powershell
.\.venv\Scripts\Activate.ps1
cd _condamad\stories\CS-435-anti-regression-concurrency-live-replay-bigbang\evidence
python -B -c "from pathlib import Path; assert Path('replay-free-basic-generate-full.md').exists()"
python -B -c "from pathlib import Path; assert Path('concurrency-proof.md').exists()"
python -B -c "from pathlib import Path; assert Path('entitlement-freshness-proof.md').exists()"
python -B -c "from pathlib import Path; assert Path('public-get-list-accepted-only.md').exists()"
python -B -c "from pathlib import Path; assert Path('legacy-scan-results.md').exists()"
```

Repository status check:

```powershell
git status --short -- _condamad _story_briefs backend frontend
```

## Regression Risks

- A replay can pass through mocked state while live entitlement cache still resolves stale Free.
- Concurrency tests can pass without proving one quota debit after accepted persistence.
- Scan hits can be over-allowed as historical evidence while still being runtime-reachable.
- Public DOM tests can miss technical leakage from a newly routed Basic payload.
- Registry update can document the invariant without an executable guard.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep backend Python commands inside the activated venv.
- Keep frontend changes behind existing React, TypeScript, Vitest, and lint conventions.
- Persist command output or concise summaries in the evidence directory.
- Do not modify `_condamad/run-state.json`.

## References

- `_story_briefs/cs-435-anti-regression-concurrency-live-replay-bigbang.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`
- `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md`
- `_condamad/stories/regression-guardrails.md`
