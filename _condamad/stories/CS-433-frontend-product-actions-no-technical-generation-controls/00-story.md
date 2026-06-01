# Story CS-433 frontend-product-actions-no-technical-generation-controls: Remove Frontend LLM Technical Generation Controls
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`.
- Operating mode: Repo-informed story.
- Dependency: CS-432 must provide the public product-action API contract.
- Problem statement: the natal frontend still chooses LLM generation controls instead of requesting backend product actions.
- Source-alignment evidence: this story maps every brief primitive to frontend API client, CTA, state rendering, TS type, scan, or non-goal.

## Objective

Make the natal frontend request product actions only. The frontend must stop sending technical LLM controls and must stop
triggering short generation after a Basic upgrade without an explicit user action.

## Target State

- `NatalInterpretation` no longer owns technical generation state such as `shouldRefreshShortAfterBasicUpgrade` or `forceRefresh`.
- The frontend API client exposes a product-action command for `preview`, `generate_full`, `regenerate`, and `download`.
- Public TypeScript generation request types no longer expose `useCaseLevel`, `variantCode`, `forceRefresh`, `useCase`, or technical `plan`.
- The UI consumes public slots and controlled states: `accepted`, `generating`, `failed_retriable`, `locked`, `paywall`, and `rejected`.
- Basic rendering consumes the public payload schema only and keeps sources or legal mentions deduplicated.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-433`.
- Evidence 3: `_story_briefs/cs-432-public-api-cutover-product-actions.md` - backend product-action dependency consulted.
- Evidence 4: `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - post-upgrade short generation source consulted.
- Evidence 5: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - product-action model consulted.
- Evidence 6: `frontend/src/features/natal-chart/NatalInterpretation.tsx` currently contains `shouldRefreshShortAfterBasicUpgrade`.
- Evidence 7: `frontend/src/api/natal-chart/index.ts` currently sends `use_case_level` and `force_refresh`.
- Evidence 8: `_condamad/stories/regression-guardrails.md` was consulted by targeted ID search and guardrail resolver scope.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `shouldRefreshShortAfterBasicUpgrade` | in scope | AC3, Task 1, Reintroduction Guard |
| `use_case_level` | in scope | AC1, Task 2, Reintroduction Guard |
| `variant_code` | in scope | AC2, Task 2, Regression Guardrails |
| `forceRefresh` and `force_refresh` | in scope | AC3, AC4, Task 2 |
| Technical `plan` and `use_case` request fields | in scope | AC8, AC9, Task 2 |
| Legacy generator API functions | in scope | AC14, Task 2, Removal Audit |
| Product actions `preview`, `generate_full`, `regenerate`, `download` | in scope | AC4, AC5, Task 3 |
| Slot states `accepted`, `generating`, `failed_retriable`, `locked`, `paywall`, `rejected` | in scope | AC6, AC7, Task 4 |
| Existing accepted reading | in scope | AC6, Task 4 |
| Basic public schema | in scope | AC10, Task 5 |
| Legal mentions deduplication | in scope | AC11, Task 5 |
| Backend runtime/provider | out of scope | Non-goals and validation exclusions |

## Domain Boundary

- Domain: frontend-natal
- In scope:
  - React orchestration in `frontend/src/features/natal-chart/**`.
  - Natal API client request shape in `frontend/src/api/natal-chart/**`.
  - Public natal interpretation rendering in `frontend/src/components/natal-interpretation/**`.
  - Frontend tests under `frontend/src/tests/**`.
- Out of scope:
  - Backend runtime, provider, DB schema, migrations, Stripe billing, auth, i18n copy rewrites, broad CSS restyle, and live QA.
- Explicit non-goals:
  - No backend endpoint implementation.
  - No provider prompt, schema, gateway, persistence, or quota implementation.
  - No visual redesign.
  - No new CSS outside selector support required by changed component structure.

## Operation Contract

- Operation type: remove
- Primary archetype: field-contract-removal
- Archetype reason: the story removes frontend request fields, TS request fields, and an automatic generation trigger.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Replace frontend LLM technical controls with product-action requests only.
  - Keep public rendering behavior unchanged outside controlled states and product-action CTA wiring.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: CS-432 product-action endpoint or action names are not available at implementation time.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest and request mocks prove the frontend sends product actions only. |
| Baseline Snapshot | yes | Before/after scan artifacts prove the technical controls are gone from the frontend scope. |
| Ownership Routing | yes | Product-action orchestration must stay in the frontend natal feature and API client. |
| Allowlist Exception | no | No broad allowlist handling is authorized for technical generation controls. |
| Contract Shape | yes | Product-action request shape and controlled slot states are explicit public frontend contracts. |
| Batch Migration | no | No multi-batch migration is in scope. |
| Reintroduction Guard | yes | Scans and tests must fail when technical controls return. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Frontend request bodies omit `use_case_level`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan plus `pnpm test`. |
| AC2 | Frontend request bodies omit `variant_code`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scan plus `pnpm test`. |
| AC3 | Basic upgrade does not auto-start short generation. | Evidence profile: no_legacy_contract; `pnpm test -- natalInterpretation`. |
| AC4 | Product-action command bodies omit force refresh controls. | Evidence profile: json_contract_shape; `pnpm test -- natalInterpretation`. |
| AC5 | The full CTA sends `action: "generate_full"`. | Evidence profile: json_contract_shape; `pnpm test -- natalInterpretation`. |
| AC6 | The preview CTA sends `action: "preview"`. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation NatalChartPage`. |
| AC7 | The regenerate CTA sends `action: "regenerate"`. | Evidence profile: json_contract_shape; `pnpm test -- natalInterpretation`. |
| AC8 | The download CTA sends `action: "download"`. | Evidence profile: json_contract_shape; `pnpm test -- natalInterpretation`. |
| AC9 | Public generation request types omit technical fields. | Evidence profile: frontend_typecheck_no_orphan; lint plus targeted `rg`. |
| AC10 | The UI renders controlled slot states. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalInterpretation NatalChartPage`. |
| AC11 | Basic rendering consumes only public schema fields. | Evidence profile: ast_architecture_guard; `AST guard`; `pnpm test`; `rg` scan. |
| AC12 | Legal mentions remain deduplicated. | Evidence profile: no_legacy_contract; DOM/source Vitest plus `pnpm --dir frontend build`. |
| AC13 | Removed frontend controls stay absent after implementation. | Evidence profile: reintroduction_guard; forbidden-control `rg` scans. |
| AC14 | Old generator functions are deleted or readonly non-generative compat. | Evidence profile: no_legacy_contract; audit plus `rg`. |

## Implementation Tasks

- [ ] Task 1: Remove `shouldRefreshShortAfterBasicUpgrade` and its React effect from `NatalInterpretation`. (AC: AC3, AC13)
- [ ] Task 2: Replace frontend generation request payload fields with a product-action command body. (AC: AC1, AC2, AC4, AC9)
- [ ] Task 2b: Delete old generator helpers or move them to explicit readonly non-generative compatibility. (AC: AC14)
- [ ] Task 3: Wire preview, full, regenerate, and download CTAs to explicit product actions. (AC: AC5, AC6, AC7, AC8)
- [ ] Task 4: Render public slot states without deriving LLM generation mode in the component. (AC: AC10)
- [ ] Task 5: Keep Basic public rendering and legal mention deduplication intact. (AC: AC11, AC12)
- [ ] Task 6: Update Vitest coverage for payload shape, CTA actions, Basic upgrade behavior, and controlled states. (AC: AC1, AC2, AC3, AC10)
- [ ] Task 7: Persist story evidence artifacts for scans, tests, lint, and removal audit. (AC: AC13)

## Files to Inspect First

- `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `_condamad/stories/regression-guardrails.md`

## Runtime Source of Truth

- Primary source of truth:
  - Vitest request mocks, React component behavior, the central natal API client, and an AST guard over TS sources.
- Secondary evidence:
  - Targeted `rg` scans for removed controls and product-action command names.
- Static scans alone are not sufficient for this story because:
  - CTA behavior and post-upgrade absence must be proven through component tests.

## Contract Shape

- Contract type:
  - Frontend product-action command and public slot state rendering.
- Request fields:
  - `chart_id`: chart identifier forwarded to the product-action API.
  - `action`: one of `preview`, `generate_full`, `regenerate`, or `download`.
  - `persona_profile_id`: persona identifier or `null`.
  - `locale`: UI locale forwarded from frontend state.
  - `client_request_id`: frontend idempotency identifier.
- Forbidden request fields:
  - `use_case_level`, `variant_code`, `forceRefresh`, `force_refresh`, `use_case`, and technical generation `plan`.
- Response state values:
  - `accepted`, `generating`, `failed_retriable`, `locked`, `paywall`, and `rejected`.
- Fields:
  - `chart_id`, `action`, `persona_profile_id`, `locale`, and `client_request_id`.
- Required fields:
  - `chart_id`, `action`, `locale`, and `client_request_id`.
- Optional fields:
  - `persona_profile_id`.
- Status codes:
  - The frontend client forwards product-action HTTP responses; CS-432 owns public API status behavior.
- Serialization names:
  - `action` is emitted as `action`, and no technical generation field is emitted.
- Frontend type impact:
  - Public generation request types must expose product actions, not LLM technical controls.
- Generated contract impact:
  - Generated frontend contract check is bounded to TypeScript compile/lint and API-client request mocks.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/evidence/frontend-control-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/evidence/frontend-control-scan-after.txt`
- Expected invariant:
  - The only intended frontend surface delta is removal of technical generation controls and product-action CTA wiring.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Product-action API call | `frontend/src/api/natal-chart/index.ts` | Component-local fetch in `frontend/src/features/natal-chart/**` |
| Natal interpretation orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Shared presentational components |
| Public Basic rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Backend or provider logic |
| Regression tests | `frontend/src/tests/natalInterpretation.test.tsx` | Manual-only verification |

## Mandatory Reuse / DRY Constraints

- Reuse the existing central natal API client instead of adding a second fetch helper.
- Reuse existing test setup and factories in `frontend/src/tests/natalInterpretation.test.tsx`.
- Do not duplicate product-action string unions across components and API client.
- Keep business routing out of presentational render helpers.

## No Legacy / Forbidden Paths

- No legacy frontend request field may remain for natal LLM generation.
- No compatibility wrapper may keep sending technical generation controls.
- Any retained compatibility helper must be explicitly readonly, non-generative, and unable to emit old LLM request fields.
- No fallback React effect may start generation without an explicit user action.
- No alias from product action back to `useCaseLevel` or `forceRefresh` is allowed.
- Forbidden symbols in frontend request surfaces: `use_case_level`, `variant_code`, `forceRefresh`, `force_refresh`, `useCaseLevel`, `variantCode`.
- Forbidden technical request symbols in public generation types: `useCase`, technical `plan`, `use_case`, and generation `plan`.

## Removal Classification Rules

- `canonical-active`: product-action API client, CTA handlers, public slot rendering, and public Basic schema rendering.
- `historical-facade`: old frontend generation helpers that only wrap or expose the former technical request surface.
- `dead`: frontend technical generation fields with no remaining first-party product-action consumer after the cutover.
- `external-active`: any surface documented by CS-432 or public API docs as externally consumed.
- `needs-user-decision`: any old helper consumed outside `frontend/src` or required by CS-432 compatibility.

## Removal Audit Format

The implementation must write the audit to:

`_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/evidence/removal-audit.md`

Allowed decisions for the audit are `keep`, `delete`, `replace-consumer`, and `needs-user-decision`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `shouldRefreshShortAfterBasicUpgrade` | symbol | historical-facade | `NatalInterpretation` | CTA | delete | `rg` plus Vitest | Auto short returns |
| `use_case_level` | request field | historical-facade | API client | `action` | delete | `rg` plus Vitest | Backend receives LLM control |
| `variant_code` | request field | historical-facade | API client | Backend resolver | delete | `rg` plus Vitest | Frontend selects output variant |
| `forceRefresh` or `force_refresh` | request field | historical-facade | API client | `regenerate` | delete | `rg` plus Vitest | Hidden refresh |
| Technical `useCase` or `plan` | TS request field | historical-facade | API types | Backend contract | delete | `rg` plus lint | TS API leaks internals |
| Old generator helper | function | historical-facade | API client | readonly read | delete/readonly | audit plus scan | Legacy path active |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Product action selection | Backend product-action contract from CS-432 | Frontend LLM level, use case, variant, or plan selection |
| Product action transport | `frontend/src/api/natal-chart/index.ts` | Component-local fetch, duplicate API client, compatibility wrapper |
| CTA orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Presentational rendering components |
| Public reading display | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Provider payload or backend runtime logic |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted, not repointed.
- Do not preserve wrappers that translate old technical controls into product actions.
- A retained compatibility helper is allowed only when it is readonly, non-generative, and documented in the removal audit.
- Do not keep soft-disabled controls, hidden props, aliases, or re-exports for removed fields.
- Do not retain old request fields inside tests outside bounded negative scan fixture descriptions.

## External Usage Blocker

- External usage blocker: no external frontend consumer is known from the consulted brief and reports.
- Blocking condition: stop implementation if scans find use outside `frontend/src` docs, generated clients, public API examples, or CS-432 compatibility surfaces.
- Any `external-active` item must not be deleted without an explicit user decision.
- Required proof: removal audit must include the scan command and exact consumers for every `external-active` or `needs-user-decision` item.

## Generated Contract Check

- Generated contract check: active
- Required checks:
  - `pnpm --dir frontend lint`
  - `rg -n "useCaseLevel|variantCode|forceRefresh|useCase|plan" frontend/src/api frontend/src/features/natal-chart frontend/src/tests`
- Reason: TypeScript public API and tests are the affected generated/static frontend contract surfaces.

## Reintroduction Guard

- Forbidden route or symbol set:
  - `shouldRefreshShortAfterBasicUpgrade`
  - `use_case_level`
  - `variant_code`
  - `forceRefresh`
  - `force_refresh`
  - public request `useCase`
  - technical generation `plan`
- Required deterministic guards:
  - Deterministic source: forbidden symbols in frontend TypeScript source and mocked request payloads.
  - `rg` scans over `frontend/src`.
  - Vitest coverage for CTA product actions and post-upgrade behavior.
  - An architecture guard must fail if removed frontend controls are reintroduced.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-071 | `NatalInterpretation.tsx` -> no monolithic owner -> architecture test plus line/import inventory. |
| RG-073 | Feature owner -> stays in `frontend/src/features/natal-chart/**` -> Vitest plus legacy wrapper scan. |
| RG-153 | Public `/natal` layers stay narrative/public-reading centered -> `NatalChartPage` Vitest plus build. |
| RG-154 | Public DOM -> no raw technical/evidence leak -> DOM Vitest plus targeted denylist scans. |
| RG-158 | CTA and accordion surface stay modern -> action tests, toggle scan, and no inline style scan. |
| RG-170 | Basic DOM -> sources and legal mentions stay deduplicated -> DOM/source guard plus build. |

- Needs-investigation: resolver returned broad frontend-adjacent guardrails; this story rejects those IDs because the brief names exact local guardrails.
- Non-applicable example: backend API guardrails from CS-432 remain out of scope for this frontend-only story.
- Non-applicable example: DB, migration, and provider guardrails remain out of scope.
- Registry gap: no new registry row is added in normal story generation.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Control scan before | `evidence/frontend-control-scan-before.txt` | Record current technical controls. |
| Control scan after | `evidence/frontend-control-scan-after.txt` | Prove removed controls stay absent. |
| Removal audit | `evidence/removal-audit.md` | Classify each removed frontend surface. |
| Vitest output | `evidence/vitest.txt` | Prove component and API-client behavior. |
| Lint output | `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/evidence/lint.txt` | Prove frontend lint status. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist is authorized for removed frontend technical controls.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - remove automatic technical generation state and wire product actions.
- `frontend/src/api/natal-chart/index.ts` - add product-action client and remove technical generation request fields.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - consume public slots and states without technical use case routing.
- `frontend/src/tests/natalInterpretation.test.tsx` - add non-regression coverage for actions, states, scans, and deduplication.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - cover request payloads, post-upgrade behavior, product actions, and slot states.

Files not expected to change:

- `backend/**` - out of scope; CS-432 owns backend product-action API behavior.
- `frontend/src/styles/**` - out of scope unless class support is required by a changed component structure.
- `frontend/e2e/**` - out of scope for this story's minimum proof.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend test -- natalInterpretation NatalChartPage`
- VC2: `pnpm --dir frontend lint`
- VC3 forbidden pattern: `shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh`
- VC3 allowed fixture pattern: `_condamad/stories/CS-433-frontend-product-actions-no-technical-generation-controls/**`
- VC3 roots: `frontend/src`
- VC3 expected false positives: none in application code after implementation.
- VC3 command: `rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src`
- VC4 forbidden pattern: `useCaseLevel|variantCode|forceRefresh|useCase|plan`
- VC4 allowed fixture pattern: astrology domain words such as `planet`, `planet_code`, and non-generation chart `planets`
- VC4 roots: `frontend/src/api frontend/src/features/natal-chart frontend/src/tests`
- VC4 expected false positives: public astrology words containing `plan` may be classified and justified in the removal audit.
- VC4 command: `rg -n "useCaseLevel|variantCode|forceRefresh|useCase|plan" frontend/src/api frontend/src/features/natal-chart frontend/src/tests`
- VC5 forbidden pattern: missing product-action command names
- VC5 allowed fixture pattern: none
- VC5 roots: `frontend/src`
- VC5 expected false positives: none
- VC5 command: `rg -n "action:\\s*['\"]generate_full|ThemeNatalReadingAction|theme-natal/readings" frontend/src`
- VC6 forbidden pattern: `style=`
- VC6 allowed fixture pattern: none
- VC6 roots: `frontend/src/features/natal-chart frontend/src/components/natal-interpretation`
- VC6 expected false positives: none for this story because no inline style is authorized.
- VC6 command: `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation`
- VC7 command: `pnpm --dir frontend build`
- VC7 reason: required by RG-153 and RG-170 to prove the public natal and Basic DOM surfaces still compile.
- VC8 command: `pnpm --dir frontend test -- natalInterpretation component-architecture NatalChartPage`
- VC8 reason: required by RG-071 and RG-073 to prove feature ownership and component decomposition.
- VC9 command: `rg -n "components/NatalInterpretation|NatalInterpretationLegacyBody" frontend/src`
- VC9 reason: required by RG-073 and RG-158 to reject legacy wrappers, aliases, and fallback bodies.

## Regression Risks

- Removing the old query state can hide an accepted reading if existing public slot rendering is not preserved.
- A residual React effect can reintroduce short-generation after Basic upgrade without explicit user action.
- Product-action command wiring can accidentally trigger `regenerate` instead of `generate_full`.
- The word `plan` has legitimate astrology uses, so scans must classify allowed astrology-domain hits precisely.
- Legal mentions can duplicate again if Basic public rendering is reworked without the existing deduplication helper.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all CSS in stylesheet files; no inline style is authorized.
- Preserve the frontend React/TypeScript stack and existing test style.
- Treat CS-432 as the backend product-action source, not as permission to edit backend code.

## References

- `_story_briefs/cs-433-frontend-remove-llm-technical-generation-controls.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
