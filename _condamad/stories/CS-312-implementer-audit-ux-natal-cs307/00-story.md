# Story CS-312 implementer-audit-ux-natal-cs307: Implement CS-307 Natal UX Audit
Status: ready-to-dev

## Trigger / Source

- Source type: audit closure brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-312-implementer-audit-ux-natal-cs307.md`.
- Selected mode: Audit-to-story with Fast Story Writer Mode.
- Problem statement: CS-307 is drafted but not implemented, so `/natal` UX closure after projection wiring has no final evidence.
- Source stakes: execute the real `/natal` audit, persist browser proof, fix only demonstrated UI irritants, and close CS-307 with validation.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief stakes without replacing them.

## Objective

Implement the CS-307 `/natal` UX audit for real, persist the missing evidence capsule, and correct only UI defects proven by the audit ledger.
The story closes the open CS-307 evidence gap without changing backend contracts, projection policy, plans, providers, DB, or migrations.

## Target State

- CS-307 has `generated/10-final-evidence.md` with a dated implementation summary and validation outcome.
- CS-307 has `ux-audit-before.md`, `ux-audit-after.md`, `browser-qa.md`, `product-decisions.md`, and `validation.txt`.
- Desktop, tablet, and mobile screenshots are persisted under the CS-307 evidence capsule.
- Loading, success, empty, error, entitlement, degraded, and disclaimer states are verified on `/natal`.
- Proven UI irritants are corrected only in existing React and CSS owners.
- Targeted Vitest coverage proves corrected states, and standard frontend validation is recorded.
- CS-307 and `_condamad/stories/story-status.md` move to `done` only after implementation evidence passes.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-312-implementer-audit-ux-natal-cs307.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; `CS-311` was the latest CS row before this story.
- Evidence 3: `_condamad/reports/CS-307-CS-311-delivery-report.md` - CS-307 classified as `Not evidenced`.
- Evidence 4: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md` - open CS-307 contract read.
- Evidence 5: CS-307 lacks `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/generated/10-final-evidence.md`.
- Evidence 6: CS-303 final evidence proves projection wiring and notes browser/manual startup risk.
- Evidence 7: CS-306 final evidence proves prior browser QA with controlled projection responses.
- Evidence 8: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner inspected.
- Evidence 9: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection display owner inspected.
- Evidence 10: `frontend/src/features/natal-chart/NatalInterpretation.css` - existing CSS owner inspected.
- Evidence 11: `frontend/src/tests/natalInterpretation.test.tsx` - projection state tests inspected.
- Evidence 12: `_condamad/stories/regression-guardrails.md` - scoped resolver consulted through `resolve_guardrails.py`.
- Source-alignment evidence: PASS; the final story executes the brief closure map and forbids unrelated product or backend drift.

## Domain Boundary

- Domain: frontend-ux
- In scope:
  - Execute CS-307 implementation closure for `/natal` UX after B2C projection wiring.
  - Create the missing CS-307 final evidence and audit artifacts.
  - Run real browser QA on desktop, tablet, and mobile for `/natal`.
  - Verify loading, success, empty, error, entitlement, degraded, and disclaimer states.
  - Correct only UI defects demonstrated in `ux-audit-before.md` or `browser-qa.md`.
  - Update existing targeted Vitest coverage for corrected states.
  - Mark CS-307 `done` only after evidence and validation are complete.
- Out of scope:
  - Backend, API contracts, projection payload builders, providers, prompts, DB, auth, i18n rewrites, build tooling, and migrations.
  - Full redesign of `/natal`, new navigation, new component system, generated client, and package changes.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No backend route, serializer, projection builder, entitlement policy, prompt, provider, admin, replay, or audit runtime change.
  - No product strategy decision embedded in code.
  - No inline style implementation.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend UX audit implementation with evidence capsule closure.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only UI surfaces proven defective by CS-307 audit evidence.
  - Keep projection transport in `frontend/src/api/astrologyProjections.ts`.
  - Keep projection orchestration in `frontend/src/features/natal-chart/NatalInterpretation.tsx`.
  - Keep projection rendering in `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`.
  - Keep style changes in existing CSS files and reuse existing variables, colors, spacing, borders, and responsive patterns.
  - Keep loading, success, empty, error, entitlement, degraded, and disclaimer states visible.
  - Preserve backend projection payloads, entitlement policy, and public API contracts unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a finding needs product positioning, commercial policy, or copy strategy beyond obvious UI correction.
- Additional validation rules:
  - Browser QA must record route, viewport, state, result, and screenshot path for each visual check.
  - Audit entries must use decisions `corrected`, `acceptable`, or `product-decision-required`.
  - Static scans must prove no inline styles and no direct projection HTTP call in touched frontend files.
  - Corrected UI states must have Vitest coverage or a bounded manual browser check in `browser-qa.md`.
  - CS-307 tracker status must remain unchanged until final evidence and validation are complete.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Browser QA, Vitest, and `pnpm lint` prove the `/natal` UX result. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | React, CSS, tests, screenshots, and generated evidence must stay in canonical owners. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for this closure story. |
| Contract Shape | yes | The audit ledger, browser ledger, and final evidence have exact required fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Inline styles, direct projection calls, and backend changes must stay absent. |
| Persistent Evidence | yes | CS-307 audit, screenshots, validation output, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | CS-307 final evidence exists. | Evidence profile: baseline_before_after_diff; `python` checks `generated/10-final-evidence.md`. |
| AC2 | UX audit artifacts classify inspected findings. | Evidence profile: baseline_before_after_diff; `python` checks audit decisions and artifact paths. |
| AC3 | Browser QA covers three viewports. | Evidence profile: baseline_before_after_diff; Manual check: screenshots verify desktop tablet mobile. |
| AC4 | Projection states remain understandable. | Evidence profile: json_contract_shape; `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`. |
| AC5 | Disclaimers remain visible. | Evidence profile: json_contract_shape; `vitest` or Manual check: screenshot evidence covers disclaimer placement. |
| AC6 | UI fixes stay in existing owners. | Evidence profile: ast_architecture_guard; `AST guard`, `rg`, and `component-architecture-guards`. |
| AC7 | Standard frontend validation is recorded. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and full `vitest` output. |
| AC8 | Product decisions stay outside code. | Evidence profile: baseline_before_after_diff; `python` checks `product-decisions.md`. |
| AC9 | CS-307 tracker status is closed only with proof. | Evidence profile: baseline_before_after_diff; `python` checks tracker and final evidence. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-307, CS-303 evidence, CS-306 evidence, owners, tests, and scoped guardrails. (AC: AC1, AC6)
- [ ] Task 2: Create CS-307 `ux-audit-before.md` from browser and test observations before UI edits. (AC: AC2, AC3)
- [ ] Task 3: Capture `/natal` desktop, tablet, and mobile screenshots for the inspected states. (AC: AC3, AC5)
- [ ] Task 4: Verify loading, success, empty, error, entitlement, degraded, and disclaimer states. (AC: AC4, AC5)
- [ ] Task 5: Correct only demonstrated UX defects in existing React and CSS owners. (AC: AC2, AC4, AC6)
- [ ] Task 6: Add or adjust focused Vitest coverage for corrected UI states. (AC: AC4, AC5, AC7)
- [ ] Task 7: Create CS-307 `ux-audit-after.md`, `browser-qa.md`, and `product-decisions.md`. (AC: AC2, AC3, AC8)
- [ ] Task 8: Run inline-style, projection-ownership, and component architecture guards. (AC: AC6)
- [ ] Task 9: Run targeted and full frontend validation, then persist `validation.txt`. (AC: AC7)
- [ ] Task 10: Write CS-307 `generated/10-final-evidence.md` and update CS-307 tracker status to `done`. (AC: AC1, AC9)

## Files to Inspect First

- `_story_briefs/cs-312-implementer-audit-ux-natal-cs307.md` - source brief.
- `_condamad/reports/CS-307-CS-311-delivery-report.md` - delivery gap source.
- `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md` - source implementation contract.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - wiring proof.
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md` - prior browser QA proof.
- `frontend/src/pages/NatalChartPage.tsx` - `/natal` page composition owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering owner.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - styling owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - projection and disclaimer tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - page integration tests.
- `frontend/src/tests/component-architecture-guards.test.ts` - AST guard and ownership tests.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard`: `frontend/src/tests/component-architecture-guards.test.ts`.
  - Real browser checks for `/natal` on desktop, tablet, and mobile viewports.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation` from `frontend`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run NatalChartPage` from `frontend`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - `pnpm lint` from `frontend`.
- Secondary evidence:
  - CS-307 audit artifacts and screenshots under `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/`.
  - Targeted `rg` scans for inline styles, direct projection HTTP calls, disclaimer ownership, and backend drift.
- Static scans alone are not sufficient because:
  - Visual hierarchy, responsive overlap, and disclaimer placement require browser evidence.

## Contract Shape

- Contract type:
  - CS-307 UX audit evidence and browser QA closure contract.
- Fields:
  - `audit_date`: ISO date of the audit.
  - `route`: `/natal`.
  - `viewport`: desktop, tablet, mobile, or not-browser.
  - `state`: loading, success, empty, error, entitlement, degraded, disclaimer, or visual-hierarchy.
  - `finding`: inspected UX issue or accepted state.
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
  - `viewport`
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
  - CS-307 `generated/10-final-evidence.md` must summarize validation, files changed, residual risks, and closure status.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-before.md`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa.md`
- Comparison after implementation:
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/ux-audit-after.md`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/validation.txt`
  - `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/generated/10-final-evidence.md`
- Expected invariant:
  - The only intended application delta is correction of proven `/natal` UX defects inside existing frontend owners.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `/natal` page composition | `frontend/src/pages/NatalChartPage.tsx` | New route or marketing page |
| Projection orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | API module or unrelated page |
| Projection rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Backend or admin component |
| Natal interpretation styles | `frontend/src/features/natal-chart/NatalInterpretation.css` | Inline TSX `style` attributes |
| Targeted tests | `frontend/src/tests/natalInterpretation.test.tsx` and `frontend/src/tests/NatalChartPage.test.tsx` | Duplicate harness |
| Architecture guards | `frontend/src/tests/component-architecture-guards.test.ts` | Ad hoc script |
| CS-307 evidence | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/` | Application source comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing `/natal` components, projection state mapping, CSS classes, and test helpers.
- Reuse existing design variables, color tokens, spacing tokens, borders, and responsive patterns.
- Reuse existing Vitest and logged Vite runner commands.
- Reuse CS-303 and CS-306 evidence as context only; do not duplicate their capsule content.
- Do not add external packages, generated clients, API clients, UI framework components, or duplicate projection parsing logic.
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
- Guard path 4: legal disclaimer copy must remain app-owned and visible inside interpretation content.
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
| Browser screenshots | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-screenshots/` | Store visual proof. |
| Validation log | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/validation.txt` | Keep final validation commands. |
| Product decisions | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/product-decisions.md` | List decisions left to product. |
| Final evidence | `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/generated/10-final-evidence.md` | Close CS-307. |
| Review output | `_condamad/stories/CS-312-implementer-audit-ux-natal-cs307/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

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
- `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/generated/10-final-evidence.md` - close CS-307.
- `_condamad/stories/story-status.md` - mark CS-307 done after validation evidence exists.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - projection rendering, state, disclaimer, and corrected UI behavior.
- `frontend/src/tests/NatalChartPage.test.tsx` - `/natal` page-level integration states.
- `frontend/src/tests/component-architecture-guards.test.ts` - ownership and architecture guards.

Files not expected to change:

- `backend/app/**` - out of scope; projection runtime remains unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story work must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create CS-307 audit artifacts under `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/`.
- VC2: open `/natal` in a real browser on desktop, tablet, and mobile; persist screenshots and `browser-qa.md`.
- VC3: from `frontend`, run `pnpm lint`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage`.
- VC5: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
- VC6: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC7: from repo root, run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages -g "*.tsx"`.
- VC8: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC9: from repo root, run `rg -n "legalNoticeLines|disclaimerTitle" frontend/src/components/natal-interpretation frontend/src/i18n frontend/src/tests`.
- VC10: from repo root with venv active, run `python -B` to assert CS-307 evidence paths, audit decisions, and tracker status.

## Regression Risks

- UX audit scope could expand into a broad redesign instead of correcting only proven defects.
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
- Start from CS-307 `ux-audit-before.md` before changing UI code.
- Correct only defects that can be evidenced from `/natal` screenshots or tests.
- Keep every style change in CSS and reuse existing design tokens.
- Keep product decisions in `product-decisions.md` instead of embedding unapproved product strategy.
- Keep CS-307 `done` status gated by final evidence, not by story drafting evidence.

## References

- `_story_briefs/cs-312-implementer-audit-ux-natal-cs307.md`
- `_condamad/reports/CS-307-CS-311-delivery-report.md`
- `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`
