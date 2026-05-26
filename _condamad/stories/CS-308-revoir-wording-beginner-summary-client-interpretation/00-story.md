# Story CS-308 revoir-wording-beginner-summary-client-interpretation: Review Beginner Summary And Client Interpretation Wording
Status: ready-to-review

## Trigger / Source

- Source type: product wording brief with repository-informed boundary.
- Source reference: `_story_briefs/cs-308-revoir-wording-beginner-summary-client-interpretation.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: `/natal` exposes two B2C projections, but their surrounding app wording must be clearer and less anxiety-inducing.
- Source stakes: preserve app-owned disclaimers, avoid deterministic advice, distinguish the two reading levels, and keep degraded states understandable.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without changing backend projection logic.

## Objective

Audit and adjust the application wording around `beginner_summary_v1` and `client_interpretation_projection_v1` on `/natal`.
The story must correct labels, helper text, state messages, and critical tests without rewriting projection builders or moving disclaimers into payload ownership.

## Target State

- A wording inventory lists every visible app text around both B2C projections on `/natal`.
- The two projection titles and descriptions clearly distinguish a beginner summary from a client interpretation.
- App-owned disclaimers remain visible and tested from existing translation or component owners.
- Loading, degraded, empty, error, and entitlement messages use simple non-technical wording.
- Forbidden deterministic, medical, legal, financial, diagnostic, treatment, or guarantee wording is absent from touched app copy.
- Rejected or deferred formulations are documented with a product-decision reason.
- Targeted frontend tests cover critical labels, disclaimer visibility, and state wording.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-308-revoir-wording-beginner-summary-client-interpretation.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-308` after `CS-307`.
- Evidence 3: `docs/architecture/astrology-disclaimer-projection-policy.md` - app-owned disclaimer policy inspected.
- Evidence 4: `frontend/src/i18n/natalChart.ts` - translation owner and existing disclaimer lines inspected.
- Evidence 5: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection display owner inspected.
- Evidence 6: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection state orchestration owner inspected.
- Evidence 7: `backend/app/services/api_contracts/public/projections.py` - public projection response contract inspected as unchanged context.
- Evidence 8: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - wiring proof read.
- Evidence 9: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md` - related UX story checked for dependency context.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - scoped resolver and targeted ID lookup consulted.
- Source-alignment evidence: PASS; all source ACs map to inventory, wording changes, tests, forbidden scan, and final evidence.

## Domain Boundary

- Domain: frontend-copy
- In scope:
  - App wording visible around `beginner_summary_v1` and `client_interpretation_projection_v1` on `/natal`.
  - Titles, descriptions, labels, loading, degraded, empty, error, entitlement, and disclaimer-adjacent copy.
  - Translation keys and presentational React labels owned by the existing natal interpretation frontend files.
  - Targeted Vitest coverage for critical wording and app-owned disclaimer visibility.
  - Evidence artifacts documenting wording inventory, refused formulations, and validation output.
- Out of scope:
  - Backend projection builders, prompts, providers, payload runtime, DB schema, auth, build tooling, migrations, and plan policy.
  - Visual redesign of `/natal`, generated clients, API shape changes, new routes, registry enrichment, and new dependencies.
  - Making disclaimers depend on projection or LLM payload content.
- Explicit non-goals:
  - No backend builder, prompt, provider, projection payload, persistence, entitlement, admin, replay, or audit runtime change.
  - No new frontend route, navigation model, subscription offer redesign, or product strategy rewrite.
  - No inline style implementation.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a scoped frontend application wording audit with targeted copy corrections.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only application-owned wording around the two B2C projections on `/natal`.
  - Keep projection transport in `frontend/src/api/astrologyProjections.ts`.
  - Keep projection rendering in existing natal interpretation components.
  - Keep disclaimers owned by application code or translation owners, never by projection payload content.
  - Keep CSS changes out of scope unless a copy adjustment requires existing class reuse for text layout.
  - Preserve backend projection payloads, builder logic, prompts, providers, entitlement plans, and public API contracts unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a wording choice requires legal, medical, financial, product positioning, or plan-policy approval beyond neutral B2C copy.
- Additional validation rules:
  - Wording inventory must include every visible app-owned projection text inspected on `/natal`.
  - Refused or deferred wording must record the reason and the product owner decision requested.
  - Static scans must cover forbidden deterministic and regulated-advice terms in touched frontend copy.
  - Tests must assert the critical labels, disclaimer visibility, and degraded or unavailable state wording.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest, Testing Library, and `pnpm lint` prove rendered wording behavior. |
| Baseline Snapshot | yes | Wording inventory before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Copy owners, React owners, tests, and evidence artifacts must stay in canonical paths. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for scoped wording corrections. |
| Contract Shape | yes | The wording inventory and refused wording ledger have exact required fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend projection logic, payload disclaimers, risky terms, and inline styles must stay absent. |
| Persistent Evidence | yes | Inventory, refused wording, validation output, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Visible projection wording is inventoried. | Evidence profile: baseline_before_after_diff; `python` checks the CS-308 wording inventory. |
| AC2 | Projection titles distinguish both reading levels. | Evidence profile: json_contract_shape; `vitest` covers beginner and client labels. |
| AC3 | App-owned disclaimers stay visible. | Evidence profile: targeted_forbidden_symbol_scan; `vitest` and `rg` cover disclaimer ownership. |
| AC4 | Projection state messages use plain wording. | Evidence profile: json_contract_shape; `vitest` covers degraded, empty, error, and entitlement states. |
| AC5 | Regulated-advice wording is absent. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans forbidden terms in touched frontend files. |
| AC6 | Backend projection runtime remains unchanged. | Evidence profile: ast_architecture_guard; `AST guard`, `git diff --name-only`, and `rg` verify boundaries. |
| AC7 | Frontend validation commands pass. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` and targeted `vitest` commands pass. |
| AC8 | Final wording decisions are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-308 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the source brief, disclaimer policy, existing projection copy owners, tests, and scoped guardrails. (AC: AC1, AC3, AC6)
- [ ] Task 2: Create the wording inventory artifact for all visible app-owned projection texts on `/natal`. (AC: AC1)
- [ ] Task 3: Adjust only the labels, descriptions, and state messages that fail the inventory review. (AC: AC2, AC4, AC5)
- [ ] Task 4: Keep disclaimer text app-owned and verify no projection payload disclaimer becomes the source of truth. (AC: AC3, AC6)
- [ ] Task 5: Add or update targeted Vitest coverage for projection labels, state copy, and disclaimer visibility. (AC: AC2, AC3, AC4, AC7)
- [ ] Task 6: Run forbidden wording, inline-style, direct projection transport, and backend drift scans. (AC: AC5, AC6)
- [ ] Task 7: Persist refused wording, final wording changes, and validation output under the CS-308 capsule. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-308-revoir-wording-beginner-summary-client-interpretation.md` - source brief.
- `docs/architecture/astrology-disclaimer-projection-policy.md` - app-owned disclaimer policy.
- `frontend/src/i18n/natalChart.ts` - canonical translation owner for natal wording and disclaimers.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection cards and state messages.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - projection query state orchestration.
- `frontend/src/tests/natalInterpretation.test.tsx` - targeted projection rendering and state tests.
- `frontend/src/tests/NatalChartPage.test.tsx` - `/natal` page-level state tests.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API wrapper context, inspect only to avoid transport drift.
- `backend/app/services/api_contracts/public/projections.py` - unchanged public projection response context.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - wiring evidence.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation astrology-i18n natalChartApi` from `frontend`.
  - `AST guard` coverage through component architecture or import-boundary tests.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - `pnpm lint` from `frontend`.
  - Testing Library assertions for rendered labels, disclaimers, and state messages.
- Secondary evidence:
  - Wording inventory and refused wording ledger under `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/`.
  - Targeted `rg` scans for regulated-advice terms, payload-owned disclaimers, direct API bypass, inline styles, and backend drift.
- Static scans alone are not sufficient because:
  - This story validates user-visible React wording and state rendering.

## Contract Shape

- Contract type:
  - Frontend wording inventory and refused wording evidence contract.
- Fields:
  - `audit_date`: ISO date of the wording audit.
  - `route`: `/natal`.
  - `projection_type`: `beginner_summary_v1`, `client_interpretation_projection_v1`, or `shared_projection_panel`.
  - `state`: success, loading, degraded, empty, error, entitlement, disclaimer, or evidence.
  - `source_file`: canonical file path that owns the text.
  - `current_text`: text inspected before any allowed delta.
  - `decision`: keep, adjust, refused, or product-decision-required.
  - `final_text`: final app wording or `unchanged`.
  - `reason`: brief reason tied to clarity, non-anxiety, disclaimer policy, or B2C suitability.
  - `evidence_path`: persisted artifact path.
- Required fields:
  - `audit_date`
  - `route`
  - `projection_type`
  - `state`
  - `source_file`
  - `decision`
  - `reason`
  - `evidence_path`
- Optional fields:
  - `current_text`
  - `final_text`
  - `product_decision_owner`
  - `validation_command`
- Status codes:
  - none; this story does not change HTTP response codes.
- Serialization names:
  - Ledger keys are written exactly as listed in this section.
- Frontend type impact:
  - only targeted type updates required by wording-state tests are authorized.
- Backend type impact:
  - none; backend projection payloads and API contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, or generated manifest change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/wording-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/wording-inventory-after.md`
  - `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md`
  - `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt`
- Expected invariant:
  - The only intended application delta is scoped app wording around the two B2C projection displays on `/natal`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal translation wording | `frontend/src/i18n/natalChart.ts` | Backend builder, prompt, or payload |
| Projection card rendering | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | New duplicate renderer |
| Projection state orchestration | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Presentation-only child component |
| Targeted frontend tests | `frontend/src/tests/natalInterpretation.test.tsx` | New duplicate test harness |
| Page-level state tests | `frontend/src/tests/NatalChartPage.test.tsx` | Backend or E2E-only proof |
| Evidence artifacts | CS-308 `evidence/` directory | Application source comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing natal translation objects, projection card rendering, and projection query state mapping.
- Reuse existing Testing Library patterns and logged Vite runner commands.
- Reuse existing CSS classes and design tokens if text layout needs a minimal adjustment.
- Reuse CS-303 evidence as context only; do not duplicate its capsule content.
- Do not add external packages, generated clients, new API clients, new UI components, or duplicate projection parsing logic.
- Do not move disclaimer ownership into backend payloads, prompts, providers, or frontend ad hoc constants outside the translation owner.

## No Legacy / Forbidden Paths

- No legacy projection label path may be added beside the canonical natal interpretation owners.
- No compatibility copy source may be added for the projection panel.
- No fallback API transport may be added in the page or interpretation components.
- Do not create aliases, shims, wrappers, or duplicated state machines for projection wording.
- Do not add inline `style` attributes in TSX files.
- Do not change backend projection code, builders, prompts, providers, DB schema, migrations, entitlement plans, or public API schemas.
- Do not hide loading, empty, error, entitlement, degraded, or disclaimer states to simplify wording.

## Reintroduction Guard

- Guard path 1: projection wording must remain owned by natal i18n or the existing projection display component.
- Guard path 2: app disclaimers must remain visible and cannot be sourced from projection payload disclaimers.
- Guard path 3: touched frontend copy must not introduce regulated-advice or deterministic guarantee terms.
- Guard path 4: backend projection files must remain unchanged for this frontend wording story.
- Guard path 5: touched TSX files must not gain inline `style` attributes.
- Required deterministic guards:
  - `rg -n "medical|juridique|financier|garanti|certain|diagnostic|traitement" frontend/src`.
  - `rg -n "payload\\.disclaimers|payload\\[[\"']disclaimers" frontend/src/components/natal-interpretation frontend/src/features/natal-chart`.
  - `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
  - `git diff --name-only -- backend frontend _condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | Minimal copy layout changes keep canonical style owners. | `rg` token scan; targeted Vitest. |
| Story-local `/natal` wording guard | Projection labels, states, and disclaimers stay clear and app-owned. | Wording inventory; `vitest`; `rg`. |
| Needs-investigation | Resolver returned backend/docs guardrails for frontend wording scope; they are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-027 is not selected because pure backend prediction infra is out of scope.
- RG-041 is not selected because entitlement documentation is not edited.
- RG-042 is not selected because backend LLM documentation is not edited.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Wording inventory before | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/wording-inventory-before.md` | Record inspected app copy. |
| Wording inventory after | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/wording-inventory-after.md` | Record final copy decisions. |
| Refused ledger | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/refused-wording.md` | Document deferred formulations. |
| Validation log | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt` | Keep final validation commands. |
| Final wording evidence | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md` | Summarize implementation evidence. |
| Review output | `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/11-code-review.md` | Keep automatic review separate. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/i18n/natalChart.ts` - adjust app-owned projection labels, helper copy, state copy, and disclaimer-adjacent wording.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - change hardcoded projection display wording only.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - change only if state wording ownership requires orchestration labels.
- `frontend/src/tests/natalInterpretation.test.tsx` - cover critical projection wording, states, and disclaimers.
- `frontend/src/tests/NatalChartPage.test.tsx` - cover page-level degraded or unavailable wording that appears on `/natal`.
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/**` - persist wording and validation artifacts.

Likely tests:

- `frontend/src/tests/natalInterpretation.test.tsx` - projection labels, state messages, and app-owned disclaimer visibility.
- `frontend/src/tests/NatalChartPage.test.tsx` - `/natal` state wording and degraded page messages.
- `frontend/src/tests/natalChartApi.test.tsx` - projection API context remains unchanged unless existing expectations require label-safe fixtures.

Files not expected to change:

- `backend/app/**` - out of scope; projection runtime and public contracts remain unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no package or script change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: create wording inventory, refused wording ledger, and final evidence under the CS-308 capsule.
- VC2: from `frontend`, run `pnpm lint`.
- VC3: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation astrology-i18n natalChartApi`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC5: from repo root, run `rg -n "medical|juridique|financier|garanti|certain|diagnostic|traitement" frontend/src`.
- VC6: from repo root, run `rg -n "payload\\.disclaimers|payload\\[[\"']disclaimers" frontend/src/components/natal-interpretation frontend/src/features/natal-chart`.
- VC7: from repo root, run `rg -n "fetch\\(.*/v1/astrology/projections|axios\\(.*/v1/astrology/projections" frontend/src`.
- VC8: from repo root, run `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"`.
- VC9: from repo root with venv active, run `python -B` to assert CS-308 evidence paths and wording decision ledgers exist.

## Regression Risks

- Copy adjustments could become product positioning changes without a recorded product decision.
- Wording could sound softer while still implying certainty or regulated advice.
- Moving copy into the component could duplicate the translation owner.
- Tests could lock only French copy while missing shared projection state behavior.
- Backend payload wording ambiguity could remain; that must become a separate backend/content story rather than a frontend mask.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start from the wording inventory before changing copy.
- Keep disclaimers app-owned and visible.
- Keep every style change in CSS and reuse existing design tokens.
- Keep backend projection payload concerns in a separate story decision record.

## References

- `_story_briefs/cs-308-revoir-wording-beginner-summary-client-interpretation.md`
- `docs/architecture/astrology-disclaimer-projection-policy.md`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `backend/app/services/api_contracts/public/projections.py`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
