# Story CS-119 supprimer-composants-test-only-sans-ui-runtime: Supprimer les composants test-only sans existence UI runtime

Status: done

## 1. Objective

Supprimer physiquement les composants `frontend/src/components/**` classes
`test-only` par l'audit source, avec leurs CSS/support files orphelins et les
tests qui ne validaient que ces composants. Les tests transverses qui couvrent
aussi le design-system, les guards ou des invariants runtime doivent etre
adaptes sans importer les surfaces supprimees.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-09-0031/05-executive-summary.md`
- Reason for change: l'audit demande de decider si les surfaces B2B, ops,
  privacy, daily et prediction `test-only` doivent etre restaurees au runtime
  ou supprimees. La decision utilisateur est de supprimer les composants
  utilises uniquement par les tests et absents de l'UI runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Inventaire frais et exhaustif de `frontend/src/components/**` avant deletion.
  - Suppression des fichiers composants confirmes `test-only` sans runtime par
    l'inventaire frais; la liste d'audit est un minimum, pas une limite.
  - Suppression des CSS dedies devenus orphelins.
  - Mise a jour des allowlists `component-usage` et `component-architecture`
    pour retirer les exceptions des surfaces supprimees.
  - Suppression des tests qui ne servent qu'a tester les composants supprimes.
  - Adaptation des tests transverses qui importent ou lisent les composants/CSS supprimes mais protègent aussi d'autres invariants.
  - Remplacement local du type interne `MiniInsightCardType` dans
    `frontend/src/hooks/useDailyInsights.ts` si le hook reste conserve.
- Out of scope:
  - Suppression des composants classes `used` ou `public-library-export`.
  - Reattachement de surfaces B2B, ops, privacy, daily ou prediction a des routes runtime.
  - Refactor feature/page hors du dossier `components`.
  - Changement de contrats backend, API, OpenAPI ou routes frontend.
- Explicit non-goals:
  - Ne pas supprimer les surfaces prouvees `used` par l'audit:
    `AdminGuard`, `B2BReconciliationPanel`, `EnterpriseCredentialsPanel`,
    `SupportOpsPanel`, `DeleteAccountModal`, les layouts, les formulaires auth
    et les surfaces natal.
  - Ne pas supprimer `DashboardCard`, `DashboardIcons`, `Card` ou `FormField`, classes `public-library-export`.
  - Ne pas modifier les invariants `RG-069`, `RG-070`, `RG-071`, `RG-072` autrement que pour retirer les exceptions exactes devenues obsoletes.
  - Ne pas ajouter de route, wrapper, alias, fallback, barrel export, re-export
    ou shim pour conserver les composants supprimes.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: les surfaces visees sont des composants UI sans
  consommateur runtime, conserves uniquement pour des tests ou des guards.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les surfaces sans existence UI runtime peuvent disparaitre.
  - Les routes et ecrans runtime existants ne doivent pas changer.
  - Les guards design-system et component-architecture doivent rester executables apres adaptation.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: l'inventaire frais trouve un import runtime
  non-test, un re-export barrel public, un export public non classe `test-only`,
  ou une preuve externe.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La suppression ne peut viser que des fichiers absents du graphe runtime depuis `frontend/src/main.tsx`. |
| Baseline Snapshot | yes | Un inventaire avant/apres des composants et tests touches est requis pour prouver l'absence d'oubli. |
| Ownership Routing | yes | Les classifications `test-only`, `used` et `public-library-export` determinent delete/keep. |
| Allowlist Exception | yes | Les exceptions `component-usage` et `component-architecture` doivent etre retirees sans wildcard ni residu stale. |
| Contract Shape | no | Aucun contrat API, DTO, payload, OpenAPI ou type public genere n'est modifie; `MiniInsightCardType` doit rester interne. |
| Batch Migration | no | La decision est delete-only, sans migration de consommateurs runtime. |
| Reintroduction Guard | yes | Les surfaces supprimees ne doivent pas revenir comme composant, import, CSS orphelin ou exception stale. |
| Persistent Evidence | yes | L'inventaire de suppression et les preuves avant/apres doivent etre conserves dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/component-usage-guards.test.ts`, qui calcule le graphe d'import runtime depuis `frontend/src/main.tsx`.
  - Scan cible des imports non-test sous `frontend/src` pour chaque composant candidat.
  - Inventaire des barrels `frontend/src/components/**/index.ts?(x)` et de leurs
    re-exports relatifs.
- Secondary evidence:
  - `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md`
  - `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md`
  - `frontend/src/tests/component-usage-allowlist.ts`
  - `frontend/src/tests/component-architecture-allowlist.ts`
- Static scans alone are not sufficient for this story because:
  - Les composants peuvent etre atteints par imports indirects; le graphe runtime et les allowlists doivent confirmer que la surface est seulement test-only avant suppression.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/test-only-component-removal-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/test-only-component-removal-after.md`
- Expected invariant:
  - Tous les composants confirmes `test-only` sans runtime par l'inventaire
    frais sont absents apres implementation, sauf blocker documente.
  - Les composants `used`, `public-library-export`, ou decouverts actifs par
    l'inventaire frais restent presents sauf decision utilisateur explicite.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| UI runtime active | Route/page/feature actuellement reachable depuis `frontend/src/main.tsx` | Test-only component under `frontend/src/components/**` |
| Composant partage public | Export public ou barrel classe `public-library-export` | Suppression dans cette story |
| Surface test-only sans UI runtime | Aucun owner runtime; decision utilisateur `delete` | Wrapper, alias, fallback, re-export ou exception allowlist |
| Guard transversal | `frontend/src/tests/*guards*.test.*` | Import direct d'un composant supprime |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `component-usage-allowlist.ts` | rows `test-only` listees ici | Exceptions obsoletes | Retirer sans remplacement. |
| `component-architecture-allowlist.ts` | B2B, ops, privacy test-only | Containers API sans runtime | Retirer les exceptions supprimees. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, public export, DTO, OpenAPI contract, or
  generated client is affected. The only type work is internal and non-public:
  remove the `MiniInsightCardType` import from a deleted component.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required; this is delete-only removal with test adaptation.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline inventory | `test-only-component-removal-before.md` | Lister composants, CSS, imports et decision initiale. |
| After inventory | `test-only-component-removal-after.md` | Prouver suppressions, tests adaptes et exceptions retirees. |
| Validation log | `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/validation-evidence.md` | Conserver commandes, resultats et limitations eventuelles. |

For audit-sourced stories, include at least one artifact or generated evidence entry that records source finding closure status and any remaining closure map.

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- AST guard `frontend/src/tests/component-usage-guards.test.ts`
- frontend route table / import graph from `frontend/src/main.tsx`
- targeted forbidden symbol scans
- `COMPONENT_USAGE_EXCEPTIONS`
- `COMPONENT_API_IMPORT_EXCEPTIONS`
- `frontend/src/components/**/index.ts`
- `frontend/src/components/**/index.tsx`

Required forbidden examples:

- `components/B2BAstrologyPanel.tsx`
- `components/B2BBillingPanel.tsx`
- `components/B2BEditorialPanel.tsx`
- `components/B2BUsagePanel.tsx`
- `components/OpsMonitoringPanel.tsx`
- `components/OpsPersonaPanel.tsx`
- `components/PrivacyPanel.tsx`
- `components/DailyInsightsSection.tsx`
- `components/MiniInsightCard.tsx`
- `components/ConstellationSVG.tsx`
- `components/HeroHoroscopeCard.tsx`
- `components/TodayHeader.tsx`
- `components/prediction/DayPredictionCard.tsx`
- `components/prediction/TurningPointsList.tsx`
- `components/HeroHoroscopeCard.css`
- `components/MiniInsightCard.css`
- `components/prediction/DayPredictionCard.css`
- `components/prediction/TurningPointsList.css`
- `B2BAstrologyPanel.test.tsx`
- `B2BBillingPanel.test.tsx`
- `B2BEditorialPanel.test.tsx`
- `B2BUsagePanel.test.tsx`
- `OpsMonitoringPanel.test.tsx`
- `OpsPersonaPanel.test.tsx`
- `PrivacyPanel.test.tsx`
- `HeroHoroscopeCard.test.tsx`
- `MiniInsightCard.test.tsx`
- `TodayHeader.test.tsx`
- `TurningPointsEnriched.test.tsx`
- `day-prediction-card-tone.test.ts`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `npm run test -- component-usage component-architecture design-system visual-smoke`
  checks stale exceptions, stale imports, and design guards after deletion.
- Evidence profile: `negative_scan`; targeted `rg` commands listed in the validation plan prove forbidden paths and symbols are absent outside `_condamad` historical artifacts.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-components/2026-05-09-0031/05-executive-summary.md#What-Remains`
- Closure proof required: before/after inventory, stale allowlist cleanup, component-usage and component-architecture guards, targeted negative scans, frontend lint and tests.
- Known residual in-domain work: none after the required fresh exhaustive
  component inventory passes.
- Deferred non-domain concerns: exact API-owning runtime components still
  deferred to feature/page owners as documented by F-001; this story does not
  relocate runtime-used components.

Full closure forbids `PASS with limitation`, broad allowlists, wildcard
exceptions, unclassified fallback, compatibility, legacy, migration-only, shim,
alias, TODO, and hidden residual in-domain work.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md`
  - classification des surfaces `test-only`, `used` et `public-library-export`.
- Evidence 1b: `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md`
  - lignes de scope: l'audit source n'est pas un re-audit exhaustif complet.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md` - E-005 and E-011 document component usage classification and runtime usage evidence.
- Evidence 3: `frontend/src/tests/component-usage-allowlist.ts`
  - exact `test-only` entries for B2B, ops, privacy, daily and prediction.
- Evidence 4: `frontend/src/tests/component-architecture-allowlist.ts`
  - API exceptions include test-only B2B, ops, and privacy containers.
- Evidence 5: `frontend/src/tests/visual-smoke.test.tsx`
  - imports `MiniInsightCard` and reads `HeroHoroscopeCard.css`.
- Evidence 6: `frontend/src/tests/design-system-guards.test.ts`
  - reads CSS/source files for some deleted surfaces and many unrelated guards.
- Evidence 7: `frontend/src/hooks/useDailyInsights.ts`
  - imports `MiniInsightCardType` type-only from a component slated for deletion.
- Evidence 8: `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md`
  - prior story kept these surfaces because product decision was deferred.
- Evidence 9: `_condamad/stories/regression-guardrails.md`
  - invariants consulted: `RG-047`, `RG-048`, `RG-050`, `RG-056`,
    `RG-057`, `RG-069`, `RG-070`, `RG-072`, `RG-074`.

### Pre-Removal Inventory

| Surface | Support | Consumers | Decision |
|---|---|---|---|
| `components/B2BAstrologyPanel.tsx` | none | `B2BAstrologyPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/B2BBillingPanel.tsx` | none | `B2BBillingPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/B2BEditorialPanel.tsx` | none | `B2BEditorialPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/B2BUsagePanel.tsx` | none | `B2BUsagePanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/OpsMonitoringPanel.tsx` | none | `OpsMonitoringPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/OpsPersonaPanel.tsx` | none | `OpsPersonaPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/PrivacyPanel.tsx` | none | `PrivacyPanel.test.tsx`; allowlists | delete component/test; remove allowlists. |
| `components/DailyInsightsSection.tsx` | `MiniInsightCard`; hook | `MiniInsightCard.test.tsx`; design guard | delete; adapt design guard. |
| `components/MiniInsightCard.tsx` | `MiniInsightCard.css` | focused test; visual smoke; type-only hook | delete; adapt hook and smoke. |
| `components/ConstellationSVG.tsx` | none | indirect via `HeroHoroscopeCard` | delete with `HeroHoroscopeCard`. |
| `components/HeroHoroscopeCard.tsx` | `HeroHoroscopeCard.css` | focused test; visual/design guards | delete; adapt guards. |
| `components/TodayHeader.tsx` | none | `TodayHeader.test.tsx`; usage allowlist | delete component/test; remove allowlist. |
| `components/prediction/DayPredictionCard.tsx` | `DayPredictionCard.css` | tone test; design guard | delete; adapt guard. |
| `components/prediction/TurningPointsList.tsx` | `TurningPointsList.css` | `TurningPointsEnriched.test.tsx`; design guard | delete; adapt guard. |

This table is the minimum seed from the audit. If the required fresh inventory
finds another component with zero runtime consumer, no public barrel, and only
test consumers, the implementation must add it to the before/after artifacts
and delete it under the same rules.

## 6. Target State

After implementation:

- `test-only-component-removal-before.md` prouve un inventaire frais de tous les
  composants, barrels, imports runtime, imports test et CSS dedies.
- All components confirmed `test-only` without runtime by the fresh inventory
  are physically absent.
- Their dedicated CSS files are absent when no other runtime file imports them.
- Focused tests that only validate deleted components are deleted.
- Transverse tests no longer import or read deleted files and still validate their unrelated guard responsibilities.
- `COMPONENT_USAGE_EXCEPTIONS` contains no `test-only` entries for deleted files and no stale exception pointing to a missing file.
- `COMPONENT_API_IMPORT_EXCEPTIONS` contains no B2B/ops/privacy exceptions for deleted files.
- Negative scans prove no runtime, test, barrel, type-only, CSS, or guard import
  remains for deleted surfaces outside historical `_condamad` artifacts.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - tests/styles touches must not reintroduce static inline style debt.
  - `RG-048` - CSS files kept after adaptation must not add unclassified token fallbacks.
  - `RG-050` - design-system guards must remain executable after removing CSS files from guarded clusters.
  - `RG-056` - shared component UI literals must not regress when adapting residual CSS guard clusters.
  - `RG-057` - runtime compatibility vocabulary and removed frontend surfaces must not return.
  - `RG-069` - component API import exceptions must remain exact and shrink when test-only API containers are deleted.
  - `RG-070` - component TypeScript suppressions must remain absent.
  - `RG-072` - component usage exceptions must remain exact; no unused component may stay unclassified.
  - `RG-074` - test-only component removals from CS-119 must not be reintroduced as files, imports, CSS or allowlist exceptions.
- Non-applicable invariants:
  - `RG-071` - `NatalInterpretation` is out of scope and must not be changed.
  - `RG-073` - natal feature owner relocation is out of scope and must not be changed.
- Required regression evidence:
  - `npm run test -- component-usage component-architecture design-system visual-smoke`
  - targeted negative scans for deleted paths/symbols
  - `npm run lint`
- Allowed differences:
  - Deleted test-only component files, deleted focused tests, deleted orphan CSS, and removed allowlist rows only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before artifact inventories all current component files. | Evidence: `runtime_source`; `npm run test -- component-usage` plus before artifact. |
| AC2 | All confirmed test-only deletion candidates are physically absent. | Evidence: `negative_scan`; `Test-Path`/`rg --files` checks. |
| AC3 | Focused tests are deleted; transverse tests keep unrelated guard coverage. | Evidence: `test_inventory`; `npm run test -- design-system visual-smoke`. |
| AC4 | Usage/API allowlists contain no stale row or broad replacement. | Evidence: `runtime_source`; AST guard `npm run test -- component-usage component-architecture`. |
| AC5 | No reference to a deleted symbol or module remains outside historical artifacts. | Evidence: `runtime_source,negative_scan`; AST guard plus targeted `rg`. |
| AC6 | Frontend validation remains green. | Evidence profile: `validation_command`; targeted tests plus `npm run lint` from `frontend/`. |
| AC7 | Reintroduction guard fails on forbidden module paths. | Evidence: `reintroduction_guard`; `npm run test -- component-usage`. |
| AC8 | After artifact proves closure with no hidden residual test-only component. | Evidence: `persistent_evidence`; after artifact and `npm run test -- component-usage`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture the exact baseline before editing (AC: AC1)
  - [ ] Subtask 1.1 - Write `test-only-component-removal-before.md` with an
    exhaustive list of `frontend/src/components/**/*.tsx` component files.
  - [ ] Subtask 1.2 - Record runtime graph, test import, barrel re-export and
    CSS import evidence for every target symbol and path under `frontend/src`.
  - [ ] Subtask 1.3 - Mark any newly discovered active or public-barrel surface
    as blocker instead of deleting it.

- [ ] Task 2 - Delete only confirmed test-only component surfaces (AC: AC2)
  - [ ] Subtask 2.1 - Delete the seeded target component files listed in
    `Pre-Removal Inventory`.
  - [ ] Subtask 2.1b - Delete any additional component proven by the fresh
    inventory to be test-only, non-runtime, and non-public-barrel.
  - [ ] Subtask 2.2 - Delete `HeroHoroscopeCard.css`, `MiniInsightCard.css`, `DayPredictionCard.css`, and `TurningPointsList.css` if no non-deleted file imports them.
  - [ ] Subtask 2.3 - Keep all audit-classified `used` and `public-library-export` files intact.

- [ ] Task 3 - Remove or adapt impacted tests (AC: AC3, AC6)
  - [ ] Subtask 3.1 - Delete focused tests dedicated only to removed components:
    B2B panel tests, ops panel tests, `PrivacyPanel.test.tsx`,
    `HeroHoroscopeCard.test.tsx`, `MiniInsightCard.test.tsx`,
    `TodayHeader.test.tsx`, `TurningPointsEnriched.test.tsx`, and the tone test
    unless a non-test runtime helper owner is discovered.
  - [ ] Subtask 3.2 - Adapt `visual-smoke.test.tsx` to remove `MiniInsightCard` and `HeroHoroscopeCard.css` references while preserving the remaining smoke checks.
  - [ ] Subtask 3.3 - Adapt `design-system-guards.test.ts` to remove deleted
    CSS/source files while keeping unrelated design-system invariants.

- [ ] Task 4 - Clean allowlists and type-only dependencies (AC: AC4, AC5)
  - [ ] Subtask 4.1 - Remove all deleted component rows from `COMPONENT_USAGE_EXCEPTIONS`.
  - [ ] Subtask 4.2 - Remove deleted B2B/ops/privacy rows from `COMPONENT_API_IMPORT_EXCEPTIONS`.
  - [ ] Subtask 4.3 - Replace the `MiniInsightCardType` dependency in
    `useDailyInsights.ts` without importing from a deleted component.

- [ ] Task 5 - Harden reintroduction checks and persist closure evidence (AC: AC5, AC7, AC8)
  - [ ] Subtask 5.1 - Update or add deterministic guard logic so stale missing
    allowlist rows, reintroduced component paths and barrel re-exports are caught.
  - [ ] Subtask 5.2 - Write `test-only-component-removal-after.md` and `validation-evidence.md` with command results and remaining risks.
  - [ ] Subtask 5.3 - Confirm no `PASS with limitation` or hidden residual `test-only` component remains for the listed scope.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/tests/component-usage-guards.test.ts` for runtime reachability and stale unused component detection.
  - `frontend/src/tests/component-architecture-guards.test.ts` for component API import exception validation.
  - `frontend/src/tests/design-system-policy.ts` helpers for test-side file inventory and CSS reads.
- Do not recreate:
  - replacement UI components for deleted surfaces;
  - new barrels or re-exports for deleted files;
  - duplicated usage scanners when the existing guard helpers can be extended.
- Shared abstraction allowed only if:
  - an existing test guard cannot express the forbidden path check, and the new helper is used by at least one deterministic guard in this story.

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

- `B2BAstrologyPanel`, `B2BBillingPanel`, `B2BEditorialPanel`, `B2BUsagePanel`
- `OpsMonitoringPanel`, `OpsPersonaPanel`, `PrivacyPanel`
- `DailyInsightsSection`, `MiniInsightCard`, `ConstellationSVG`, `HeroHoroscopeCard`, `TodayHeader`
- `DayPredictionCard`, `getDayPredictionToneClassKey`, `TurningPointsList`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/components/MiniInsightCard.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/TurningPointsList.css`

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

For this story, `test-only` from `COMPONENT_USAGE_EXCEPTIONS` plus zero
non-test runtime import maps to `dead` after user deletion decision. Any
non-test runtime import changes the item to `canonical-active` and blocks
deletion.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed `Decision` values in the audit are exactly:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/test-only-component-removal-before.md`
- `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/test-only-component-removal-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Enterprise runtime reconciliation | `frontend/src/pages/admin/ReconciliationAdmin.tsx` plus currently used enterprise components | Test-only B2B panels listed for deletion. |
| Admin operations runtime | Existing runtime pages/components importing `SupportOpsPanel` | Test-only ops panels listed for deletion. |
| Settings privacy runtime | Existing settings page and `DeleteAccountModal` | Test-only `PrivacyPanel`. |
| Daily/dashboard runtime | Current route-reachable pages and cards | Test-only daily/dashboard components listed for deletion. |
| Prediction runtime | Current prediction pages/features reachable from routes | Test-only prediction components listed for deletion. |

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

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

For this story, known external generated contracts are not expected for local UI
components. If a public package export, docs link, generated design manifest, or
route deep link references a target component, classify that item as
`needs-user-decision` and do not delete it silently.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

Required generated-contract evidence:

- `npm run lint` proves TypeScript import/type graph integrity after deletion.
- `npm run test -- component-usage component-architecture` proves frontend component registries and guards remain coherent.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/05-executive-summary.md`
- `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md`
- `frontend/src/tests/component-usage-allowlist.ts`
- `frontend/src/tests/component-usage-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/hooks/useDailyInsights.ts`
- `frontend/src/components/**/index.ts`
- `frontend/src/components/**/index.tsx`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/components/B2BAstrologyPanel.tsx` - delete.
- `frontend/src/components/B2BBillingPanel.tsx` - delete.
- `frontend/src/components/B2BEditorialPanel.tsx` - delete.
- `frontend/src/components/B2BUsagePanel.tsx` - delete.
- `frontend/src/components/OpsMonitoringPanel.tsx` - delete.
- `frontend/src/components/OpsPersonaPanel.tsx` - delete.
- `frontend/src/components/PrivacyPanel.tsx` - delete.
- `frontend/src/components/DailyInsightsSection.tsx` - delete.
- `frontend/src/components/MiniInsightCard.tsx` - delete.
- `frontend/src/components/MiniInsightCard.css` - delete if orphan.
- `frontend/src/components/ConstellationSVG.tsx` - delete.
- `frontend/src/components/HeroHoroscopeCard.tsx` - delete.
- `frontend/src/components/HeroHoroscopeCard.css` - delete if orphan.
- `frontend/src/components/TodayHeader.tsx` - delete.
- `frontend/src/components/prediction/DayPredictionCard.tsx` - delete.
- `frontend/src/components/prediction/DayPredictionCard.css` - delete if orphan.
- `frontend/src/components/prediction/TurningPointsList.tsx` - delete.
- `frontend/src/components/prediction/TurningPointsList.css` - delete if orphan.
- `frontend/src/hooks/useDailyInsights.ts` - remove type-only dependency on deleted component if the hook remains.
- `frontend/src/tests/component-usage-allowlist.ts` - remove deleted `test-only` rows.
- `frontend/src/tests/component-architecture-allowlist.ts` - remove deleted B2B/ops/privacy API exceptions.
- `frontend/src/tests/component-usage-guards.test.ts` - update guard expectations for deleted type-only import and optionally add forbidden path checks.
- `frontend/src/tests/design-system-guards.test.ts` - remove deleted CSS/source files from guard lists and targeted checks while preserving unrelated guards.
- `frontend/src/tests/visual-smoke.test.tsx` - remove deleted component/CSS references while preserving other visual smoke coverage.

Likely tests:

- `frontend/src/tests/B2BAstrologyPanel.test.tsx` - delete.
- `frontend/src/tests/B2BBillingPanel.test.tsx` - delete.
- `frontend/src/tests/B2BEditorialPanel.test.tsx` - delete.
- `frontend/src/tests/B2BUsagePanel.test.tsx` - delete.
- `frontend/src/tests/OpsMonitoringPanel.test.tsx` - delete.
- `frontend/src/tests/OpsPersonaPanel.test.tsx` - delete.
- `frontend/src/tests/PrivacyPanel.test.tsx` - delete.
- `frontend/src/tests/HeroHoroscopeCard.test.tsx` - delete.
- `frontend/src/tests/MiniInsightCard.test.tsx` - delete.
- `frontend/src/tests/TodayHeader.test.tsx` - delete.
- `frontend/src/tests/TurningPointsEnriched.test.tsx` - delete unless its assertions are moved to a runtime-owned prediction presenter discovered before implementation.
- `frontend/src/tests/day-prediction-card-tone.test.ts` - delete unless `getDayPredictionToneClassKey` is moved to an existing runtime-owned utility with a non-test consumer.

Files not expected to change:

- `frontend/src/components/B2BReconciliationPanel.tsx` - classified `used` by runtime import evidence.
- `frontend/src/components/EnterpriseCredentialsPanel.tsx` - classified `used`.
- `frontend/src/components/SupportOpsPanel.tsx` - classified `used`.
- `frontend/src/components/settings/DeleteAccountModal.tsx` - classified `used`.
- `frontend/src/components/dashboard/DashboardCard.tsx` - classified `public-library-export`.
- `frontend/src/components/icons/DashboardIcons.tsx` - classified `public-library-export`.
- `frontend/src/components/ui/Card/Card.tsx` - classified `public-library-export`.
- `frontend/src/components/ui/Form/FormField.tsx` - classified `public-library-export`.
- `frontend/src/features/natal-chart/**` - natal feature owner is outside this deletion.
- `backend/**` - no backend scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- component-usage component-architecture design-system visual-smoke
npm run lint
rg -n "B2BAstrologyPanel|B2BBillingPanel|B2BEditorialPanel" src `
  -g "*.ts" -g "*.tsx" -g "*.css"
rg -n "B2BUsagePanel|OpsMonitoringPanel|OpsPersonaPanel|PrivacyPanel" src `
  -g "*.ts" -g "*.tsx" -g "*.css"
rg -n "DailyInsightsSection|MiniInsightCard|ConstellationSVG|HeroHoroscopeCard|TodayHeader" src `
  -g "*.ts" -g "*.tsx" -g "*.css"
rg -n "DayPredictionCard|getDayPredictionToneClassKey|TurningPointsList" src `
  -g "*.ts" -g "*.tsx" -g "*.css"
rg -n "components/(B2BAstrologyPanel|B2BBillingPanel|B2BEditorialPanel|B2BUsagePanel)" src `
  -g "*.ts" -g "*.tsx"
rg -n "components/(OpsMonitoringPanel|OpsPersonaPanel|PrivacyPanel|DailyInsightsSection)" src `
  -g "*.ts" -g "*.tsx"
rg -n "components/(MiniInsightCard|ConstellationSVG|HeroHoroscopeCard|TodayHeader)" src `
  -g "*.ts" -g "*.tsx"
rg -n "components/prediction/(DayPredictionCard|TurningPointsList)" src `
  -g "*.ts" -g "*.tsx"
rg -n "(B2BAstrologyPanel|B2BBillingPanel|B2BEditorialPanel|B2BUsagePanel)" src/components `
  -g "index.ts" -g "index.tsx"
rg -n "(OpsMonitoringPanel|OpsPersonaPanel|PrivacyPanel|DailyInsightsSection)" src/components `
  -g "index.ts" -g "index.tsx"
rg -n "(MiniInsightCard|ConstellationSVG|HeroHoroscopeCard|TodayHeader)" src/components `
  -g "index.ts" -g "index.tsx"
rg -n "(DayPredictionCard|TurningPointsList)" src/components/prediction `
  -g "index.ts" -g "index.tsx"
```

Story validation commands, from repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py `
  --explain-contracts `
  _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md
```

## 22. Regression Risks

- Risk: suppression accidentelle d'un composant encore route-reachable.
  - Guardrail: `RG-072`; baseline runtime graph, targeted import scans, and keep-list for `used` / `public-library-export` files.
- Risk: tests transverses affaiblis au lieu d'etre adaptes.
  - Guardrail: `RG-050`; `design-system` and `visual-smoke` must still run and their unrelated assertions must remain.
- Risk: allowlist stale masquant une regression.
  - Guardrail: `RG-069` and `RG-072`; remove exact rows and run guards.
- Risk: reintroduction ulterieure des composants supprimes sous forme d'alias ou de re-export.
  - Guardrail: `RG-074`; forbidden path/symbol scans and component usage guard update.

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
  TODO, or hidden residual work when this story is marked `full-closure`.
- Before deleting each file, prove it has no non-test runtime consumer. If the proof contradicts this story, keep the file and record a blocker instead of deleting.
- All Python validation commands for this story must be run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-components/2026-05-09-0031/05-executive-summary.md` - source decision point.
- `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md` - audited classification table and limitations.
- `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md` - command evidence for usage and runtime classifications.
- `_condamad/audits/frontend-components/2026-05-09-0031/02-finding-register.md`
  - F-004 classifies the residual test-only surfaces.
- `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md` - prior keep/delete decision ledger.
- `_condamad/stories/regression-guardrails.md` - applicable no-regression invariants.
