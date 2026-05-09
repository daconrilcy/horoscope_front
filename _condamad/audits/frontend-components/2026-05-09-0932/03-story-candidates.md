<!-- Candidats stories issus du nouvel audit CONDAMAD frontend components. -->

# Story Candidates - frontend-components

## Candidate Summary

| Candidate | Source finding | Closure intent | Priority |
|---|---|---|---|
| SC-001 | F-001 | phased-with-map | P1 |

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Converger les containers API restants de `components` vers leurs owners feature/page
- Suggested archetype: ownership-routing-refactor
- Primary domain: `frontend-components`
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Allowlist Exception, Reintroduction Guard, Persistent Evidence.
- Draft objective: remove the remaining active API/feature orchestration from `frontend/src/components/**` by relocating each exact runtime surface to the canonical feature/page owner, then delete stale component exceptions without creating wrappers, aliases, fallbacks, or re-exports.
- Closure intent: `phased-with-map`
- Must include: before artifact for every current E-010 hit; after artifact proving old component import paths are absent; exact no-wildcard allowlist reduction; no compatibility wrappers, aliases, fallback modules, or re-exports; reintroduction guard for old component paths and stale allowlist rows.
- Validation hints: run `npm run test -- component-architecture component-usage`, route/page tests for each moved slice, `npm run lint`, and targeted `rg` scans for each old component path and stale exception.
- Blockers: external import evidence, absent canonical owner decision, or any need to preserve an old component path must stop implementation and be classified as `needs-user-decision`.

## Exhaustive Files To Modify

### F-001

Application files in the current affected surface:

- `frontend/src/components/AdminGuard.tsx`
- `frontend/src/components/B2BReconciliationPanel.tsx`
- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/components/SupportOpsPanel.tsx`
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx`
- `frontend/src/components/layout/BottomNav.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/settings/DeleteAccountModal.tsx`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx`

Likely consumer files to inspect and update:

- `frontend/src/pages/**`
- `frontend/src/layouts/**` if present
- `frontend/src/app/**` if present
- `frontend/src/tests/**` tests importing the moved owners
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`

Governance/test files:

- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `_condamad/stories/regression-guardrails.md` only if a story creates a new durable invariant.

## Complete Closure Map

| Slice | Current surface | Target owner decision | Stop condition |
|---|---|---|---|
| Admin routing guard | `components/AdminGuard.tsx` | route-level admin guard or admin feature owner | no `AdminGuard` API import under `components`; old component path absent; route/admin tests pass. |
| Enterprise/B2B runtime panels | `components/B2BReconciliationPanel.tsx`, `components/EnterpriseCredentialsPanel.tsx` | enterprise or B2B feature/page owner | both exceptions removed; enterprise/reconciliation tests pass; no compatibility export under `components`. |
| Admin ops/support | `components/SupportOpsPanel.tsx` | admin ops/support feature owner | exception removed; support/admin tests pass; no old path import. |
| Settings privacy | `components/settings/DeleteAccountModal.tsx` | settings/privacy feature or page-adjacent owner | exception removed; settings/privacy tests pass; no modal API owner under shared components. |
| Dashboard summary | `components/dashboard/useDashboardAstroSummary.ts`, `DashboardHoroscopeSummaryCardContainer.tsx` | dashboard feature/hooks owner | no dashboard API hook under `components`; dashboard tests pass; dashboard barrel remains coherent. |
| App layout auth state | `components/layout/{BottomNav,Header,Sidebar}.tsx` | route layout/provider owner or prop-driven layout components | layout components under `components` become presentational/API-free or move to layout owner; layout tests pass. |
| UI test type dependency | `components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | extract `UpgradeHint` type to neutral UI/billing contract or adjust test fixture | no API import from a component test under `components`; UI tests pass. |

## Must Include

- before artifact listing every current hit from E-010 with owner, consumer, canonical target, and current tests;
- after artifact proving each moved slice has no old component import path;
- no-wildcard allowlist policy: remove exact rows only after the moved surface is proved canonical elsewhere;
- no compatibility wrappers, aliases, fallback modules, or re-exports under `frontend/src/components/**`;
- reintroduction guard that fails on old component paths and stale allowlist rows;
- validation commands:
  - `npm run test -- component-architecture component-usage`
  - route/page tests for each moved slice
  - `npm run lint`
  - targeted `rg` scans for each old component path and stale exception.

## Blockers / User Decision

- If any current component path is externally imported outside first-party `frontend/src/**`, classify that exact surface as `needs-user-decision` before deletion.
- If a target feature/page owner does not exist, create the smallest owner consistent with the slice; do not use a broad `features/misc` or compatibility namespace.
- Stop after the listed closure map is exhausted. Do not emit a vague follow-up without a new scan proving a new surface.

## Deferred Non-Domain Context

None for F-001 inside the audited component boundary. The candidate may be split into the slices above for implementation, but this audit provides the complete current closure map.

## Findings Without Implementation Candidate

### F-002

Application files: none.

Governance/test files: none.

Rationale: auth and natal relocations are closed under current evidence.

### F-003

Application files: none.

Governance/test files: none.

Rationale: deleted test-only surfaces have no active hits and are guarded.

### F-004

Application files: none.

Governance/test files: none.

Rationale: guard suite is passing; no new guard story is required for the audited surfaces.
