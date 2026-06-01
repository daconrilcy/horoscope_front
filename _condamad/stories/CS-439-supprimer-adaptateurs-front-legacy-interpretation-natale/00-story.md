# Story CS-439 supprimer-adaptateurs-front-legacy-interpretation-natale: Supprimer Les Adaptateurs Front Legacy D'Interpretation Natale
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`.
- Operating mode: Repo-informed story.
- Fast Story Writer Mode: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` read first.
- Removal contract: `.agents/skills/condamad-story-writer/references/removal-story-contract.md` read because this story removes front adapters.
- Dependency: CS-438 owns backend historical route retirement; this story owns first-party frontend adapter retirement.
- Problem statement: the `/natal` frontend still accepts historical interpretation DTOs and old use-case heuristics for modern reading display.
- Source-alignment evidence: every source primitive maps to ACs, tasks, validation commands, non-goals, or blocker rules.

## Objective

Remove the first-party frontend adapters that translate historical natal interpretation payloads into modern public reading UI.
The `/natal` reading flow must consume explicit `theme_natal` public payloads and product states without old use-case heuristics.

## Target State

- `frontend/src/api/natal-chart/index.ts` exposes a public `ThemeNatalReadingPublicPayload` flow as the modern reading target.
- `mapProductActionDataToInterpretation` no longer returns `NatalInterpretationResult` or silently accepts the old envelope.
- `NatalInterpretationContent` renders public `theme_natal` schemas directly and does not branch on an old `use_case`.
- `NatalInterpretation.tsx` does not select public readings from `natal_long_free` or `natal_interpretation_short`.
- Public reading selection does not use old `level` heuristics, legacy route actions, or historical refresh controls.
- Public generation requests contain only `chart_id`, `action`, `persona_profile_id`, `locale`, and `client_request_id`.
- `variant_code` remains allowed only for entitlement display or gate state outside public LLM command construction.
- Front tests no longer contain positive fixtures built from `natal_long_free` or `natal_interpretation_short`.
- DOM guard tests reject public reading exposure of old technical symbols.
- No inline style is introduced by this change.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-439`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-153`, `RG-154`, `RG-155`, `RG-158`, `RG-170`, and `RG-173` read.
- Evidence 4: `resolve_guardrails.py` - resolver run with frontend natal, `/natal`, public reading, DOM guard, and product-action scope.
- Evidence 5: `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live-test report confirms old use-case collisions.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang report defines `theme_natal`.
- Evidence 7: `frontend/src/api/natal-chart/index.ts` contains `NatalInterpretationResult` and `mapProductActionDataToInterpretation`.
- Evidence 8: `frontend/src/features/natal-chart/NatalInterpretation.tsx` still detects `natal_long_free`.
- Evidence 9: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` still resolves display from `data.use_case` or `meta.use_case`.
- Evidence 10: `frontend/src/tests/natalInterpretation.test.tsx` and `frontend/src/tests/natalPublicDomGuard.test.tsx` contain positive old-use-case fixtures.
- Repository structure alert: expected frontend roots exist in this workspace; no root creation is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `mapProductActionDataToInterpretation` | in scope | AC1, Task 1, Reintroduction Guard |
| `ThemeNatalReadingPublicPayload` | in scope | AC1, AC3, Task 1, Task 3 |
| `NatalInterpretationResult` modern target | in scope | AC1, AC9, Task 2 |
| `item.use_case === "natal_long_free"` | in scope | AC2, AC7, Task 4 |
| `useCase === "natal_long_free"` | in scope | AC3, AC7, Task 3 |
| `use_case === "natal_interpretation_short"` | in scope | AC2, AC7, Task 4 |
| `level` reading heuristic | in scope | AC3, AC9, Task 3 |
| `variant_code` entitlement display | in scope | AC5, Task 5 |
| historical route buttons/actions | in scope | AC11, Task 10 |
| public generation body fields | in scope | AC4, Task 6 |
| `NatalInterpretationContent` public rendering | in scope | AC3, AC6, Task 3 |
| DOM guard denylist | in scope | AC6, Task 7 |
| inline style guard | in scope | AC8, Task 8 |
| backend contracts | out of scope | Explicit non-goals |
| entitlement billing/admin/global model | out of scope | Explicit non-goals |
| visual redesign of `/natal` | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: frontend-natal-reading
- In scope:
  - Frontend API client typing and hooks under `frontend/src/api/natal-chart/index.ts`.
  - Public `/natal` interpretation rendering under `NatalInterpretation.tsx` and `NatalInterpretationContent.tsx`.
  - Public DOM guard, API tests, and component tests proving old technical symbols are not user-facing.
  - Static scans over bounded frontend natal files for old use cases, generation controls, and inline styles.
- Out of scope:
  - Backend API contracts, database schema, auth, i18n copy rewrites, style redesign, build tooling, migrations, and billing/admin entitlement removal.
- Explicit non-goals:
  - No backend endpoint change.
  - No visual redesign of `/natal`.
  - No removal of `variant_code` from billing, admin, daily horoscope, or entitlement display surfaces.
  - No compatibility adapter, alias, shim, wrapper, fallback branch, or hidden remapping for old interpretation envelopes.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes historical frontend DTO adapters, heuristic branches, and positive fixtures from the public natal reading flow.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only first-party frontend handling of old natal interpretation envelopes in the public reading flow.
  - Preserve modern product-action command behavior already covered by CS-432 and CS-438.
  - Keep entitlement display state readable without using `variant_code` to construct an LLM command.
  - The only allowed surface delta is frontend consumption of `theme_natal` public payloads without old-use-case remapping.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: a first-party public UI path must still render stored historical rows after CS-438.
- Additional validation rules:
  - Use `pnpm` tests for frontend API body shape, component rendering, and DOM guard behavior.
  - Use bounded `rg` scans for old use cases, old generation controls, `variant_code`, and inline style syntax.
  - Use TypeScript lint through `pnpm --dir frontend lint` for orphaned type or hook references.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pnpm` component/API tests prove browser-facing behavior and command body shape. |
| Baseline Snapshot | yes | Before/after scan artifacts prove the only allowed frontend surface delta. |
| Ownership Routing | yes | Public reading payload ownership must stay in `frontend/src/api/natal-chart/index.ts` and UI readers. |
| Allowlist Exception | no | No allowlist handling is authorized for old frontend adapters or positive old-use-case fixtures. |
| Contract Shape | yes | The frontend command body and public reading payload shape are exact. |
| Batch Migration | no | No data migration or multi-batch repository conversion is in scope. |
| Reintroduction Guard | yes | Old use cases, controls, and DTO adapter symbols must stay absent from public reading code. |
| Persistent Evidence | yes | Removal audit, scans, test output, validation output, and review artifacts must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The modern API hook returns public reading payloads. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalChartApi.test.tsx`. |
| AC2 | `NatalInterpretation.tsx` stops selecting old use cases. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans bounded feature files. |
| AC3 | Content ignores old `use_case`. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalInterpretation.test.tsx`. |
| AC4 | Generation command bodies use only authorized fields. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- natalChartApi.test.tsx`. |
| AC5 | `variant_code` stays entitlement-only in `/natal`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans bounded front files. |
| AC6 | Public DOM rejects old technical symbols. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalPublicDomGuard.test.tsx`. |
| AC7 | Positive old-use-case fixtures are gone. | Evidence profile: repo_wide_negative_scan; `rg` scans bounded frontend tests. |
| AC8 | Inline styles are not introduced. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `style=\\{\\{` in bounded TSX files. |
| AC9 | Removed adapter symbols cannot reappear. | Evidence profile: reintroduction_guard; `rg` scans old DTO, mapper, control, and use-case symbols. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks `evidence/validation.txt`. |
| AC11 | Historical route actions are absent or modernized. | Runtime evidence: `pnpm --dir frontend test -- frontend/src/tests/NatalChartPage.test.tsx`. |

## Implementation Tasks

- [ ] Task 1: Replace `mapProductActionDataToInterpretation` with a public `theme_natal` payload mapping. (AC: AC1, AC4)
- [ ] Task 2: Stop using `NatalInterpretationResult` as the primary target for modern public readings. (AC: AC1, AC9)
- [ ] Task 3: Refactor `NatalInterpretationContent` to render public schemas without old `use_case` branching. (AC: AC3, AC6)
- [ ] Task 4: Remove old-use-case selection branches from `NatalInterpretation.tsx`. (AC: AC2, AC7)
- [ ] Task 5: Constrain `variant_code` usage to entitlement display or gate state in `NatalChartPage.tsx`. (AC: AC5)
- [ ] Task 6: Prove generated command bodies contain only the authorized product-action fields. (AC: AC4)
- [ ] Task 7: Strengthen DOM guard coverage for public reading symbols and remove positive old-use-case fixtures. (AC: AC6, AC7)
- [ ] Task 8: Run the inline-style scan over bounded TSX surfaces and move any required styling to CSS. (AC: AC8)
- [ ] Task 9: Persist removal audit, scan outputs, test output, lint output, and validation output. (AC: AC9, AC10)
- [ ] Task 10: Remove historical route buttons/actions or bind them to modern product-action endpoints after CS-438 status is checked. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md` - source brief.
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live-test failure source.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target architecture source.
- `_condamad/stories/regression-guardrails.md` - targeted frontend natal guardrail IDs.
- `frontend/src/api/natal-chart/index.ts` - canonical front API client and reading payload owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - public reading selection owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - public reading render owner.
- `frontend/src/pages/NatalChartPage.tsx` - `/natal` entitlement and page orchestration owner.
- `frontend/src/tests/natalChartApi.test.tsx` - API body and hook contract tests.
- `frontend/src/tests/natalInterpretation.test.tsx` - public reading component tests.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM denylist guard.

## Removal Classification Rules

- `canonical-active`: public `theme_natal` payloads, product-action command fields, and entitlement display state that remain first-party active.
- `external-active`: a frontend surface documented outside this repo as requiring old interpretation DTOs; delete is blocked until user decision.
- `historical-facade`: adapter symbols, old-use-case branches, and positive fixtures that only preserve old frontend envelopes.
- `dead`: old DTO or fixture symbols with zero first-party production, test, doc, generated contract, and known external consumers.
- `needs-user-decision`: a first-party public UI path still requires old stored rows after required scans and CS-438 route status are reviewed.

## Removal Audit Format

The implementation must write `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/frontend-removal-audit.md`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `mapProductActionDataToInterpretation` | symbol | historical-facade | `useNatalInterpretation` | `ThemeNatalReadingPublicPayload` | delete | `rg` output | Old DTO remap returns |
| `NatalInterpretationResult` modern target | type | historical-facade | public reading hook | public theme natal type | replace-consumer | `rg` output | Old envelope remains |
| `natal_long_free` branch | symbol | historical-facade | public UI and tests | explicit public state | delete | `rg` output | Free reading remap returns |
| `natal_interpretation_short` fixture | symbol | historical-facade | tests | public payload fixture | delete | `rg` output | Positive legacy fixture remains |
| `variant_code` entitlement display | field | canonical-active | `NatalChartPage.tsx` | entitlement gate state | keep | `rg` output | None |
| `variant_code` command use | field | historical-facade | command body construction | product `action` field | delete | `rg` output | Product command drift |
| unknown external old DTO consumer | symbol | needs-user-decision | external docs | public theme natal type | needs-user-decision | audit source | Public breakage |

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public natal reading payload type | `frontend/src/api/natal-chart/index.ts` | `NatalInterpretationResult` adapter target |
| Public reading rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | old `use_case` display branch |
| Reading selection in `/natal` | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | `natal_long_free` and `natal_interpretation_short` heuristics |
| Entitlement display state | `frontend/src/pages/NatalChartPage.tsx` | command body `variant_code` construction |
| Public DOM guard | `frontend/src/tests/natalPublicDomGuard.test.tsx` | positive old-use-case UI fixtures |

## Delete-Only Rule

- Items classified as `historical-facade` or `dead` must be deleted from public frontend paths.
- Removable items must be deleted, not repointed.
- Do not repoint old DTO adapters to the modern payload.
- Do not preserve wrapper functions that accept the old envelope.
- Do not add a compatibility alias for old use cases.
- Do not keep a fallback branch keyed by old `use_case`, `level`, or `variant_code`.
- Do not preserve the old path through re-export.
- Do not replace deletion with a soft-disabled hidden path.

## External Usage Blocker

- External usage blocker: active.
- Required action: scan first-party frontend, tests, reports, and known generated/public contracts before deleting each item.
- Any item classified as `external-active` must not be deleted.
- Blocker rule: any `external-active` item must be recorded in the removal audit with consumer, deletion risk, and user-decision text.
- The story requires an explicit user decision before deleting any `external-active` item.
- Allowed closure: no public frontend old adapter may stay nominally active without a `needs-user-decision` audit row.

## Generated Contract Check

- Generated contract check: active
- Required proof:
  - `pnpm --dir frontend lint` proves TypeScript references do not retain orphaned public adapter symbols.
  - `rg` scans prove old DTO and command-control symbols are absent from bounded frontend public reading surfaces.
- Reason: the frontend API module is the local public TypeScript contract consumed by the UI.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard` over frontend public imports and symbols.
  - `pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx`.
- Secondary evidence:
  - Targeted `rg` scans for old use cases, old generation controls, `variant_code` command use, and inline style syntax.
- Static scans alone are not sufficient for this story because:
  - Hook output shape, command body shape, component rendering, and DOM output must be proven through frontend tests.

## Contract Shape

- Contract type:
  - Frontend public reading payload, command body, and rendered DOM contract.
- Fields:
  - `chart_id`: required command chart identifier.
  - `action`: required product action.
  - `persona_profile_id`: optional persona profile for authorized full reading actions.
  - `locale`: optional locale value passed through the modern product-action command.
  - `client_request_id`: optional idempotency or request tracking value.
  - `state`: explicit product state from the modern reading command response.
  - `data`: accepted public `theme_natal` reading payload.
- Required fields:
  - `chart_id` and `action`.
- Optional fields:
  - `persona_profile_id`, `locale`, and `client_request_id`.
- Status codes:
  - HTTP route status behavior belongs to CS-438; this story validates frontend command and render contracts.
- Serialization names:
  - Command body keys are emitted as `chart_id`, `action`, `persona_profile_id`, `locale`, and `client_request_id`.
- Frontend type impact:
  - `UseNatalInterpretationResult` must expose modern public payload data instead of `NatalInterpretationResult`.
- Generated contract impact:
  - The local TypeScript API contract must not expose old envelopes as the primary modern reading target.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/frontend-legacy-before.txt`
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/variant-code-before.txt`
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/inline-style-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/frontend-legacy-after.txt`
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/variant-code-after.txt`
  - `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/inline-style-after.txt`
- Expected invariant:
  - The only intended frontend surface delta is removal of historical natal interpretation adapters and fixtures.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public reading payload mapping | `frontend/src/api/natal-chart/index.ts` | old `NatalInterpretationResult` adapter branch |
| Public reading render decision | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | old `use_case` or `level` heuristic |
| Reading selection | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | `natal_long_free` or `natal_interpretation_short` branch |
| Entitlement display | `frontend/src/pages/NatalChartPage.tsx` | LLM command body construction |
| DOM anti-return guard | `frontend/src/tests/natalPublicDomGuard.test.tsx` | production component code |

## Mandatory Reuse / DRY Constraints

- Reuse the existing centralized frontend API client instead of creating a second natal API client.
- Reuse existing public reading components and helpers before adding new helpers.
- Keep one canonical public payload type for modern `theme_natal` reading data.
- Do not duplicate product-action body construction across components.
- Keep CSS in existing stylesheet ownership; no inline style implementation is allowed.

## No Legacy / Forbidden Paths

- No legacy DTO adapter may remain in the public modern reading flow.
- No compatibility branch may accept `NatalInterpretationResult` as a modern public reading payload.
- No fallback branch may select rendering from old `use_case`, `level`, or `variant_code`.
- Forbidden symbols in public reading production paths: `natal_long_free`, `natal_interpretation_short`, `use_case_level`, `forceRefresh`, `force_refresh`.
- Forbidden historical controls: route action buttons or handlers that call retired CS-438 endpoints instead of modern product-action flow.
- Forbidden command-control use in public reading production paths: `variant_code` or `variantCode` outside entitlement display or gate state.
- Forbidden positive test fixtures: `natal_long_free` and `natal_interpretation_short`.
- Forbidden style syntax in touched public reading TSX paths: `style={{`.

## Reintroduction Guard

- Guard target: public frontend natal reading production paths and bounded tests.
- The implementation must add or update an architecture guard that fails when removed frontend adapter symbols return.
- The architecture guard must fail when removed frontend adapter symbols are reintroduced.
- Deterministic source: forbidden symbols in bounded frontend files.
- Guard command 1:
  - `rg -n "natal_long_free|natal_interpretation_short|use_case_level|forceRefresh|force_refresh|shouldRefreshShortAfterBasicUpgrade" frontend/src`
- Guard command 2:
  - Run:
    ```powershell
    rg -n "variant_code|variantCode" `
      frontend/src/features/natal-chart `
      frontend/src/components/natal-interpretation `
      frontend/src/api/natal-chart `
      frontend/src/pages/NatalChartPage.tsx
    ```
- Guard command 3:
  - Run:
    ```powershell
    rg -n "NatalInterpretationResult|mapProductActionDataToInterpretation|isNatalInterpretationResult" `
      frontend/src/api/natal-chart `
      frontend/src/features/natal-chart `
      frontend/src/components/natal-interpretation
    ```
- Guard command 4:
  - `rg -n "style=\\{\\{" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages/NatalChartPage.tsx`
- Expected result:
  - Guard command 1 allows denylist declarations only in `natalPublicDomGuard.test.tsx`; positive fixtures are forbidden.
  - Guard command 2 allows entitlement display or gate-state reads in `NatalChartPage.tsx`; command body construction is forbidden.
  - Guard command 3 must have zero hits in modern public reading production flow after replacement.
  - Guard command 4 must have zero hits in touched TSX paths.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-153 `/natal` composition | public `/natal` -> narrative public reading stays active -> `pnpm` `natalInterpretation.test.tsx`. |
| RG-154 DOM denylist | public reading DOM -> old technical symbols stay hidden -> `pnpm` `natalPublicDomGuard.test.tsx`. |
| RG-155 semantic integrity | public rendering -> no frontend padding or empty-source fallback -> component and DOM guard tests. |
| RG-158 modern accordions | public reading UI -> modern accordion rendering remains -> `pnpm` `natalInterpretation.test.tsx`. |
| RG-170 Basic sources/legal | Basic public DOM -> sources and legal notices stay deduplicated -> DOM guard or component `pnpm` test. |
| RG-173 raw old use case | public generation -> old use cases do not drive commands -> `rg` guard plus `pnpm` API test. |
| RG-047 inline styles | touched TSX -> no inline style syntax added -> bounded `rg` guard. |

- Applicability note: backend rejection evidence for `RG-155` stays owned outside this frontend story; this story must not add frontend padding or empty-source fallback.
- Non-applicable examples: DB schema, auth, backend migrations.
- Registry gap: no dedicated guardrail currently names removal of `NatalInterpretationResult` as a frontend modern payload target.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/frontend-removal-audit.md` | Classify removed symbols and blockers. |
| Before scan | `evidence/frontend-legacy-before.txt` | Capture old frontend symbols before work. |
| After scan | `evidence/frontend-legacy-after.txt` | Prove old frontend symbols after work. |
| Variant scan | `evidence/variant-code-after.txt` | Prove entitlement-only usage classification. |
| Inline style scan | `evidence/inline-style-after.txt` | Prove no inline style syntax in touched paths. |
| Validation output | `evidence/validation.txt` | Keep lint, tests, and scans for review. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for old frontend adapters, DTO target use, or positive old-use-case fixtures.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/api/natal-chart/index.ts` - replace old adapter target and public payload hook shape.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - remove old-use-case selection branches.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - render public schemas without old-use-case branching.
- `frontend/src/pages/NatalChartPage.tsx` - keep `variant_code` entitlement-only.
- `frontend/src/tests/natalChartApi.test.tsx` - prove command body shape and modern payload hook behavior.
- `frontend/src/tests/natalInterpretation.test.tsx` - replace old positive fixtures with public payload fixtures.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - strengthen denylist without positive old-use-case fixture payloads.
- `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/evidence/*.txt` - persist implementation evidence.

Likely tests:

- `frontend/src/tests/natalChartApi.test.tsx` - command body and API mapping contract.
- `frontend/src/tests/natalInterpretation.test.tsx` - UI rendering and selection behavior.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - public DOM anti-return guard.
- `frontend/src/tests/NatalChartPage.test.tsx` - page entitlement and header action behavior.

Files not expected to change:

- `backend/**` - out of scope; CS-438 owns backend route and contract removal.
- `frontend/src/styles/**` - unchanged unless touched TSX currently requires moving an inline style to existing CSS ownership.
- `frontend/src/api/billing/**` - out of scope; entitlement model remains available.
- `frontend/src/admin/**` - out of scope; admin display is not changed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx`
- VC2: `pnpm --dir frontend lint`
- VC3 forbidden pattern: `natal_long_free|natal_interpretation_short|use_case_level|forceRefresh|force_refresh|shouldRefreshShortAfterBasicUpgrade`.
- VC3 allowed fixture pattern: denylist declaration in `frontend/src/tests/natalPublicDomGuard.test.tsx`; positive old-use-case fixtures are forbidden.
- VC3 roots: `frontend/src`.
- VC3 expected false positives: denylist regex declaration only.
- VC3 command: `rg -n "natal_long_free|natal_interpretation_short|use_case_level|forceRefresh|force_refresh|shouldRefreshShortAfterBasicUpgrade" frontend/src`
- VC4 forbidden pattern: `variant_code|variantCode`.
- VC4 allowed fixture pattern: entitlement display or gate-state assertions, never product-action command body construction.
- VC4 roots: `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`, `frontend/src/api/natal-chart`, `frontend/src/pages/NatalChartPage.tsx`.
- VC4 expected false positives: entitlement display or quota gate reads in `NatalChartPage.tsx` and tests proving the field is not sent.
- VC4 command:
  ```powershell
  rg -n "variant_code|variantCode" `
    frontend/src/features/natal-chart `
    frontend/src/components/natal-interpretation `
    frontend/src/api/natal-chart `
    frontend/src/pages/NatalChartPage.tsx
  ```
- VC5 forbidden pattern: `style=\\{\\{`.
- VC5 allowed fixture pattern: none.
- VC5 roots: `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`, `frontend/src/pages/NatalChartPage.tsx`.
- VC5 expected false positives: none.
- VC5 command: `rg -n "style=\\{\\{" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages/NatalChartPage.tsx`
- VC6 forbidden pattern: `NatalInterpretationResult|mapProductActionDataToInterpretation|isNatalInterpretationResult`.
- VC6 allowed fixture pattern: removal audit or generated story evidence only, outside `frontend/src`.
- VC6 roots: `frontend/src/api/natal-chart`, `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`.
- VC6 expected false positives: none in bounded production frontend roots.
- VC6 command:
  ```powershell
  rg -n "NatalInterpretationResult|mapProductActionDataToInterpretation|isNatalInterpretationResult" `
    frontend/src/api/natal-chart `
    frontend/src/features/natal-chart `
    frontend/src/components/natal-interpretation
  ```

## Regression Risks

- Public reading may stop displaying old dev rows; that is an allowed delta unless a user-decision blocker is recorded.
- Removing old adapter types can reveal orphaned TypeScript imports; `pnpm --dir frontend lint` is required.
- `variant_code` may still appear in entitlement display code; the removal audit must classify each remaining hit.
- DOM guard denylist may intentionally contain forbidden strings; positive old-use-case fixture payloads must still be removed.
- CS-438 route retirement may require deleting public buttons instead of rebinding them; the implementation must record the chosen action.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all CSS changes in existing CSS ownership; no inline style is authorized.
- Do not modify backend routes, schemas, migrations, or database code for this story.

## References

- `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-story-writer/references/removal-story-contract.md`
