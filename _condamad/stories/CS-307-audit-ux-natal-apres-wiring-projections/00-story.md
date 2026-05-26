# Story CS-307 audit-ux-natal-apres-wiring-projections: Audit UX Natal After Projection Wiring
Status: done

## Trigger / Source

- Source type: audit brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md`.
- Selected mode: Audit-to-story with Fast Story Writer Mode.
- Problem statement: `/natal` has technical projection proof, but the B2C reading experience still needs a structured UX audit and scoped fixes.
- Source stakes: make projection content readable, preserve existing UI ownership, verify desktop and mobile, and document product decisions separately.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails keep the brief focused on `/natal` UX after CS-303 to CS-306.

## Objective

Audit the real `/natal` experience after B2C projection wiring, correct proven UI irritants inside the existing frontend scope, and persist a dated audit note.
The story must turn CS-303 and CS-306 technical proof into a product-level UX closure without redesigning `/natal`.

## Target State

- A dated UX audit note lists inspected issues for `/natal` as corrected, acceptable, or requiring product decision.
- `beginner_summary_v1` and `client_interpretation_projection_v1` remain readable inside the existing interpretation area.
- Loading, success, empty, error, entitlement, degraded, and disclaimer states remain visible and understandable.
- Desktop, tablet, and mobile checks prove critical text and controls do not overlap.
- Obvious UI defects are fixed in existing React owners and CSS files only.
- Targeted frontend tests cover corrected states, and the full frontend suite is run or its concrete limit is documented.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-307` after `CS-306`.
- Evidence 3: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - CS-303 wiring proof read.
- Evidence 4: `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md` - browser QA proof read.
- Evidence 5: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection state orchestration owner inspected.
- Evidence 6: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection display and disclaimer owner inspected.
- Evidence 7: `frontend/src/features/natal-chart/NatalInterpretation.css` - existing styling owner inspected.
- Evidence 8: `frontend/src/pages/NatalChartPage.tsx` - `/natal` page composition owner inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped resolver and targeted ID lookup consulted.
- Source-alignment evidence: PASS; the story preserves all source stakes and keeps backend projections, plans, and marketing surfaces out of scope.

## Domain Boundary

- Domain: frontend-ux
- In scope:
  - UX audit of `/natal` after CS-303 projection wiring and CS-306 browser proof.
  - Visual hierarchy, readability, card density, titles, copy labels, states, messages, and disclaimers in the existing `/natal` UI.
  - Desktop, tablet, and mobile browser checks with before and after evidence for corrected defects.
  - Minimal React and CSS changes inside existing `/natal` interpretation owners.
  - Targeted Vitest coverage for corrected UX states and architecture guard preservation.
- Out of scope:
  - Backend projection payloads, API contracts, DB schema, auth, i18n rewrites, build tooling, migrations, and plan policy changes.
  - Full `/natal` redesign, new marketing page, generated client, new UI dependency, and new styling system.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No backend route, serializer, projection builder, persistence, entitlement policy, prompt, provider, admin, replay, or audit runtime change.
  - No new page, new navigation model, plan redesign, or product positioning rewrite.
  - No inline style implementation.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a scoped frontend UX audit with targeted UI corrections.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Correct only proven `/natal` UX defects from the audit note.
  - Keep projection transport in `frontend/src/api/astrologyProjections.ts`.
  - Keep projection rendering in existing natal interpretation components.
  - Keep styles in existing CSS files and reuse available variables, tokens, spacing, color, and border patterns.
  - Keep loading, success, empty, error, entitlement, degraded, and disclaimer behavior visible.
  - Preserve backend projection payloads, entitlement plans, and public API contracts unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a UX issue needs product positioning, offer policy, or copy strategy beyond obvious UI correction.
- Additional validation rules:
  - Browser evidence must include date, route, viewport, inspected state, result, and screenshot path for visual corrections.
  - Audit note entries must use only `corrected`, `acceptable`, or `product-decision-required` decisions.
  - Static scans must prove no inline styles and no new projection API bypass in touched frontend files.
  - Corrected UI states must have targeted Vitest evidence or a bounded manual browser check.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Browser checks, Vitest, and `pnpm lint` prove the `/natal` UX result. |
| Baseline Snapshot | yes | Before and after audit artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | React owners, CSS owners, tests, and audit artifacts must stay in canonical paths. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for scoped UX fixes. |
| Contract Shape | yes | The UX audit note and QA ledger have exact required fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Inline styles, direct projection HTTP calls, and backend changes must stay absent. |
| Persistent Evidence | yes | Audit note, screenshots, validation output, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | A dated UX audit note classifies inspected issues. | Evidence profile: baseline_before_after_diff; `python` checks audit note decisions. |
| AC2 | Projection hierarchy is readable on `/natal`. | Evidence profile: json_contract_shape; `vitest` or Manual check: browser screenshots cover the two projection blocks. |
| AC3 | Critical text never overlaps controls. | Evidence profile: baseline_before_after_diff; Manual check: desktop, tablet, and mobile screenshots verify no overlap. |
| AC4 | Projection state messages remain understandable. | Evidence profile: json_contract_shape; `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`. |
| AC5 | Disclaimers remain app-owned. | Evidence profile: targeted_forbidden_symbol_scan; `vitest` and `rg` verify disclaimer ownership. |
| AC6 | UI corrections stay in existing owners. | Evidence profile: ast_architecture_guard; `AST guard`, `rg`, and `component-architecture-guards`. |
| AC7 | Frontend validation commands pass or document a limit. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and full `vitest` command output. |
| AC8 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-307 evidence paths. |
| AC9 | Disclaimers remain visible. | Evidence profile: json_contract_shape; `vitest` or Manual check: browser screenshots cover disclaimer placement. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-303 proof, CS-306 proof, `/natal` owners, existing tests, and scoped guardrails. (AC: AC1, AC6)
- [ ] Task 2: Create the dated UX audit note with inspected issues and exact decisions. (AC: AC1)
- [ ] Task 3: Review `/natal` visual hierarchy for both B2C projection blocks. (AC: AC2)
- [ ] Task 4: Capture desktop, tablet, and mobile evidence for projection readability and critical controls. (AC: AC2, AC3)
- [ ] Task 5: Correct proven UI defects in existing React components and CSS owners only. (AC: AC2, AC3, AC6)
- [ ] Task 6: Verify loading, success, empty, error, entitlement, degraded, and disclaimer states. (AC: AC4, AC5, AC9)
- [ ] Task 7: Add or adjust targeted Vitest coverage for corrected UX states. (AC: AC4, AC5, AC7, AC9)
- [ ] Task 8: Run architecture, inline-style, and projection ownership scans. (AC: AC6)
- [ ] Task 9: Run targeted frontend validation and full frontend suite. (AC: AC7)
- [ ] Task 10: Persist screenshots, QA ledger, validation output, and final notes under the CS-307 capsule. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md` - source brief.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - projection wiring evidence.
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md` - browser QA closure evidence.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection state orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering and disclaimer owner.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - existing style owner.
- `frontend/src/pages/NatalChartPage.tsx` - `/natal` page composition owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - projection state tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - page integration tests.
- `frontend/src/tests/component-architecture-guards.test.ts` - architecture guard tests.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Real browser checks for `/natal` on desktop, tablet, and mobile viewports.
  - `AST guard` coverage through the existing component architecture guard tests.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation` from `frontend`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - `pnpm lint` from `frontend`.
- Secondary evidence:
  - Dated UX audit note and QA ledger under `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/`.
  - Targeted `rg` scans for inline styles, projection API bypass, backend drift, and app-owned disclaimer ownership.
- Static scans alone are not sufficient because:
  - This story validates actual reading hierarchy and responsive layout, which require browser evidence.

## Contract Shape

- Contract type:
  - Frontend UX audit note and browser QA evidence contract.
- Fields:
  - `audit_date`: ISO date of the UX audit.
  - `route`: `/natal`.
  - `viewport`: desktop, tablet, mobile, or not-browser.
  - `state`: loading, success, empty, error, entitlement, degraded, disclaimer, or visual-hierarchy.
  - `finding`: concise inspected UX issue or accepted state.
  - `decision`: corrected, acceptable, or product-decision-required.
  - `evidence_path`: persisted artifact path.
  - `result`: pass, corrected, blocked-product-decision, or documented-limit.
- Required fields:
  - `audit_date`
  - `route`
  - `state`
  - `finding`
  - `decision`
  - `evidence_path`
  - `result`
- Optional fields:
  - `screenshot_path`
  - `product_decision_owner`
  - `validation_command`
- Status codes:
  - none; this story does not change HTTP response codes.
- Serialization names:
  - Ledger keys are written exactly as `audit_date`, `route`, `viewport`, `state`, `finding`, `decision`, `evidence_path`, and `result`.
- Frontend type impact:
  - only targeted type changes required by proven UI-state tests are authorized.
- Backend type impact:
  - none; backend projection payloads and API contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, or generated manifest change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-before.md`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-after.md`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-after.md`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/validation.txt`
- Expected invariant:
  - The only intended application delta is correcting proven `/natal` UX defects inside existing frontend owners.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `/natal` page composition | `frontend/src/pages/NatalChartPage.tsx` | New page or marketing route |
| Projection state orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | API module or unrelated page |
| Projection rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Backend or admin component |
| Natal interpretation styling | `frontend/src/features/natal-chart/NatalInterpretation.css` | Inline TSX `style` attributes |
| Targeted tests | `frontend/src/tests/natalInterpretation.test.tsx` and `frontend/src/tests/NatalChartPage.test.tsx` | New duplicate test harness |
| UX evidence | CS-307 `evidence/` directory | Application source comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing `/natal` components, projection state mapping, and CSS classes.
- Reuse existing design variables, color tokens, spacing tokens, borders, and responsive patterns.
- Reuse existing Vitest and logged Vite runner commands.
- Reuse CS-303 and CS-306 evidence as context only; do not duplicate their capsule content.
- Do not add external packages, generated clients, new API clients, new UI framework components, or duplicate projection parsing logic.
- Do not move business logic into UI components while fixing visual defects.

## No Legacy / Forbidden Paths

- No legacy `/natal` UI path may be added for projection display.
- No compatibility projection renderer may be added beside the canonical components.
- No fallback API transport may be added in the page or interpretation components.
- Do not create aliases, shims, wrappers, or duplicated state machines for projection rendering.
- Do not add inline `style` attributes in TSX files.
- Do not change backend projection code, payload builders, DB schema, migrations, entitlement plans, or public API schemas.
- Do not hide loading, empty, error, entitlement, degraded, or disclaimer states to simplify layout.

## Reintroduction Guard

- Guard path 1: touched TSX files must not gain inline `style` attributes.
- Guard path 2: `/v1/astrology/projections` calls must remain owned by the central API client.
- Guard path 3: backend files must remain unchanged for this frontend UX story.
- Guard path 4: legal disclaimer copy must remain app-owned and visible inside the interpretation content.
- Required deterministic guards:
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages -g "*.tsx"`.
  - `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
  - `rg -n "legalNoticeLines|disclaimerTitle" frontend/src/components/natal-interpretation frontend/src/i18n frontend/src/tests`.
  - `git diff --name-only -- backend frontend _condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | CSS fixes keep canonical frontend style owners. | `rg` token scan; targeted Vitest. |
| Story-local `/natal` UX guard | Projection and disclaimer states stay readable across viewports. | Browser ledger; screenshots; Vitest. |
| Needs-investigation | Resolver returned backend/docs guardrails for frontend UX scope; they are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-027 is not selected because pure backend prediction infra is out of scope.
- RG-041 is not selected because entitlement documentation is not edited.
- RG-042 is not selected because backend LLM documentation is not edited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| UX audit before | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-before.md` | Record initial audit findings. |
| UX audit after | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-after.md` | Record decisions after fixes. |
| Browser QA ledger | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa.md` | Track route, viewport, state, result. |
| Browser screenshots | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-screenshots/` | Store responsive visual proof. |
| Validation log | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/validation.txt` | Keep final validation commands. |
| Product decisions | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/product-decisions.md` | List decisions left to product. |
| Review output | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - change only for proven state hierarchy or label issues.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - change only for proven projection display issues.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - correct layout, spacing, responsive, and readability defects.
- `frontend/src/pages/NatalChartPage.tsx` - change only for proven page-level `/natal` hierarchy issues.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover corrected projection and disclaimer states.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover corrected page-level UX states.
- `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/**` - persist audit, screenshots, and validation logs.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - projection rendering, state, disclaimer, and corrected UI behavior.
- `frontend/src/tests/NatalChartPage.test.tsx` - `/natal` page-level integration states.
- `frontend/src/tests/component-architecture-guards.test.ts` - ownership and architecture guards.

Files not expected to change:

- `backend/app/**` - out of scope; projection runtime remains unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create dated UX audit artifacts under the CS-307 evidence directory.
- VC2: open `/natal` in a real browser on desktop, tablet, and mobile viewports; persist screenshots and a QA ledger.
- VC3: from `frontend`, run `pnpm lint`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage`.
- VC5: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
- VC6: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC7: from repo root, run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages -g "*.tsx"`.
- VC8: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC9: from repo root, run `rg -n "legalNoticeLines|disclaimerTitle" frontend/src/components/natal-interpretation frontend/src/i18n frontend/src/tests`.
- VC10: from repo root with venv active, run `python -B` to assert CS-307 evidence paths and audit decisions exist.

## Regression Risks

- A UX audit could expand into a broad redesign instead of correcting only proven defects.
- Visual fixes could introduce inline styles or bypass existing CSS token ownership.
- A state could become less visible while improving the success-state layout.
- Product decisions could be silently embedded in copy or plan logic without an explicit decision record.
- Browser screenshots could miss tablet width, leaving a responsive gap between desktop and mobile.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start from the UX audit note before changing UI code.
- Correct only defects that can be evidenced from `/natal` screenshots or tests.
- Keep every style change in CSS and reuse existing design tokens.
- Keep product decisions in the product decisions artifact instead of embedding unapproved product strategy.

## References

- `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `_condamad/stories/regression-guardrails.md`
