# Story CS-427 theme-natal-product-contract-action-resolver: Theme Natal Product Contract And Action Resolver
Status: ready-to-dev

## Trigger / Source

Brief direct from `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`.
The bounded problem is product-action resolution for natal readings before any LLM provider call.

## Objective

Introduce a pure backend product contract and action resolver for theme natal readings so callers request a business action.
The resolver owns product authorization before generation contract selection.

## Target State

- `ThemeNatalReadingProductContract` describes feature, reading kind, output variant, persona mode, locale, entitlement result, and contract key.
- `ThemeNatalReadingAction` accepts only `preview`, `generate_full`, `regenerate`, and `download`.
- `ThemeNatalReadingKind` contains the stable `natal_reading` kind.
- `ThemeNatalOutputVariant` contains `free_preview`, `basic_full_reading`, and `premium_full_reading`.
- `ThemeNatalPersonaMode` is independent from output variant and never owns the schema.
- A pure resolver returns only `allowed`, `locked_paywall`, `existing_reading`, `generate_with_contract_key`, or `invalid_request`.
- The frontend no longer chooses LLM level, use case, raw plan, technical variant, or forced refresh for new product-action inputs.

## Brief Primitive Ledger

| Primitive | Source expectation | Story mapping |
|---|---|---|
| `ThemeNatalReadingProductContract` | Define a pure domain product contract. | AC1, Task 1, Contract Shape. |
| `ThemeNatalReadingAction` | Model product actions `preview`, `generate_full`, `regenerate`, `download`. | AC2, Task 1. |
| `ThemeNatalReadingKind` | Model stable reading kind `natal_reading`. | AC3, Task 1. |
| `ThemeNatalOutputVariant` | Model `free_preview`, `basic_full_reading`, `premium_full_reading`. | AC4, Task 1. |
| `ThemeNatalPersonaMode` | Keep persona separate from output variant. | AC5, Task 1. |
| Resolver input | Accept user, chart, action, fresh entitlement, locale, optional persona. | AC6, AC7, AC8, AC9, AC10, Task 2. |
| Resolver output | Return a closed decision vocabulary. | AC11, Task 2. |
| Frontend technical inputs | Refuse `use_case`, `use_case_level`, `variant_code`, `plan`, `forceRefresh`. | AC13, Task 4. |
| Product matrix | Cover free, basic, premium, preview, full, and existing reading cases. | AC6, AC7, AC8, AC9, AC10, Task 3. |
| Dependency CS-426 | Classification feeds later cutover work. | Current State Evidence, Regression Risks, References. |
| Non-goals | Provider call, slot persistence, DB migration, endpoint cutover, physical legacy removal. | Domain Boundary, Batch Migration Plan. |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-427`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs `RG-002`, `RG-005`, `RG-006`, `RG-149`, `RG-157`, `RG-164`, `RG-167` read.
- Evidence 4: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - product contract stakes and target variants checked.
- Evidence 5: `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - dependency and classification scope checked.
- Evidence 6: `backend/app/api/v1/routers/public/natal_interpretation.py` - current public route still receives `use_case_level` and `variant_code`.
- Evidence 7: `frontend/src/api/natal-chart/index.ts` - current client still sends `use_case_level` and `force_refresh`.
- Evidence 8: `backend/app/domain/theme_natal` is an expected implementation-created path.
- Evidence 9: `backend/tests/unit/domain/theme_natal` is an expected implementation-created path.
- Repository structure alert: expected implementation roots are absent at drafting time.
- Implementation will create `backend/app/domain/theme_natal` and `backend/tests/unit/domain/theme_natal` if the scope remains confirmed.
- Source-alignment evidence: objective, ACs, tasks, scans, and non-goals map back to the brief without changing the requested boundary.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Pure domain contracts for theme natal reading product resolution.
  - Pure action resolver for product decisions before LLM generation selection.
  - Unit matrix tests for free, basic, premium, preview, full, existing reading, persona, and rejected technical input cases.
  - Targeted scan of frontend and public API client surfaces to prevent new product-action DTO drift.
- Out of scope:
  - Provider calls, persistence slots, database schema, migrations, public endpoint cutover, frontend UI, i18n, styling, and build tooling.
- Explicit non-goals:
  - No public route replacement in this story.
  - No physical removal of historical generation code in this story.
  - No provider/model selection policy in this story.
  - No frontend screen, React state, or UX behavior change in this story.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only pure product contract and resolver behavior for theme natal reading actions.
  - Keep current public endpoint behavior unchanged until a later cutover story.
  - Keep entitlement consumption outside this resolver.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: `CS-426` classification evidence is missing at implementation start.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`.
  - Architecture evidence must include an `AST guard` proving no FastAPI, SQLAlchemy, frontend, or LLM gateway imports in the resolver.
  - Public DTO evidence must include a zero-hit scan for `use_case_level|variant_code|forceRefresh` on new product-action DTO roots.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, matrix cases, and `AST guard` prove resolver behavior and purity. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta. |
| Ownership Routing | yes | Domain contracts must not be placed in routers, frontend, infra, or LLM gateway modules. |
| Allowlist Exception | no | No allowlist handling is authorized for this product resolver. |
| Contract Shape | yes | Contract fields, action enum, variants, persona mode, and decision statuses are closed. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Technical frontend inputs must not enter new backend product-action contracts. |
| Persistent Evidence | yes | Validation and scan artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Product contract fields are closed. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC2 | Product action values are closed. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC3 | Reading kind is `natal_reading`. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC4 | Output variants match the target set. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC5 | Persona mode stays separate. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC6 | Free preview resolves `free_preview`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC7 | Free full generation resolves paywall. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC8 | Basic preview avoids short generation. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks `natal_interpretation_short`. |
| AC9 | Basic full resolves target variant. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC10 | Premium full resolves target variant. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC11 | Resolver decision statuses are closed. | Evidence profile: json_contract_shape; `pytest` checks `tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`. |
| AC12 | Resolver has no framework imports. | Evidence profile: ast_architecture_guard; `python` AST guard; `rg` checks forbidden imports. |
| AC13 | Technical request inputs are rejected. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks `use_case_level|variant_code|forceRefresh`. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence artifact paths. |

## Implementation Tasks

- [ ] Task 1: Add pure domain contract types for product, action, kind, output variant, and persona mode. (AC: AC1, AC2, AC3, AC4, AC5)
- [ ] Task 2: Implement the pure product action resolver with the closed decision vocabulary. (AC: AC6, AC7, AC8, AC9, AC10, AC11)
- [ ] Task 3: Add matrix tests for free, basic, premium, preview, full, existing reading, persona, and entitlement cases. (AC: AC6, AC7, AC8, AC9, AC10, AC11)
- [ ] Task 4: Add rejection tests for `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh`. (AC: AC13)
- [ ] Task 5: Add an AST architecture guard for resolver purity. (AC: AC12)
- [ ] Task 6: Persist before and after scan artifacts under the story evidence directory. (AC: AC14)
- [ ] Task 7: Keep public endpoint cutover and persistence changes out of the implementation diff. (AC: AC12, AC13)

## Files to Inspect First

- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - source contract.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - product architecture decision.
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - prerequisite classification scope.
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py` - fresh entitlement behavior.
- `backend/app/services/entitlement/effective_entitlement_resolver_service.py` - plan and entitlement snapshot shape.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - current adapter boundary and technical inputs.
- `frontend/src/api/natal-chart/index.ts` - current client technical input surface.
- `backend/app/domain/theme_natal` - expected implementation-created path.
- `backend/tests/unit/domain/theme_natal` - expected implementation-created path.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`.
  - `AST guard` for imports in `backend/app/domain/theme_natal`.
- Secondary evidence:
  - Targeted `rg` scans for technical request inputs and historical generation keys.
- Static scans alone are not sufficient for this story because:
  - Resolver decisions must be proven by executable product matrix cases.

## Contract Shape

- Contract type:
  - Pure backend domain product contract and resolver decision.
- Fields:
  - `feature`: fixed value `theme_natal`.
  - `reading_kind`: fixed value `natal_reading`.
  - `action`: one of `preview`, `generate_full`, `regenerate`, `download`.
  - `output_variant`: one of `free_preview`, `basic_full_reading`, `premium_full_reading`.
  - `persona_mode`: separate style/cache dimension.
  - `locale`: caller locale used by product decision and downstream contract key selection.
  - `entitlement`: fresh backend entitlement result.
  - `contract_key`: emitted only for `generate_with_contract_key`.
- Required fields:
  - `feature`, `reading_kind`, `action`, `output_variant`, `persona_mode`, `locale`, `entitlement`.
- Optional fields:
  - `contract_key` only on generation decisions.
- Status codes:
  - No new HTTP status code is introduced; current route responses remain unchanged.
- Serialization names:
  - New product-action DTOs must not serialize `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh`.
- Frontend type impact:
  - No frontend type change is in scope; scan current client surface for drift evidence only.
- Generated contract impact:
  - No OpenAPI or generated client contract is changed in this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/product-contract-before.txt`
  - `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/technical-input-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/product-contract-after.txt`
  - `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/technical-input-scan-after.txt`
- Expected invariant:
  - The only intended behavior delta is a pure resolver that maps product actions to closed product decisions.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product contract types | `backend/app/domain/theme_natal/product_contract.py` | `backend/app/api/**`, `frontend/src/**`, `backend/app/infra/**` |
| Product action resolver | `backend/app/domain/theme_natal/product_action_resolver.py` | `backend/app/services/llm_generation/**` |
| Product matrix tests | `backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py` | `backend/tests/integration/**` |
| Public DTO rejection tests | `backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py` | `frontend/src/**` |

## Mandatory Reuse / DRY Constraints

- Reuse existing entitlement snapshot concepts instead of duplicating plan lookup logic.
- Keep product variant constants in one domain module.
- Keep resolver matrix helpers in tests shared across free, basic, and premium cases.
- Do not add a second source of truth for Basic reading plan ownership.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy product-action path may be added for theme natal reading generation.
- No compatibility route path may be added for this resolver.
- No fallback route path may be added for this resolver.
- Do not accept `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh` in new product-action contracts.
- Do not call LLM gateway, provider client, SQLAlchemy, FastAPI router code, or frontend code from the resolver.
- Do not route Basic full generation through `natal_interpretation`, `natal_interpretation_short`, or `natal_long_free`.

## Reintroduction Guard

- Guard forbidden technical request inputs with:
  - `rg -n "use_case_level|variant_code|forceRefresh" backend/app/services backend/app/domain backend/tests`.
- Guard resolver purity with:
  - `python -B scripts/architecture/check_theme_natal_product_resolver_purity.py` or an equivalent collected test AST guard.
- Guard historical generation keys with:
  - `rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/domain/theme_natal backend/tests/unit/domain/theme_natal`.
- Expected result:
  - No new product-action DTO or domain contract accepts frontend technical generation inputs.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-002 `refactor-api-v1-routers` | API adapter boundary -> route logic stays out of routers -> `rg` scans and unit `pytest`. |
| RG-005 `remove-api-v1-router-logic` | Backend domain resolver -> business logic lives outside API handlers -> `AST guard` and unit `pytest`. |
| RG-006 `api-adapter-boundary-convergence` | Non-API layers -> no import from `app.api` -> `python` AST guard. |
| RG-149 `CS-350-prompt-generation-current-implementation` | Prompt-generation map -> product contract stays explicit -> `rg` scans contract keys. |
| RG-157 `CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides` | Entitlement -> no quota debit in resolver -> unit `pytest`. |
| RG-164 `CS-415` | Basic plan owner -> Basic full reads stay plan-backed -> matrix `pytest`. |
| RG-167 `CS-418` | Basic runtime engine -> Basic full resolves expected engine key -> matrix `pytest`. |

Needs-investigation:

- Resolver output names may require a later durable guardrail for "all public LLM generation passes through a versioned product/generation contract".
- `RG-047`, `RG-052`, and `RG-041` are non-applicable examples: no frontend style, CSS namespace, or documentation entitlement edit is in scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/validation.txt` | Keep final command output for review. |
| Product matrix output | `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/product-contract-after.txt` | Prove resolver decisions. |
| Technical input scan | `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/technical-input-scan-after.txt` | Prove forbidden inputs stay out. |
| Review output | `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single product resolver.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/theme_natal/__init__.py` - expose pure domain symbols.
- `backend/app/domain/theme_natal/product_contract.py` - define contract, action, kind, output variant, persona mode, and decision types.
- `backend/app/domain/theme_natal/product_action_resolver.py` - implement product action decision logic.
- `backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py` - cover matrix, purity, and technical input rejection.
- `backend/tests/unit/domain/theme_natal/test_product_action_resolver_architecture.py` - AST guard for forbidden imports.
- `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/product-contract-before.txt` - before evidence.
- `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/product-contract-after.txt` - after evidence.
- `_condamad/stories/CS-427-theme-natal-product-contract-action-resolver/evidence/technical-input-scan-after.txt` - scan evidence.

Likely tests:

- `backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py` - product matrix and rejected technical inputs.
- `backend/tests/unit/domain/theme_natal/test_product_action_resolver_architecture.py` - AST import boundary.

Files not expected to change:

- `frontend/src/**` - out of scope; only scan evidence is required.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - endpoint cutover is out of scope.
- `backend/app/infra/**` - out of scope; no persistence change is authorized.
- `backend/alembic/**` - out of scope; no migration is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: activate venv, then run from `backend`: `ruff format .`.
- VC2: activate venv, then run from `backend`: `ruff check .`.
- VC3: activate venv, then run from `backend`: `python -B -m pytest -q tests/unit -k "theme_natal and product_contract" --tb=short`.
- VC4: activate venv, then `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_product_contract_action_resolver.py`.
- VC5: activate venv, then `python -B -m pytest -q backend/tests/unit/domain/theme_natal/test_product_action_resolver_architecture.py`.
- VC6 forbidden pattern: `use_case_level|variant_code|forceRefresh`.
- VC6 allowed fixture pattern: source brief, story artifacts, and tests explicitly asserting rejection.
- VC6 scan roots: `backend/app/services`, `backend/app/domain`, `backend/tests`.
- VC6 command: `rg -n "use_case_level|variant_code|forceRefresh" backend/app/services backend/app/domain backend/tests`.
- VC6 expected false positives: rejection tests and persisted story evidence only.
- VC7 forbidden pattern: `ThemeNatalReadingProductContract|basic_full_reading|premium_full_reading|free_preview`.
- VC7 allowed fixture pattern: canonical domain module, resolver tests, and story evidence.
- VC7 scan roots: `backend/app`, `backend/tests`.
- VC7 command: `rg -n "ThemeNatalReadingProductContract|basic_full_reading|premium_full_reading|free_preview" backend/app backend/tests`.
- VC7 expected false positives: none; hits must be canonical owners or tests.
- VC8 forbidden pattern: `natal_interpretation_short|natal_long_free|natal_interpretation`.
- VC8 allowed fixture pattern: rejection tests and story evidence only.
- VC8 scan roots: `backend/app/domain/theme_natal`, `backend/tests/unit/domain/theme_natal`.
- VC8 command: `rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/domain/theme_natal backend/tests/unit/domain/theme_natal`.
- VC8 expected false positives: tests that assert rejected historical keys.

## Regression Risks

- CS-426 is currently a prerequisite story; implementation must verify its classification evidence before using its conclusions.
- The existing public route still accepts technical input names; this story must not silently cut over the route.
- Basic and Premium must not share the same final generation contract key.
- Free preview must not trigger a full generation path.
- Persona mode must not become a schema or output variant owner.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands under `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new backend application files.
- Preserve the current public endpoint behavior until a later cutover story.

## References

- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py`
- `backend/app/services/entitlement/effective_entitlement_resolver_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `frontend/src/api/natal-chart/index.ts`
