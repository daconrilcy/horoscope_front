# Story CS-380 durcir-natal-expert-panel-contre-payloads-partiels: Harden Natal Expert Panel Against Partial Payloads
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`.
- Selected mode: Repo-informed story.
- Problem statement: `NatalExpertPanel` reads `traditional_conditions.{planet}.hayz.is_hayz` directly and can crash when a
  temporary partial expert payload reaches the frontend after natal chart generation.
- Source-alignment evidence: this story keeps the frontend as an API fact consumer, protects page rendering locally, and
  preserves CS-379 as the backend public-contract fix.

## Objective

Make the natal expert panel tolerate partial expert sub-blocks without synthesizing astrology facts or normalizing the
partial payload as the nominal frontend API contract.

## Target State

- Complete expert payloads keep rendering the existing `hayz` and `rejoicing` facts.
- A partial `traditional_conditions` planet entry renders a localized degraded state for that entry.
- Other valid planet entries remain visible when one traditional entry is partial.
- The nominal TypeScript API types still require complete `hayz` and `rejoicing` blocks.
- Frontend code does not compute, score, infer, or invent traditional astrology facts.
- Existing non-sensitive frontend trace conventions are reused only if applicable to this natal expert drift.
- Generation navigation remains usable after a temporary partial payload reaches the natal page.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md` -
  source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign story number `CS-380`.
- Evidence 3: targeted reads confirmed `frontend/src/features/natal-chart/NatalExpertPanel.tsx` directly reads
  `condition.hayz.is_hayz` and `condition.rejoicing.rejoicing_house`.
- Evidence 4: targeted reads confirmed `frontend/src/api/natal-chart/index.ts` models `TraditionalPlanetCondition` with
  required `hayz` and `rejoicing`.
- Evidence 5: targeted reads confirmed `frontend/src/tests/NatalExpertPanel.test.tsx` already proves full expert rendering.
- Evidence 6: `resolve_guardrails.py` selected frontend local validation guardrails for this scope.
- Source stakes retained: no page-wide crash, visible contract drift, no React-side astrology derivation, strict nominal
  public type contract, and no new frontend dependency.

## Domain Boundary

- Domain: frontend-natal-expert-panel
- In scope:
  - `NatalExpertPanel` rendering of partial `traditional_conditions` entries.
  - Local read guards for `condition.hayz`, `condition.rejoicing`, and expert sub-blocks consumed by this panel.
  - CSS class reuse or extension for the localized degraded state.
  - Vitest coverage for a missing `hayz` block and for the complete expert payload.
- Out of scope:
  - Backend contract repair, API route changes, database schema, auth, i18n framework changes, build tooling, and migrations.
- Explicit non-goals:
  - No frontend recalculation of hayz, sect, rejoicing, dignities, scores, or doctrinal facts.
  - No conversion of partial traditional payloads into the nominal API type.
  - No redesign of the expert panel.
  - No public display of prompt, provider, or internal LLM payload details.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a localized frontend robustness contract for partial API data.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only frontend rendering and tests around `NatalExpertPanel` and its local style surface.
  - Keep complete payload rendering unchanged for the fields already asserted in tests.
  - Keep partial-payload tolerance local to the UI rendering boundary.
  - Surface contract drift visibly through localized degraded copy and test naming.
- Additional validation rules:
  - Vitest must render a chart with `traditional_conditions.alpha.hayz` missing.
  - Static scan must show no added astrology calculation, scoring, doctrinal fallback, or inline style in touched TSX.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product wants partial `traditional_conditions` to become a supported public contract.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest and Testing Library prove rendered behavior for complete and partial payloads. |
| Baseline Snapshot | yes | Before/after test evidence proves the page-level crash is converted to localized degraded output. |
| Ownership Routing | yes | Runtime tolerance must stay in the panel rendering boundary, not API nominal types. |
| Allowlist Exception | no | No broad allowlist handling is authorized for this localized rendering hardening. |
| Contract Shape | yes | Nominal API types stay strict while invalid runtime input is narrowed locally. |
| Batch Migration | no | No batch migration or multi-surface conversion is in scope. |
| Reintroduction Guard | yes | React must not add astrology derivation, hidden fallback facts, or inline style. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Missing `hayz` no longer crashes the panel. | Evidence profile: json_contract_shape; `pnpm test -- NatalExpertPanel`. |
| AC2 | A partial traditional entry shows localized degraded copy. | Evidence profile: json_contract_shape; `pnpm test -- NatalExpertPanel`. |
| AC3 | Valid neighboring traditional entries remain visible. | Evidence profile: json_contract_shape; `pnpm test -- NatalExpertPanel`. |
| AC4 | Complete expert rendering still proves hayz fields. | Evidence profile: json_contract_shape; `pnpm test -- NatalExpertPanel`. |
| AC5 | Nominal API types keep required traditional blocks. | Evidence profile: frontend_typecheck_no_orphan; `AST guard`; `pnpm build`. |
| AC6 | React adds no astrology derivation. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans touched TSX and tests. |
| AC7 | No inline style is introduced. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "style=" frontend/src/features/natal-chart`. |
| AC8 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC9 | Trace decision non-sensitive. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "trackEvent|console\\." frontend/src/features/natal-chart`. |

## Implementation Tasks

- [ ] Task 1: Capture the failing partial traditional payload fixture in `NatalExpertPanel.test.tsx`. (AC: AC1, AC8)
- [ ] Task 2: Add local narrowing helpers for traditional condition entries inside the panel module. (AC: AC1, AC5)
- [ ] Task 3: Render degraded copy for the partial planet entry without filling missing facts. (AC: AC2, AC6)
- [ ] Task 4: Preserve rendering for complete `hayz` and `rejoicing` facts. (AC: AC3, AC4)
- [ ] Task 5: Add or reuse CSS classes for the degraded state in `NatalExpertPanel.css`. (AC: AC2, AC7)
- [ ] Task 6: Keep `frontend/src/api/natal-chart/index.ts` nominal types strict. (AC: AC5)
- [ ] Task 7: Decide trace handling from existing frontend convention without exposing provider or prompt data. (AC: AC9)
- [ ] Task 8: Run targeted frontend validation and persist validation output. (AC: AC1, AC5, AC8)

## Files to Inspect First

- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - expert panel rendering and local read guards.
- `frontend/src/features/natal-chart/NatalExpertPanel.css` - CSS-only styling for degraded state.
- `frontend/src/api/natal-chart/index.ts` - nominal public API types that must stay strict.
- `frontend/src/tests/NatalExpertPanel.test.tsx` - focused Vitest coverage for complete and partial payloads.
- `frontend/src/pages/BirthProfilePage.tsx` - generation navigation witness after chart creation.
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx` - generation CTA witness.
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md` - backend contract context.

## Runtime Source of Truth

- Primary source of truth:
  - Vitest with Testing Library rendering `NatalExpertPanel` from real component code.
  - `AST guard` over `frontend/src/api/natal-chart/index.ts` for required `hayz` and `rejoicing` type fields.
- Secondary evidence:
  - Targeted `rg` scans over touched frontend files for forbidden derivation and inline style.
- Static scans alone are not sufficient for this story because:
  - The defect is a rendered React behavior triggered by partial runtime data.

## Contract Shape

- Contract type:
  - Frontend public API consumer contract and local runtime narrowing.
- Fields:
  - `traditional_conditions.{planet}.hayz`: required by nominal API type, but locally checked before reading.
  - `traditional_conditions.{planet}.rejoicing`: required by nominal API type, but locally checked before reading.
  - `hayz.is_hayz`: displayed only when supplied by the API payload.
  - `hayz.chart_sect`: displayed only when supplied by the API payload.
  - `rejoicing.rejoicing_house`: displayed only when supplied by the API payload.
- Required fields:
  - Nominal `TraditionalPlanetCondition.hayz` and `TraditionalPlanetCondition.rejoicing` remain required in API types.
- Optional fields:
  - Local runtime-narrowed values may be absent only inside the degraded rendering branch.
- Status codes:
  - none; no API route is changed.
- Serialization names:
  - Existing snake_case JSON field names stay unchanged.
- Frontend type impact:
  - Add a local invalid-runtime guard type only inside the component or test fixture boundary.
- Generated contract impact:
  - none; no generated client or OpenAPI artifact is changed.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/partial-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/partial-after.txt`
- Expected invariant:
  - The only intended UI surface delta is localized degraded rendering for partial expert entries.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Expert panel runtime narrowing | `frontend/src/features/natal-chart/NatalExpertPanel.tsx` | `frontend/src/api/natal-chart/index.ts` |
| Nominal natal API types | `frontend/src/api/natal-chart/index.ts` | Component-local partial contract promotion |
| Degraded expert styling | `frontend/src/features/natal-chart/NatalExpertPanel.css` | Inline TSX styles |
| Generation page navigation | `frontend/src/pages/BirthProfilePage.tsx` | Expert panel data guards |

## Mandatory Reuse / DRY Constraints

- Reuse existing `formatValue`, `SectionShell`, `FactRow`, and CSS token variables before adding new helpers.
- Keep new helpers small and local to the expert panel unless duplicate runtime narrowing appears in another component.
- Do not duplicate the expert payload fixture beyond the existing `buildExpertChart` test helper pattern.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy payload mapper may be added to normalize partial expert payloads.
- No compatibility type may replace the nominal `TraditionalPlanetCondition` API contract.
- No fallback astrology facts may be rendered for missing `hayz` or `rejoicing`.
- Forbidden frontend surfaces: generated API client replacement, global chart adapter, route-level error masking.

## Reintroduction Guard

- Keep astrology derivation out of `NatalExpertPanel.tsx`.
- Keep styles in `NatalExpertPanel.css`; no `style=` attribute may be added to touched TSX.
- Require deterministic guards:
  - `rg -n "calculate|score|infer|derive|doctrine|fallback" frontend/src/features/natal-chart/NatalExpertPanel.tsx frontend/src/tests/NatalExpertPanel.test.tsx`
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/tests`
  - `rg -n "trackEvent|console\\." frontend/src/features/natal-chart frontend/src/tests`
  - `pnpm test -- NatalExpertPanel`

## Regression Guardrails

| Guardrail | Applied invariant | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Expert degraded state must use CSS, not inline style. | `rg` style scan; `pnpm lint`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | New CSS must reuse canonical tokens and avoid stale aliases. | CSS review; `pnpm lint`. |
| Registry gap | No exact guardrail for partial natal `traditional_conditions` rendering was selected. | Local Vitest evidence only. |

Non-applicable examples:

- RG-007 is not selected because this story does not touch API routes or OpenAPI.
- RG-027 is not selected because prediction domain infra is outside scope.
- RG-041 is not selected because entitlement documentation is outside scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Partial payload baseline | `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/partial-before.txt` | Show the pre-fix render failure. |
| Partial payload final | `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/partial-after.txt` | Prove degraded render output. |
| Validation output | `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/validation.txt` | Keep command results. |
| Review output | `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for this localized frontend hardening.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - add local guards and degraded rendering.
- `frontend/src/features/natal-chart/NatalExpertPanel.css` - style the degraded state with existing variables.
- `frontend/src/tests/NatalExpertPanel.test.tsx` - add partial payload regression coverage.
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/**` - persist validation evidence.

Likely tests:

- `frontend/src/tests/NatalExpertPanel.test.tsx`

Files not expected to change:

- `backend/**` - out of scope; CS-379 owns backend public-contract repair.
- `frontend/src/api/natal-chart/index.ts` - inspect only; nominal API types stay strict.
- `frontend/src/pages/**` - out of scope unless a focused page-level test proves navigation usability.
- `frontend/src/styles/**` - out of scope; component CSS owns local styling.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend test -- NatalExpertPanel`
- VC2: `pnpm --dir frontend lint`
- VC3: `pnpm --dir frontend build`
- VC4: `pnpm --dir frontend test -- BirthProfilePage NatalChartPage natalInterpretation`
- VC5: `rg -n "style=" frontend/src/features/natal-chart frontend/src/tests`
- VC6: `rg -n "calculate|score|infer|derive|doctrine|fallback" frontend/src/features/natal-chart/NatalExpertPanel.tsx frontend/src/tests/NatalExpertPanel.test.tsx`
- VC7: `python -c "s=open('frontend/src/api/natal-chart/index.ts').read(); assert 'hayz:' in s and 'rejoicing:' in s"`
- VC8: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/validation.txt').exists()"`
- VC9: `rg -n "trackEvent|console\\." frontend/src/features/natal-chart frontend/src/tests`

## Regression Risks

- A permissive frontend type could hide backend contract drift and weaken CS-379.
- A rendered placeholder could be mistaken for a calculated astrology fact.
- A panel-level fix could leave neighboring valid planets hidden by a partial entry.
- A style change could introduce inline style or duplicate design tokens.
- A page-level error boundary could still trigger if another expert sub-block is read without narrowing.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep frontend nominal API types strict.
- Keep partial-payload tolerance local to `NatalExpertPanel` rendering.
- Do not compute astrology facts in React.
- Use CSS classes and existing variables for any new visual state.
- Run frontend validation from `frontend` and persist outputs under this story evidence directory.

## References

- `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-379-stabiliser-contrat-public-generation-theme-natal/00-story.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
