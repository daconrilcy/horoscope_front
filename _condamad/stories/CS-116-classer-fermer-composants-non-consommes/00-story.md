# Story CS-116 classer-fermer-composants-non-consommes: Verifier et fermer les composants frontend non consommes

Status: done

## 1. Objective

Verifier chaque composant liste par `F-005` avec une lecture symbol/export-aware,
puis classer chaque fichier comme runtime-used, public-library-export,
test-only, remove ou needs-user-decision. Les fichiers `remove` sont supprimes
avec imports, barrels, CSS et tests associes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-004`
- Reason for change: plusieurs composants semblent non consommes ou seulement barrel-exported, creant un risque de dead code et de surface legacy.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/components`
- In scope:
  - Les fichiers application listes par `F-005`, `FormField.tsx` et `DashboardIcons.tsx`.
  - Inventaire symbol/export-aware avant/apres.
  - Suppression des fichiers classes `remove`.
  - Guard usage empechant les nouveaux composants non classes.
- Out of scope:
  - Decisions produit de navigation ou restauration de panneaux caches.
  - Refonte API/feature ownership, couverte par `CS-113`.
  - Bundle-size/performance, differe au domaine `frontend-performance`.
- Explicit non-goals:
  - Ne pas supprimer un fichier `external-active` ou ambigu sans decision utilisateur.
  - Ne pas conserver un fichier via re-export legacy ou barrel stale.
  - Ne pas modifier les invariants `RG-050`, `RG-056`, `RG-068`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story identifie et supprime les fichiers morts apres classification deterministe.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les composants runtime-used ou public-library-export ne doivent pas changer de comportement.
  - Les seules suppressions autorisees concernent les fichiers classes `dead` avec preuve zero consumer.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un panel non consomme peut etre temporairement cache, destine a une navigation future, ou expose comme primitive publique sans preuve runtime.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | le guard AST/import-aware devient source de verite de l'usage composant. |
| Baseline Snapshot | yes | inventaire usage before/after obligatoire. |
| Ownership Routing | yes | chaque fichier conserve doit avoir owner et classification. |
| Allowlist Exception | yes | les fichiers unused-looking conserves doivent etre exacts et motives. |
| Contract Shape | no | aucun contrat API ou schema genere n'est affecte. |
| Batch Migration | no | la surface est la liste finie F-005. |
| Reintroduction Guard | yes | un guard doit echouer pour les fichiers non consommes non classes. |
| Persistent Evidence | yes | classification, before/after et suppressions doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard/import-aware component usage guard in `frontend/src/tests/component-usage-guards.test.ts`, executed by `npm run test -- component-usage`.
- Secondary evidence:
  - symbol/export-aware inventory and targeted `rg --files frontend/src/components -g '*.tsx'` scan.
- Static scans alone are not sufficient for this story because:
  - the guard must classify named exports, barrel-only exports and retained exceptions deterministically.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-after.md`
- Expected invariant:
  - zero fichier composant unclassified unused/barrel-only reste dans l'inventaire.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime-used component | current runtime/page/feature consumer | unused shared component |
| Public UI primitive/export | `frontend/src/components/ui/**` or documented public component owner | stale barrel only |
| Dead component | removed file and stale imports/barrels/tests removed | soft-disabled retained file |
| Needs decision | exact classification artifact with risk | wildcard allowlist |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `component-usage-allowlist.ts` | retained exact entries | public export or hidden file | owner, rationale, exit and command |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before usage inventory | `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-before.md` | prove starting F-005 surface |
| after usage inventory | `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-after.md` | prove no unclassified unused files remain |
| classification table | `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md` | record each file decision, proof and risk |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- component files with zero runtime reference and no exact classification
- barrel-only exports without public-library classification
- retained unused files without owner and exit condition
- Deterministic source: forbidden symbols scan plus AST guard.
- Deterministic source: AST guard in `frontend/src/tests/component-usage-guards.test.ts`.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- component-usage components` checks the inventory and allowlist.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-005`
- Closure proof required: symbol/export-aware before/after inventory, classification table, remove/retain diff, passing usage guard.
- Known residual in-domain work: none
- Deferred non-domain concerns: bundle-size warnings belong to `frontend-performance`; route/page ownership belongs to `frontend-react-pages`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-components/2026-05-08-2303/06-component-usage-inventory.md` - static inventory lists no-runtime-reference and barrel-only candidates.
- Evidence 2: `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md` - `F-005` describes the legacy/dead-code risk.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

- Every `F-005` file is runtime-used, public-library-export, test-only, removed or exact `needs-user-decision`.
- Files classified `remove` are physically deleted, not soft-disabled or preserved through barrels.
- Usage guard fails on new unclassified unused component files.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - guard suites and allowlists must remain exact.
  - `RG-056` - shared UI component literals/guards must not regress while classifying primitives.
  - `RG-068` - layout/page ownership must not be used as an implicit excuse for hidden unused files.
- Non-applicable invariants:
  - `RG-047`, `RG-048` - no inline style or CSS fallback migration is required unless stale CSS is removed with a component.
- Required regression evidence:
  - `npm run test -- components component-usage design-system`
  - `npm run lint`
  - symbol/export-aware usage inventory.
- Allowed differences:
  - Deleted files and associated stale imports/barrels/tests for items classified `dead`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | A fresh symbol/export-aware inventory covers all F-005 files. | Evidence profile: `baseline_before_after_diff`; `rg --files frontend/src/components -g '*.tsx'`. |
| AC2 | Each file has an allowed classification. | Evidence profile: `ast_architecture_guard`; `component-usage-classification.md` and `npm run test -- component-usage`. |
| AC3 | `remove` files are physically deleted. | Evidence profile: `repo_wide_negative_scan`; `rg -n 'deleted-symbol-or-path' frontend/src`. |
| AC4 | Retained unused-looking files have exact owner metadata. | Evidence profile: `allowlist_register_validated`; `npm run test -- component-usage`. |
| AC5 | New unclassified files with no runtime reference fail the guard. | Evidence profile: `reintroduction_guard`; AST guard via `npm run test -- component-usage`. |
| AC6 | Frontend regression suite passes. | Evidence profile: `ast_architecture_guard`; `npm run test -- components component-usage design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Re-run import-aware inventory (AC: AC1)
  - [ ] Include named exports, barrels, dynamic imports, tests exclusion and self-file exclusion.
- [ ] Task 2 - Classify every candidate (AC: AC2, AC4)
  - [ ] Resolve `DashboardIcons.tsx` by named exports, including `SettingsIcon` collision.
  - [ ] Resolve `FormField.tsx` as public-library-export or remove candidate.
- [ ] Task 3 - Delete removable files only (AC: AC3)
  - [ ] Remove files classified `dead` and all stale imports/barrels/CSS/tests.
  - [ ] Stop on external-active or needs-user-decision.
- [ ] Task 4 - Add usage guard and exact allowlist (AC: AC4, AC5)
  - [ ] Add/update component usage allowlist and guard test.
- [ ] Task 5 - Persist after evidence and validate (AC: AC1, AC6)
  - [ ] Write after inventory/classification and run tests/lint/scans.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - audit inventory command from `06-component-usage-inventory.md`, adapted to be symbol/export-aware.
  - existing frontend test utilities and guard patterns.
- Do not recreate:
  - a second usage allowlist if an existing component architecture allowlist can be extended cleanly.
  - duplicate public primitives under new names.
- Shared abstraction allowed only if:
  - guard logic is reused by multiple component architecture tests.

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

- stale barrel exports for deleted files
- soft-disabled component files retained after `remove`
- wildcard entries in `component-usage-allowlist.ts`
- `PASS with limitation` for full-closure F-005

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, clients, analytics, or explicit audit evidence.
- `historical-facade`: item exists only to preserve an older import/export surface.
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

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| each file | component file | classify during implementation | consumers | owner or none | keep/delete/replace-consumer/needs-user-decision | command evidence | risk |

Audit output path when applicable:

- `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| B2B/admin/ops panels retained for runtime | admin/enterprise/ops owner with consumer proof | unused root component files |
| Prediction display components | prediction feature/page owner with consumer proof | unmounted shared components |
| UI form primitives | `frontend/src/components/ui/Form/**` public export if proven | barrel-only stale export |
| Dashboard icons | icon library owner if named exports are consumed | same-name local collision false positive |

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

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-components/2026-05-08-2303/06-component-usage-inventory.md`
- `frontend/src/components/B2BAstrologyPanel.tsx`
- `frontend/src/components/B2BBillingPanel.tsx`
- `frontend/src/components/B2BEditorialPanel.tsx`
- `frontend/src/components/B2BUsagePanel.tsx`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/components/HeroHoroscopeCard.tsx`
- `frontend/src/components/OpsMonitoringPanel.tsx`
- `frontend/src/components/OpsPersonaPanel.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCardContainer.tsx`
- `frontend/src/components/prediction/DecisionWindowsSection.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/components/PrivacyPanel.tsx`
- `frontend/src/components/TodayHeader.tsx`
- `frontend/src/components/ui/Form/FormField.tsx`
- `frontend/src/components/icons/DashboardIcons.tsx`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/component-usage-allowlist.ts` - exact retained unused-looking files.
- `frontend/src/tests/component-usage-guards.test.ts` - import-aware usage guard.
- files listed in `F-005` - delete or update only after classification.
- relevant barrel files such as `frontend/src/components/icons/index.ts` and `frontend/src/components/ui/Form/index.ts` - remove stale exports required by classification.

Likely tests:

- `frontend/src/tests/component-usage-guards.test.ts` - usage guard.
- impacted component tests if a classified deletion removes stale tests/imports.

Files not expected to change:

- `backend/app/**` - no backend/API change.
- `frontend/src/pages/**` except import updates caused by proven component deletion or classification.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- components component-usage design-system
npm run lint
rg --files src/components -g '*.tsx'
```

## 22. Regression Risks

- Risk: static inventory misses named export consumers and deletes a used symbol.
  - Guardrail: symbol/export-aware scan and classification proof per file.
- Risk: stale barrel exports preserve deleted surfaces.
  - Guardrail: delete-only rule and negative barrel/import scans.

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
  TODO, or hidden residual in-domain work because this story is `full-closure`.

## 24. References

- `_condamad/audits/frontend-components/2026-05-08-2303/02-finding-register.md#F-005` - source finding.
- `_condamad/audits/frontend-components/2026-05-08-2303/03-story-candidates.md#SC-004` - story candidate contract.
- `_condamad/audits/frontend-components/2026-05-08-2303/06-component-usage-inventory.md` - source inventory.
- `_condamad/stories/regression-guardrails.md` - regression invariants.
