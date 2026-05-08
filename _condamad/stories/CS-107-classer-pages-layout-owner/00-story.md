# Story CS-107 classer-pages-layout-owner: Classer tous les fichiers pages sous un layout owner

Status: ready-to-dev

## 1. Objective

Rendre chaque fichier `frontend/src/pages/**/*.tsx` auditable par rapport a un owner de layout.
Chaque fichier doit etre route, nested-route, page-adjacent, dead/unmounted candidate,
ou `needs-user-decision`, avec inventaire persistant et guard exact.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-005`
- Reason for change: `F-005` indique que plusieurs fichiers sous `frontend/src/pages/**` ne sont pas route-mounted ni classes.

## 3. Domain Boundary

- Domain: `frontend-layouts`
- In scope:
  - Inventorier `frontend/src/pages/**/*.tsx`.
  - Classer chaque fichier avec owner layout ou statut exact.
  - Router les vraies pages publiques sous un principal layout si la decision produit existe.
  - Relocaliser ou classifier les composants page-adjacent seulement avec owner canonique prouve.
  - Ajouter un guard d'inventaire exact.
- Out of scope:
  - Modifier les permissions admin, billing API, privacy copy ou contenu support.
  - Refaire la decomposition des pages volumineuses couverte par `CS-101`.
  - Changer le design system ou les tokens CSS.
- Explicit non-goals:
  - Ne pas utiliser une allowlist `pages/**`.
  - Ne pas rendre public billing/privacy sans decision si l'audit ne le prouve pas.
  - Ne pas supprimer un fichier `pages/**` classe `external-active` ou ambigu.
  - Ne pas affaiblir `RG-064`, `RG-066` ou `RG-067`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: chaque fichier page doit etre route vers un owner de layout ou une classification canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: ajout d'un routing ou classification exacts pour des pages existantes.
  - Interdit: rendre accessible une page publique sans decision produit ou changer son contenu metier.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: privacy/billing return pages doivent etre exposees publiquement ou rester non routees sans preuve produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La route tree frontend doit etre prouvee par `AST guard` pour les fichiers routes. |
| Baseline Snapshot | yes | L'inventaire before/after des fichiers pages est indispensable. |
| Ownership Routing | yes | Chaque fichier doit avoir owner layout ou classification. |
| Allowlist Exception | yes | Les classifications restantes doivent etre exactes et auditees. |
| Contract Shape | no | Aucun API/DTO/schema n'est modifie. |
| Batch Migration | yes | Plusieurs categories de fichiers pages doivent etre traitees par lots. |
| Reintroduction Guard | yes | Un fichier page non classe ne doit pas revenir. |
| Persistent Evidence | yes | L'inventaire owner doit rester consultable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime artifact: `AST guard` over `frontend/src/app/routes.tsx` route object tree;
  - filesystem inventory from `rg --files frontend/src/pages -g "*.tsx"`.
- Secondary evidence:
  - import scans for page-adjacent components and dead/unmounted candidates.
- Static scans alone are not sufficient because:
  - a file can exist under `pages/**` while its effective route ownership depends on route ancestry.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-before.md`.
- Comparison after implementation: `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`.
- Required baseline content: liste complete `rg --files frontend/src/pages -g "*.tsx"`, route tree, classification initiale, blocker decisions.
- Expected invariant: zero fichier `frontend/src/pages/**/*.tsx` non classe.
- Allowed differences: route/relocation/classification exactes et tests correspondants.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Routed application page | principal/secondary layout route ancestor | unclassified page file |
| Nested routed page | parent layout route ancestor | direct page exception |
| Page-adjacent component | feature/component owner outside `pages/**` or exact classification | permanent anonymous page namespace |
| Dead/unmounted page candidate | persisted inventory and user decision before deletion | silent deletion |
| Public billing/privacy page | product-selected principal layout | direct route without owner |

Rules:
- Classification values: `routed-page`, `nested-routed-page`, `page-adjacent-component`, `dead/unmounted-page-candidate`, `needs-user-decision`.
- Aucun fichier ne peut rester `unknown`.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `page-layout-owner-after.md` | `page-adjacent-component` file | component stored under pages namespace | permanent only with owner or relocation story |
| `page-layout-owner-after.md` | `dead/unmounted-page-candidate` file | zero route/import consumer found | expires with later removal story or user decision |
| `page-layout-owner-after.md` | `needs-user-decision` file | public visibility or owner ambiguous | blocks route/deletion |

Rules:
- No wildcard.
- No folder-wide exception.
- Every row must include owner, route/import proof, decision and expiry/permanence.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | routed/nested pages | existing route layout owners | route inventory only | page-architecture guard | zero unknown routed pages | route tree mismatch |
| B2 | privacy/billing pages | selected principal layout or blocker | `routes.tsx` if decision exists | router/App tests | no direct page route | visibility decision missing |
| B3 | support/admin page-adjacent files | feature owner or exact classification | imports if relocated | component tests if moved | no duplicate wrapper | owner unclear |
| B4 | dead/unmounted candidates | inventory blocker or later removal story | none in this story | guard inventory | no hidden residual | external usage ambiguity |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before page owner inventory | `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-before.md` | Capturer tous les fichiers pages et leur etat initial. |
| After page owner inventory | `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` | Prouver classification finale et blockers. |
| Final evidence | `_condamad/stories/CS-107-classer-pages-layout-owner/generated/10-final-evidence.md` | Conserver commandes, tests et scans. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: test qui compare `frontend/src/pages/**/*.tsx` a l'inventaire/route ownership et echoue sur fichier non classe.
- Deterministic source: filesystem inventory plus route tree and exact registry.
- Required forbidden examples:
  - nouveau fichier `frontend/src/pages/**/*.tsx` absent de classification;
  - fichier classe `needs-user-decision` route sans decision;
  - wildcard `pages/**` exception;
  - direct public route sans principal layout owner.
- Guard evidence: `npm run test -- page-architecture App router BillingSuccessPage`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-005`
- Closure proof required: before/after page owner inventory, exact guard, route/import proof for every file.
- Known residual in-domain work: only entries explicitly marked `needs-user-decision` with blocker and decision owner.
- Deferred non-domain concerns: admin permissions, billing backend, privacy legal copy, design-system debt.
- Remaining closure map: after inventory, any `needs-user-decision` row must be the only remaining in-domain blocker and must include exact decision required.
- Stop condition: zero `unknown` page file and guard fails if any unclassified page file appears.

## 5. Current State Evidence

- Evidence 1: `rg --files frontend/src/pages -g "*.tsx"` - page files include `HomePage`, `PrivacyPolicyPage`, billing return pages, support components and admin panels.
- Evidence 2: `frontend/src/app/routes.tsx` - many pages are route-mounted, but billing/privacy/support/admin panel files are not exhaustively classified.
- Evidence 3: `frontend/src/tests/page-architecture-guards.test.ts` - page guards do not classify every page file owner.
- Evidence 4: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-005` - audit identifies missing canonical owner for page files.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - `RG-064`, `RG-066`, and `RG-067` consulted before scope was finalized.

## 6. Target State

- Every `frontend/src/pages/**/*.tsx` file has exact owner classification.
- True pages are routed under a principal layout or blocked by decision.
- Page-adjacent components are relocated or classified with owner and stop condition.
- Guard prevents unclassified page file growth.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture guards remain canonical and exact.
  - `RG-066` - page-size exceptions are not broadened while inventorying pages.
  - `RG-067` - date/time helper ownership remains outside this classification story.
  - `RG-065` - admin prompts page ownership must not regress if admin files are inspected.
- Non-applicable invariants:
  - `RG-044` - no token namespace migration.
  - `RG-054` - no legacy admin redirects should be touched.
- Required regression evidence:
  - `npm run test -- page-architecture App router BillingSuccessPage`
  - `npm run lint`
  - before/after page owner inventory.
- Allowed differences:
  - exact classification, approved routing, approved relocation only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Before inventory lists every `frontend/src/pages/**/*.tsx` file. | Evidence profile: `baseline_before_after_diff`; command `rg --files frontend/src/pages -g "*.tsx"`. |
| AC2 | After inventory classifies every file. | Evidence profile: `allowlist_register_validated`; command `rg -n "unknown" page-layout-owner-after.md` returns zero. |
| AC3 | True routed pages have layout owner proof. | Evidence profile: `ownership_routing`; runtime evidence `AST guard`; command `npm run test -- page-architecture layout`. |
| AC4 | Privacy/billing pages are routed or blocked by decision. | Evidence profile: `external_usage_blocker`; command `rg -n "PrivacyPolicyPage" page-layout-owner-after.md`. |
| AC5 | Page-adjacent components are relocated or classified. | Evidence profile: `batch_migration_mapping`; command `rg -n "page-adjacent-component" page-layout-owner-after.md`. |
| AC6 | Guard blocks new unclassified page files. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture`. |
| AC7 | Frontend lint remains green. | Evidence profile: `reintroduction_guard`; command `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture full before inventory. (AC: AC1)
- [ ] Task 2 - Classify routed and nested routed pages from `routes.tsx`. (AC: AC2, AC3)
- [ ] Task 3 - Resolve or block privacy/billing public pages. (AC: AC4)
- [ ] Task 4 - Classify or relocate support/admin page-adjacent components. (AC: AC5)
- [ ] Task 5 - Add exact inventory guard. (AC: AC2, AC6)
- [ ] Task 6 - Capture after evidence and run validation. (AC: AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse existing page-architecture guard infrastructure.
- Reuse existing route tree `frontend/src/app/routes.tsx` as primary routing evidence.
- Do not create a second independent registry if `page-architecture-allowlist.ts` can hold exact classification cleanly.
- Do not duplicate support/admin panel code during relocation.

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
- wildcard `frontend/src/pages/**` allowlist.
- unclassified page file.
- routing `needs-user-decision` pages without decision.
- moving files by creating re-export shims under `pages/**`.
- hidden residual `TODO`.

## 11. Removal Classification Rules

Classification must be deterministic:
- `canonical-active`: routed page or canonical component owner.
- `external-active`: referenced by public docs/generated links or known external entrypoint.
- `dead`: zero references in route tree, imports, docs and known external surfaces.
- `needs-user-decision`: public visibility or deletion ambiguity remains after scans.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep`, `move-with-consumers` | Must keep behavior. |
| `external-active` | `keep`, `needs-user-decision` | Must not delete silently. |
| `dead` | `keep-classified`, `needs-user-decision` | Deletion is deferred to a later removal story. |
| `needs-user-decision` | `needs-user-decision` | Must block routing/deletion. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| page file from inventory | TSX file | allowed classification | route/import/docs | layout or new owner | keep/move/block | command/source path | filled for block |

Audit output path when applicable:
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Routed page layout ownership | route tree principal/secondary layout | direct/unclassified page file |
| Page file classification registry | page architecture inventory/allowlist | audit-only memory |
| Page-adjacent support/admin component | feature/component owner or exact classification | anonymous file under `pages/**` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

If privacy, billing return, or dead/unmounted candidates may be public entrypoints, stop and record exact user/product decision before routing or deletion.

Deletion is out of scope for this story. A file classified `dead/unmounted-page-candidate`
must remain present and classified until a dedicated removal story approves deletion.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-005`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/pages/support/SupportTicketForm.tsx`
- `frontend/src/pages/support/SupportCategorySelect.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/tests/page-architecture-guards.test.ts` - add inventory guard.
- `frontend/src/tests/page-architecture-allowlist.ts` - add exact ownership classifications if chosen.
- `frontend/src/app/routes.tsx` - route privacy/billing pages only with explicit decision.
- `frontend/src/pages/**` or `frontend/src/features/**` - relocate page-adjacent files only with exact owner and without shims.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/App.test.tsx` or router tests if public routes are added.
- Relevant component tests only if files are relocated.

Files not expected to change:
- `backend/**` - no backend contract.
- `frontend/src/styles/**` - no design-system migration.
- `frontend/package.json` - no dependency/script change expected.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture App router BillingSuccessPage
rg --files src/pages -g "*.tsx"
rg -n "unknown|unclassified|PASS with limitation" `
  ../_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md src/tests/page-architecture*
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-107-classer-pages-layout-owner/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: public billing/privacy routes are exposed accidentally.
  - Guardrail: AC4 requires decision or blocker.
- Risk: moving page-adjacent components creates compatibility shims.
  - Guardrail: No Legacy forbids re-export shims.
- Risk: guard becomes a broad allowlist.
  - Guardrail: AC2 and AC6 require exact classification and zero unknowns.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not route, delete, or expose public pages without decision evidence.
- Do not delete dead/unmounted candidates in this story; classify them only.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-005` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-005` - source finding.
- `frontend/src/app/routes.tsx` - route ownership evidence.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
