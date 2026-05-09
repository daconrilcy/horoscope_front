# Story CS-120 converger-containers-api-restants-components-vers-owners: Converger les containers API restants de components vers leurs owners feature/page

Status: done

## 1. Objective

Retirer les dernieres surfaces `frontend/src/components/**` qui restent owners
d'orchestration API/feature en les routant vers leurs owners canoniques
feature, page, layout ou test neutre. La story ferme la carte finie de `F-001`
de l'audit `frontend-components/2026-05-09-0932` sans wrapper de compatibilite,
alias, fallback, re-export ou exception wildcard.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md#SC-001`
- Reason for change: l'audit confirme que les tranches auth, natal et test-only sont fermees.
  Des composants partages restent proprietaires d'appels API ou d'imports feature.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - migrer ou rendre API-free toutes les surfaces exactes listees par `SC-001`;
  - repointer les consommateurs first-party vers les owners canoniques;
  - reduire `COMPONENT_API_IMPORT_EXCEPTIONS` sans wildcard ni entree stale;
  - garder ou durcir les guards `component-architecture` et `component-usage`;
  - produire des artefacts before/after persistants pour chaque batch de la closure map.
- Out of scope:
  - changer les contrats backend, endpoints, payloads ou erreurs API;
  - refondre le design system, les tokens CSS ou les primitives UI;
  - rouvrir les stories CS-117, CS-118 ou CS-119 deja fermees;
  - ajouter un nouveau domaine fourre-tout comme `features/misc`.
- Explicit non-goals:
  - ne pas modifier les invariants `RG-047`, `RG-048`, `RG-050`, `RG-056`, `RG-057`, `RG-071`, `RG-072`, `RG-073`, `RG-074`;
  - ne pas conserver un ancien chemin `components/**` par commodite;
  - ne pas accepter `PASS with limitation`, exception large, fallback non classe ou residual cache;
  - ne pas changer le comportement observable des routes, panels, modales, layouts et tests concernes.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: legacy-facade-removal
- Archetype reason: les anciens chemins `components/**` proprietaires d'API doivent disparaitre
  apres migration canonique, sans wrapper, alias, fallback ou re-export.
- Behavior change allowed: no
- Behavior change constraints:
  - les workflows admin, enterprise/B2B, support ops, settings privacy, dashboard, layout auth et `UpgradeCTA` doivent conserver leur comportement observable;
  - les seules differences autorisees sont les chemins d'import, l'emplacement des containers/hooks/tests et la suppression des anciennes exceptions exactes.
- Deletion allowed: yes
- Replacement allowed: no
- Replacement clarification:
  - les consommateurs peuvent etre repointes vers un owner canonique feature/page/layout/test;
  - aucun remplacement sous `frontend/src/components/**` ne peut preserver l'ancien chemin comme facade, wrapper, alias ou re-export.
- User decision required if: un import externe a `frontend/src/**`, une route publique documentee,
  ou une absence d'owner canonique impose de garder un ancien chemin `components/**`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les guards AST et les tests route/panel/layout doivent prouver l'ownership effectif, pas seulement des scans texte. |
| Baseline Snapshot | yes | la story doit comparer l'inventaire E-010 avant/apres et les exceptions avant/apres. |
| Ownership Routing | yes | chaque surface de la closure map doit recevoir un owner canonique ou bloquer. |
| Allowlist Exception | yes | le scope touche un registre d'exceptions existant qui doit etre reduit exactement sans wildcard. |
| Contract Shape | no | aucun DTO, payload, schema OpenAPI, status code ou contrat public n'est modifie. |
| Batch Migration | yes | la closure map contient plusieurs slices independants a migrer et prouver separement. |
| Reintroduction Guard | yes | les anciens chemins, imports et exceptions stale doivent echouer s'ils reviennent. |
| Persistent Evidence | yes | les audits before/after, mappings et resultats doivent etre conserves dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/component-architecture-guards.test.ts` via `npm run test -- component-architecture`;
  - TypeScript module graph via `npm run lint`;
  - route/panel/layout/component tests cibles listés dans le plan de validation.
- Secondary evidence:
  - scans `rg` cibles des imports API/feature sous `frontend/src/components`;
  - scans zero-hit des anciens chemins `components/**` et des entrees stale de l'allowlist.
- Static scans alone are not sufficient for this story because:
  - un zero-hit ne prouve pas que les pages admin/settings/dashboard/layout continuent de monter les memes workflows;
  - le guard AST doit valider l'absence d'exceptions implicites et de wildcards.
- Command:
  - `cd frontend && npm run test -- component-architecture component-usage`
  - `cd frontend && npm run lint`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-remaining-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-remaining-after.md`
- Comparison command or test:
  - `cd frontend && npm run test -- component-architecture component-usage`
  - targeted scans from section 21.
- Expected invariant:
  - after implementation, no runtime API/feature orchestration remains under `frontend/src/components/**`;
  - any remaining entry is a non-runtime test/type exception explicitly justified, or the story is blocked.
- Allowed differences:
  - import paths and file locations may change only for the slices listed in the Batch Migration Plan.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin route guard | route-level admin owner or admin feature guard | `frontend/src/components/AdminGuard.tsx` as API owner |
| Enterprise/B2B runtime panels | enterprise or B2B feature/page owner | shared `components` container with API calls |
| Admin ops/support panel | admin ops/support feature owner | shared `components` container with API calls |
| Settings privacy deletion modal | settings/privacy page-adjacent owner or feature owner | `components/settings/**` API owner |
| Dashboard astro summary hook/container | dashboard feature/hooks owner | `components/dashboard/**` API hook owner |
| Layout auth state | route layout/provider owner or prop-driven presentational layout components | layout components under `components` reading API/feature state directly |
| UI billing hint test type | neutral UI/billing test contract or local fixture type | component test importing API billing type directly |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/AdminGuard.tsx` | exception admin routing | remove after route/admin owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/B2BReconciliationPanel.tsx` | exception enterprise/B2B | remove after owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/EnterpriseCredentialsPanel.tsx` | exception enterprise credentials | remove after owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/SupportOpsPanel.tsx` | exception admin ops | remove after support/admin owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/dashboard/useDashboardAstroSummary.ts` | exception dashboard hook | remove after owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/layout/BottomNav.tsx` | exception layout auth state | remove after API-free evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/layout/Header.tsx` | exception layout auth state | remove after API-free evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/layout/Sidebar.tsx` | exception layout auth state | remove after API-free evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/settings/DeleteAccountModal.tsx` | exception settings privacy | remove after owner evidence |
| `frontend/src/tests/component-architecture-allowlist.ts` | `components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | exception test type-only | remove after fixture evidence |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan;
- any retained exception after this story requires `needs-user-decision` evidence, not a silent limitation.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| admin-guard | `components/AdminGuard.tsx` | admin route/feature guard | admin route imports | router/admin tests | old path absent | missing route owner |
| enterprise-b2b | `B2BReconciliationPanel` and `EnterpriseCredentialsPanel` | enterprise/B2B owner | admin page imports | panel tests | no panel re-export | missing owner |
| support-ops | `components/SupportOpsPanel.tsx` | admin ops/support owner | support imports | support tests | old path absent | owner ambiguity |
| settings-privacy | `components/settings/DeleteAccountModal.tsx` | settings/privacy owner | account settings imports | settings tests | modal path absent | owner absent |
| dashboard-summary | dashboard summary hook/container | dashboard hooks owner | dashboard imports | `DashboardPage` tests | no API hook in components | owner absent |
| layout-auth | `BottomNav`, `Header`, `Sidebar` | layout provider or props | layout imports | layout/router tests | API-free layout | auth owner absent |
| ui-test-type | `UpgradeCTA.test.tsx` | neutral fixture/contract | test only | UpgradeCTA test | no API type import | type fidelity risk |

Closure map:

- Total affected surface: exactly the files listed in `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md#Exhaustive-Files-To-Modify`.
- Batches included in this story: all seven rows above.
- Batches intentionally deferred: none.
- Stop condition for the source finding:
  every row is moved, API-free, or test-neutral with stale allowlist removed and after evidence persisted.
  Otherwise the story stops with exact `needs-user-decision` blocker before claiming closure.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| before inventory | `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-remaining-before.md` | hits E-010 |
| after inventory | `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-remaining-after.md` | old paths absent |
| migration map | `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-owner-migration.md` | decisions by batch |
| final evidence | `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/generated/10-final-evidence.md` | command results |

For audit-sourced stories, include at least one artifact or generated evidence entry that records source finding closure status and any remaining closure map.

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- stale rows for all old paths listed in `COMPONENT_API_IMPORT_EXCEPTIONS`;
- imports from `@components/B2BReconciliationPanel`, `@components/EnterpriseCredentialsPanel`, `@components/SupportOpsPanel`, `@components/settings/DeleteAccountModal`;
- imports ending in `components/AdminGuard`, `components/dashboard/useDashboardAstroSummary`, or `components/dashboard/DashboardHoroscopeSummaryCardContainer`;
- direct API/feature imports, `apiFetch(`, raw `fetch(` or `axios` in `frontend/src/components/**` without exact exception;
- `import type { UpgradeHint } from '../../../api/billing'` in `components/ui/UpgradeCTA/UpgradeCTA.test.tsx`.

Deterministic source:

- forbidden symbols checked by AST guard in `frontend/src/tests/component-architecture-guards.test.ts`;
- exact exception register `frontend/src/tests/component-architecture-allowlist.ts`;
- TypeScript module graph from `npm run lint` and targeted forbidden symbol scans in section 21.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `cd frontend && npm run test -- component-architecture component-usage`
- Evidence profile: `targeted_forbidden_symbol_scan`; targeted `rg` commands in section 21.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-components/2026-05-09-0932/02-finding-register.md#F-001`
- Closure proof required:
  before/after artifacts, per-batch migration map, architecture guards, exact allowlist diff,
  route/page/panel/layout tests, and targeted zero-hit scans for old component paths.
- Known residual in-domain work: none if all batches pass; otherwise only exact rows marked `needs-user-decision` with blocker evidence and no claim of closure.
- Deferred non-domain concerns: none.
- Remaining closure map:
  - admin-guard: close or block;
  - enterprise-b2b: close or block;
  - support-ops: close or block;
  - settings-privacy: close or block;
  - dashboard-summary: close or block;
  - layout-auth: close or block;
  - ui-test-type: close or block.
- Stop condition:
  no runtime API/feature orchestration remains under `frontend/src/components/**`;
  every stale allowlist row is removed, tests and scans pass, and no hidden residual work remains.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-components/2026-05-09-0932/00-audit-report.md` -
  status `phased-with-map`; auth, natal and test-only are closed, but `F-001` remains active.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-09-0932/02-finding-register.md#F-001` - exact active finding lists remaining API-owning component surfaces.
- Evidence 3: `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md#SC-001` - finite closure map and validation hints.
- Evidence 4: `frontend/src/tests/component-architecture-allowlist.ts` - current `COMPONENT_API_IMPORT_EXCEPTIONS` contains exact rows for the remaining surfaces.
- Evidence 5: `frontend/src/tests/component-architecture-guards.test.ts` - guard currently enforces exact component API/feature exceptions and stale-entry detection.
- Evidence 6: `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - auth relocation pattern forbids compatibility re-exports.
- Evidence 7: `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/00-story.md` - natal relocation pattern keeps orchestration under feature owner.
- Evidence 8: `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` - deleted test-only surfaces must not return.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `frontend/src/components/**` is not the owner of runtime API/feature orchestration.
- Each current E-010 surface is moved to a canonical owner, made API-free,
  or blocked with exact `needs-user-decision` evidence before implementation continues.
- `COMPONENT_API_IMPORT_EXCEPTIONS` contains no stale row for the migrated surfaces and no wildcard/folder-wide exception.
- Old component paths are absent from imports, tests, CSS wrappers, barrels and re-exports.
- Component architecture and usage guards pass with persisted final evidence.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-069` - shared components must not own unclassified API/feature orchestration.
  - `RG-070` - no component `@ts-nocheck` may be introduced while moving surfaces.
  - `RG-071` - natal owner decomposition must not be reopened by moving unrelated component orchestration.
  - `RG-072` - component usage classification must remain exact after file moves/deletions.
  - `RG-073` - old natal component paths must not return during broad component edits.
  - `RG-074` - CS-119 deleted test-only surfaces must not be recreated.
  - `RG-047`, `RG-048`, `RG-050`, `RG-056`, `RG-057` - style, fallback, design-system and No Legacy guards must remain green for touched component/UI files.
- Non-applicable invariants:
  - `RG-064` and `RG-068` are secondary validation context for routes/layouts.
    Do not change their ownership decisions except for import repoints to canonical owners.
- Required regression evidence:
  - `npm run test -- component-architecture component-usage`
  - route/page/panel/layout tests listed in section 21
  - `npm run lint`
  - targeted zero-hit scans for stale component paths and allowlist rows.
- Allowed differences:
  - file locations and import paths for the seven batches only;
  - removal of exact allowlist rows after canonical owner proof.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline captures every current E-010 hit before edits. | Evidence profile: `baseline_before_after_diff`; section 21 API/feature `rg` scan; before artifact. |
| AC2 | The seven-batch closure map has one exact final decision per batch. | Runtime evidence: AST guard test; `npm run test -- component-architecture`. |
| AC3 | `COMPONENT_API_IMPORT_EXCEPTIONS` is reduced exactly. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-architecture`; allowlist scans. |
| AC4 | Old component import paths are absent. | Evidence profile: `repo_wide_negative_scan`; targeted `rg` commands from section 21. |
| AC5 | Affected runtime UI remains equivalent. | Runtime evidence: section 21 runtime tests; `npm run test -- B2BReconciliationPanel`; `B2BReconciliationPanel.test.tsx`. |
| AC6 | Regression guards for CS-117 to CS-119 pass. | Evidence profile: `reintroduction_guard`; `npm run test -- component-architecture component-usage`. |
| AC7 | Persistent after evidence proves closure or exact blocker status. | Evidence profile: `persistent_evidence`; run the `python` persistence block in section 21. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before evidence (AC: AC1, AC7)
  - [ ] Run the current component API/feature import scan from the audit and persist every E-010 hit.
  - [ ] Record current consumers, current tests, current allowlist rows and proposed canonical owner per file.

- [ ] Task 2 - Migrate admin, enterprise/B2B and support ops slices (AC: AC2, AC4, AC5)
  - [ ] Move or rehome `AdminGuard`, B2B reconciliation, enterprise credentials and support ops into exact admin/enterprise/support owners.
  - [ ] Repoint first-party consumers and tests to canonical owners.
  - [ ] Delete old component files only after no external blocker remains.

- [ ] Task 3 - Migrate settings, dashboard and layout auth slices (AC: AC2, AC4, AC5)
  - [ ] Move or make API-free `DeleteAccountModal`, dashboard astro summary hook/container and layout auth-state components.
  - [ ] Keep presentational layout components under `components` only if they no longer import API/feature state.
  - [ ] Repoint affected pages/layouts/tests without adding compatibility exports.

- [ ] Task 4 - Remove UI test API type dependency (AC: AC2, AC3, AC5)
  - [ ] Replace the `UpgradeCTA` test import from API billing with a neutral contract or local structural fixture.
  - [ ] Preserve `UpgradeCTA` behavior assertions.

- [ ] Task 5 - Reduce and harden architecture guards (AC: AC3, AC4, AC6)
  - [ ] Remove only migrated rows from `COMPONENT_API_IMPORT_EXCEPTIONS`.
  - [ ] Add explicit anti-return assertions for stale paths when current generic guard is insufficient.
  - [ ] Prove no wildcard or folder-wide exception exists.

- [ ] Task 6 - Persist after evidence and validate (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
  - [ ] Write after inventory, migration map and final evidence.
  - [ ] Run all validation commands or record exact blocker reason before stopping.
  - [ ] Enrich `_condamad/stories/regression-guardrails.md` only if a new durable invariant beyond `RG-069` to `RG-074` is established.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - existing API clients and hooks under `frontend/src/api/**` and `frontend/src/hooks/**`;
  - existing feature owners when present under `frontend/src/features/**`;
  - existing route/page/layout owners under `frontend/src/pages/**`, `frontend/src/layouts/**` or `frontend/src/app/**` when present;
  - existing component architecture guard helpers in `frontend/src/tests/component-architecture-guards.test.ts`;
  - existing UI primitives and CSS files; no inline style migration is part of this story.
- Do not recreate:
  - duplicate API clients, entitlement hooks, auth state readers, dashboard hooks or account deletion services;
  - a broad `features/misc`, `features/shared-api`, `components/containers` or equivalent catch-all namespace;
  - old component barrels that preserve moved paths.
- Shared abstraction allowed only if:
  - at least two in-scope consumers need the same responsibility;
  - no existing owner already provides it;
  - the abstraction lives under the canonical feature/page/layout owner, not under shared `components` as API owner.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `frontend/src/components/AdminGuard.tsx` as API/feature owner after migration;
- `frontend/src/components/B2BReconciliationPanel.tsx`;
- `frontend/src/components/EnterpriseCredentialsPanel.tsx`;
- `frontend/src/components/SupportOpsPanel.tsx`;
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts` as API hook owner;
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` as API container owner;
- `frontend/src/components/settings/DeleteAccountModal.tsx` as API owner;
- API/feature imports in `frontend/src/components/layout/BottomNav.tsx`, `Header.tsx`, `Sidebar.tsx`;
- `import type { UpgradeHint } from '../../../api/billing'` in `components/ui/UpgradeCTA/UpgradeCTA.test.tsx`;
- stale rows for any of the above in `COMPONENT_API_IMPORT_EXCEPTIONS`;
- any `export * from` or wrapper preserving old component paths.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

For this story, old component files start as `canonical-active` only until their
consumers are repointed. After canonical owner proof, they must become
`historical-facade` or `dead` and be deleted, not retained.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/component-api-owner-migration.md`

Allowed decisions in this audit are `keep`, `delete`, `replace-consumer` and
`needs-user-decision`. A `keep` decision for an old `components/**` API owner is
valid only with external-active evidence and must block closure.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin access guard orchestration | route-level admin owner or admin feature guard | `frontend/src/components/AdminGuard.tsx` |
| B2B reconciliation UI with API calls | enterprise/B2B feature or admin page owner | `frontend/src/components/B2BReconciliationPanel.tsx` |
| Enterprise credentials API panel | enterprise/B2B feature or admin page owner | `frontend/src/components/EnterpriseCredentialsPanel.tsx` |
| Support operations API panel | admin ops/support feature owner | `frontend/src/components/SupportOpsPanel.tsx` |
| Account deletion mutation UI | settings/privacy feature or page-adjacent owner | `frontend/src/components/settings/DeleteAccountModal.tsx` |
| Dashboard astro summary API hook/container | dashboard feature/hooks owner | `frontend/src/components/dashboard/**` API hook/container |
| Layout auth state | app/layout provider or prop-driven presentational layout components | API/feature imports in `frontend/src/components/layout/**` |
| Upgrade hint test data | neutral UI/billing test contract or local fixture | API billing type import from component test |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

For this frontend story, blocker evidence includes:

- import usage outside first-party `frontend/src/**`;
- public docs, generated route/client artifacts or deployment templates pointing to the old component path;
- absence of a canonical owner after inspecting pages/layouts/features/app namespaces.

## 17. Generated Contract Check

Generated contract check is required for this frontend removal story even though
no backend OpenAPI or generated API client should change.

Required generated-contract evidence:

- route manifest substitute: targeted route, layout, dashboard and settings tests prove affected mounting remains valid;
- generated client/schema absence: `cd frontend && npm run lint` proves the TypeScript module graph has no orphaned old component imports;
- old path absence: targeted `rg` scans from section 21 return no hits for removed component paths and stale allowlist rows;
- OpenAPI path absence: no OpenAPI route is modified; final evidence must state that backend generated API contracts were not touched.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-components/2026-05-09-0932/00-audit-report.md`
- `_condamad/audits/frontend-components/2026-05-09-0932/02-finding-register.md`
- `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/component-usage-guards.test.ts`
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
- consumers discovered by `rg` under `frontend/src/pages/**`, `frontend/src/features/**`, `frontend/src/layouts/**`, `frontend/src/app/**` and `frontend/src/tests/**`.

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/component-architecture-allowlist.ts` - remove migrated exact exceptions.
- `frontend/src/tests/component-architecture-guards.test.ts` - add anti-return assertions if generic guard is insufficient.
- `frontend/src/components/AdminGuard.tsx` - move/delete or make non-API owner according to canonical route owner.
- `frontend/src/components/B2BReconciliationPanel.tsx` - move/delete after enterprise owner migration.
- `frontend/src/components/EnterpriseCredentialsPanel.tsx` - move/delete after enterprise owner migration.
- `frontend/src/components/SupportOpsPanel.tsx` - move/delete after support owner migration.
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts` - move/delete under dashboard owner.
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` - move/delete or make presentational after hook migration.
- `frontend/src/components/layout/BottomNav.tsx` - remove API/feature ownership or move to layout owner.
- `frontend/src/components/layout/Header.tsx` - remove API/feature ownership or move to layout owner.
- `frontend/src/components/layout/Sidebar.tsx` - remove API/feature ownership or move to layout owner.
- `frontend/src/components/settings/DeleteAccountModal.tsx` - move/delete under settings/privacy owner.
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` - remove API type import from component test.
- `frontend/src/pages/**`, `frontend/src/features/**`, `frontend/src/layouts/**`, `frontend/src/app/**` - repoint consumers discovered by baseline scan.

Likely tests:

- `frontend/src/tests/B2BReconciliationPanel.test.tsx` - update import and preserve panel assertions.
- `frontend/src/tests/EnterpriseCredentialsPanel.test.tsx` - update import and preserve panel assertions.
- `frontend/src/tests/SupportOpsPanel.test.tsx` - update import and preserve panel assertions.
- `frontend/src/tests/router.test.tsx` - preserve admin guard behavior if touched.
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` - preserve primitive behavior with neutral fixture.
- dashboard, layout, settings and account tests discovered by `rg`.

Files not expected to change:

- `backend/**` - no backend contract or persistence change.
- `frontend/src/api/**` - existing API contracts should be reused, not changed, unless a type-only neutral extraction is explicitly required and covered by tests.
- `frontend/src/styles/design-tokens.css` - no design token change.
- `frontend/src/components/natal-interpretation/**` - natal presentational children stay out of scope except guard validation.
- `frontend/src/features/auth/**` - auth closure from CS-117 stays unchanged.
- `frontend/src/features/natal-chart/**` - natal closure from CS-118 stays unchanged.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- component-architecture component-usage
npm run test -- B2BReconciliationPanel EnterpriseCredentialsPanel SupportOpsPanel UpgradeCTA
npm run test -- router DashboardPage SettingsPage BottomNavPremium
npm run test -- Header Sidebar AppShell
npm run test -- design-system visual-smoke
npm run lint
rg -n "from [\"'](?:@components/)?(?:B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel)[\"']" `
  src -g "*.ts" -g "*.tsx"
rg -n "components/(?:AdminGuard|B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel)" `
  src -g "*.ts" -g "*.tsx"
rg -n "components/settings/DeleteAccountModal|components/dashboard/useDashboardAstroSummary|components/dashboard/DashboardHoroscopeSummaryCardContainer" src -g "*.ts" -g "*.tsx"
rg -n "components/(AdminGuard|B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel)" `
  src/tests/component-architecture-allowlist.ts
rg -n "components/(dashboard/useDashboardAstroSummary|dashboard/DashboardHoroscopeSummaryCardContainer)" `
  src/tests/component-architecture-allowlist.ts
rg -n "components/settings/DeleteAccountModal" src/tests/component-architecture-allowlist.ts
rg -n "import type \\{ UpgradeHint \\} from ['\"]\\.\\.\\/\\.\\.\\/\\.\\.\\/api\\/billing['\"]" src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx
rg -n "apiFetch\\(|fetch\\(|axios|from [\"'](?:@api|@/api|.*\\/api|.*\\/features)" src/components -g "*.ts" -g "*.tsx"
```

All post-migration `rg` commands above must return no hits unless the after
evidence records an exact `needs-user-decision` blocker. If `rg` exits with code
`1` because there are zero matches, record that as PASS.

PERSISTENCE block from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
$s = "_condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners"
python -c "from pathlib import Path; b=Path('$s'); assert (b/'component-api-remaining-before.md').exists()"
python -c "from pathlib import Path; b=Path('$s'); assert (b/'component-api-remaining-after.md').exists()"
python -c "from pathlib import Path; b=Path('$s'); assert (b/'component-api-owner-migration.md').exists()"
python -c "from pathlib import Path; b=Path('$s'); assert (b/'generated/10-final-evidence.md').exists()"
```

Story contract validation before implementation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py `
  --explain-contracts `
  _condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-120-converger-containers-api-restants-components-vers-owners/00-story.md
```

## 22. Regression Risks

- Risk: a moved panel keeps working in tests but an old component import path remains as a facade.
  - Guardrail: `RG-069`, targeted zero-hit scans and no-shim proof in `component-api-owner-migration.md`.
- Risk: layout auth state is accidentally changed while making layout components API-free.
  - Guardrail: layout/router tests plus `RG-068` secondary validation context.
- Risk: allowlist reduction removes an exception before the canonical owner is proven.
  - Guardrail: AC2 and AC3 require per-batch owner proof and `component-architecture`.
- Risk: CS-117, CS-118 or CS-119 legacy surfaces are reintroduced during broad component edits.
  - Guardrail: `RG-073`, `RG-074`, component usage/architecture tests and scans for old paths.
- Risk: a test-only API type import is replaced with a divergent fixture.
  - Guardrail: `UpgradeCTA` behavior tests and explicit neutral contract/fixture evidence.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work for this closure map.
- Keep all new or moved frontend files free of inline styles; use existing CSS files/classes and variables.
- Preserve existing public contracts and route behavior; this is an ownership convergence, not a UX or API change.
- When an owner namespace is absent, create the smallest precise owner for the slice; never create a catch-all feature.

## 24. References

- `_condamad/audits/frontend-components/2026-05-09-0932/00-audit-report.md` - source audit and closure ledger.
- `_condamad/audits/frontend-components/2026-05-09-0932/02-finding-register.md#F-001` - active finding.
- `_condamad/audits/frontend-components/2026-05-09-0932/03-story-candidates.md#SC-001` - finite story candidate and closure map.
- `_condamad/audits/frontend-components/2026-05-09-0932/01-evidence-log.md` - current evidence IDs E-010, E-011, E-015, E-017.
- `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api/00-story.md` - prior component ownership convergence pattern.
- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth/00-story.md` - auth relocation precedent.
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner/00-story.md` - natal feature ownership precedent.
- `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` - deleted test-only component guard precedent.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
- `frontend/src/tests/component-architecture-allowlist.ts` - executable exception register to reduce.
- `frontend/src/tests/component-architecture-guards.test.ts` - executable architecture guard.
