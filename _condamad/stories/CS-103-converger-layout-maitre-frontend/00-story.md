# Story CS-103 converger-layout-maitre-frontend: Converger le layout maitre frontend

Status: ready-to-dev

## 1. Objective

Monter `RootLayout` comme layout maitre route-level.
Faire cesser la duplication shell/background dans les layouts principaux.
Preserver les routes protegees, admin et application.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-001`
- Reason for change: `F-001` indique que `RootLayout` existe mais n'est pas monte, tandis que `AppLayout` recree le shell et le background.

## 3. Domain Boundary

- Domain: `frontend-layouts`
- In scope:
  - Monter `frontend/src/layouts/RootLayout.tsx` dans `frontend/src/app/routes.tsx`.
  - Faire dependre la branche application/admin de ce layout maitre.
  - Retirer ou rendre impossible la duplication active de `.app-shell`, `.app-bg`, `StarfieldBackground` et `.app-bg-container` dans `AppLayout`.
  - Ajouter ou etendre un guard de hierarchie layout cible.
- Out of scope:
  - Rattacher `/login` et `/register`; story `CS-105`.
  - Monter la landing via `LandingLayout`; story `CS-104`.
  - Classer tous les fichiers `pages/**/*.tsx`; story `CS-107`.
  - Modifier les tokens CSS, le design system, ou les contrats API.
- Explicit non-goals:
  - Ne pas creer un second master layout.
  - Ne pas ajouter un wrapper de compatibilite autour de `AppLayout`.
  - Ne pas affaiblir `RG-064`, `RG-065`, `RG-066` ou `RG-067`.
  - Ne pas changer les redirects, roles ou permissions applicatives.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit l'architecture de layout en rendant le master layout executable et garde.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: changement de structure de route interne pour ajouter `RootLayout`.
  - Interdit: changement des URLs, roles, redirects, composants de page rendus et navigation visible hors effets directs du layout maitre.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: monter `RootLayout` impose un changement visuel public non equivalent ou casse un comportement d'authentification existant.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La route table frontend et un guard executable doivent prouver le layout maitre monte. |
| Baseline Snapshot | yes | La structure before/after des routes et owners de layout doit etre capturee. |
| Ownership Routing | yes | La responsabilite master shell/background doit appartenir a `RootLayout`. |
| Allowlist Exception | yes | Toute exception de route sans layout doit etre exacte et provisoire. |
| Contract Shape | no | Aucun DTO, payload, schema ou contrat HTTP n'est modifie. |
| Batch Migration | no | Cette story migre un seul axe de responsabilite, pas plusieurs lots independants. |
| Reintroduction Guard | yes | Le retour d'un `RootLayout` non monte ou d'un shell master duplique doit echouer. |
| Persistent Evidence | yes | Les inventaires route/layout before/after doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - runtime artifact: `AST guard` over the `RouteObject[]` route object tree exported by `frontend/src/app/routes.tsx`;
  - `AST guard` dans `frontend/src/tests/page-architecture-guards.test.ts` ou `layout-architecture-guards.test.ts`.
- Secondary evidence:
  - scans cibles sur `RootLayout`, `AppLayout`, `StarfieldBackground`, `.app-shell`, `.app-bg`, `.app-bg-container`.
- Static scans alone are not sufficient because:
  - le fait qu'un import existe ne prouve pas que le layout soit ancetre runtime d'une route.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-103-converger-layout-maitre-frontend/layout-master-before.md`.
- Comparison after implementation: `_condamad/stories/CS-103-converger-layout-maitre-frontend/layout-master-after.md`.
- Required baseline content: route tree, owners de layout, occurences master shell/background, tests existants.
- Expected invariant: `RootLayout` est l'ancetre master de la branche applicative et `AppLayout` ne duplique plus la responsabilite master.
- Allowed differences: nesting route-level requis par `RootLayout` et suppression des wrappers master dupliques.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Master route outlet | `frontend/src/layouts/RootLayout.tsx` | route branch sans `RootLayout` |
| Background applicatif global | `frontend/src/layouts/RootLayout.tsx` | `AppLayout` ou page locale |
| Application shell interne | `frontend/src/layouts/AppLayout.tsx` | `RootLayout` |
| Admin section shell | `frontend/src/layouts/AdminLayout.tsx` via `AdminPage` | master layout ou page enfant |

Rules:
- `RootLayout` ne doit pas absorber `Header`, `Sidebar`, `BottomNav` ou les permissions admin.
- `AppLayout` conserve le shell applicatif secondaire, sans redevenir owner du background global.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `layout-master-after.md` | routes publiques non traitees par cette story | scope phasage audit | expire par `CS-104` et `CS-105` |

Rules:
- No wildcard route exception.
- Toute exception doit nommer le path, owner attendu et story de fermeture.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: une seule responsabilite master layout est convergee.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before layout inventory | `_condamad/stories/CS-103-converger-layout-maitre-frontend/layout-master-before.md` | Capturer l'absence de `RootLayout` monte et les duplications. |
| After layout inventory | `_condamad/stories/CS-103-converger-layout-maitre-frontend/layout-master-after.md` | Prouver le nouvel owner master et les residus exacts. |
| Final evidence | `_condamad/stories/CS-103-converger-layout-maitre-frontend/generated/10-final-evidence.md` | Conserver commandes et resultats. |

## 4i. Reintroduction Guard

- Architecture guard against reintroduction: test qui echoue si `RootLayout` n'est pas present dans la route tree.
- The same guard fails if `AppLayout` redevient owner de `StarfieldBackground` ou des classes master.
- Deterministic source: route tree exportee et source TSX des layouts.
- Required forbidden examples:
  - `RootLayout` importe mais non monte dans `routes.tsx`;
  - `AppLayout` rend `StarfieldBackground`;
  - `AppLayout` rend `.app-shell app-bg` comme wrapper racine master.
- Guard evidence: `npm run test -- page-architecture layout`.

## 4j. Source Finding Closure

- Closure status: phased-with-map
- Source finding: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-001`
- Closure proof required: before/after route layout inventory, guard `RootLayout` mounted, tests App/router/layout.
- Known residual in-domain work: landing route owner `CS-104`; auth routes owner `CS-105`; hierarchy guards completes `CS-106`; page file inventory `CS-107`.
- Deferred non-domain concerns: design-system CSS token debt remains outside this domain.
- Remaining closure map: after this story, only direct public route ownership and inventory guards may remain open.
- Stop condition: `RootLayout` is mounted and guarded while protected application/admin behavior remains stable.

## 5. Current State Evidence

- Evidence 1: `frontend/src/app/routes.tsx` - routes `/`, `/login`, `/register`, and protected app branch are top-level siblings without `RootLayout`.
- Evidence 2: `frontend/src/layouts/RootLayout.tsx` - `RootLayout` renders `.app-shell app-bg`, `StarfieldBackground`, `.app-bg-container`, and `Outlet`.
- Evidence 3: `frontend/src/layouts/AppLayout.tsx` - `AppLayout` also renders `.app-shell app-bg`, `StarfieldBackground`, and `.app-bg-container`.
- Evidence 4: `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-001` - audit classifies this as missing canonical owner.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants `RG-064` to `RG-067` consulted before story scope was finalized.

## 6. Target State

- `RootLayout` is mounted as master route owner for the affected route tree.
- `AppLayout` keeps application navigation only and no longer duplicates the global background wrapper.
- Existing application/admin route behavior is preserved.
- A deterministic guard blocks `RootLayout` from becoming dead/unmounted again.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-064` - page architecture guards must stay green while route layout hierarchy changes.
  - `RG-065` - admin prompts ownership must not move back into pages.
  - `RG-066` - page-size exceptions must not be broadened.
  - `RG-067` - page date/time helper ownership is not part of this layout convergence.
- Non-applicable invariants:
  - `RG-047` - no inline style policy change is expected.
  - `RG-054` - no legacy admin redirect path is reintroduced.
- Required regression evidence:
  - `npm run test -- page-architecture App router layout`
  - `npm run lint`
  - before/after layout inventory.
- Allowed differences:
  - route nesting and removal of duplicated master wrapper only.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `RootLayout` is mounted as master ancestor. | Evidence profile: `runtime_behavior`; runtime evidence `AST guard`; command `npm run test -- page-architecture layout`. |
| AC2 | `AppLayout` no longer owns master background. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -n "StarfieldBackground" src/layouts/AppLayout.tsx`. |
| AC3 | Authenticated app/admin routing behavior remains stable. | Evidence profile: `reintroduction_guard`; test `npm run test -- App router page-architecture`. |
| AC4 | Remaining layout audit gaps are explicitly mapped to CS-104 through CS-107. | Evidence profile: `persistent_evidence`; command `rg -n "CS-104" layout-master-after.md`. |
| AC5 | Frontend lint remains green. | Evidence profile: `reintroduction_guard`; command `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture before route/layout inventory. (AC: AC1, AC2, AC4)
- [ ] Task 2 - Mount `RootLayout` in `frontend/src/app/routes.tsx`. (AC: AC1, AC3)
- [ ] Task 3 - Remove duplicated master shell/background responsibility from `AppLayout`. (AC: AC2, AC3)
- [ ] Task 4 - Add or extend the layout hierarchy guard. (AC: AC1, AC2, AC4)
- [ ] Task 5 - Capture after evidence and run validation. (AC: AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `frontend/src/layouts/RootLayout.tsx` as the only master owner.
- Reuse existing `AuthGuard`, `AdminGuard`, `RoleGuard`, `AppLayout`, `AdminLayout`.
- Do not recreate `StarfieldBackground` ownership in another layout.
- Shared test helpers are allowed only if reused by multiple architecture guards.

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
- unmounted `RootLayout` import.
- duplicate `StarfieldBackground` ownership in `AppLayout`.
- broad route exception allowlist.
- `PASS with limitation`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Master route layout | `frontend/src/layouts/RootLayout.tsx` | top-level app branch without `RootLayout` |
| Global background wrapper | `frontend/src/layouts/RootLayout.tsx` | `AppLayout` duplicate wrapper |
| Application navigation shell | `frontend/src/layouts/AppLayout.tsx` | `RootLayout` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/frontend-layouts/2026-05-08-1405/00-audit-report.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-001`
- `frontend/src/app/routes.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/layouts/AdminLayout.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`

## 19. Expected Files to Modify

Likely files:
- `frontend/src/app/routes.tsx` - mount `RootLayout` as master route owner.
- `frontend/src/layouts/AppLayout.tsx` - remove duplicated master wrapper/background responsibility.
- `frontend/src/tests/page-architecture-guards.test.ts` - add targeted guard or reuse shared scanner.

Likely tests:
- `frontend/src/tests/page-architecture-guards.test.ts` - root layout hierarchy guard.
- `frontend/src/tests/App.test.tsx` - only if route rendering assertions need update.

Files not expected to change:
- `backend/**` - no backend surface.
- `frontend/package.json` - existing scripts should be sufficient.
- `frontend/src/pages/**/*.tsx` - no page content refactor in this story.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- page-architecture App router layout
rg -n "StarfieldBackground|app-shell app-bg|app-bg-container" src/layouts/AppLayout.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-103-converger-layout-maitre-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: route nesting changes redirect behavior.
  - Guardrail: App/router tests and before/after route inventory.
- Risk: removing duplicated wrapper breaks app background or admin spacing.
  - Guardrail: targeted App/visual smoke tests and after inventory.
- Risk: story hides unresolved public route ownership.
  - Guardrail: phased closure map names CS-104 to CS-107.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup or design-system migration.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-layouts/2026-05-08-1405/03-story-candidates.md#SC-001` - source candidate.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/02-finding-register.md#F-001` - source finding.
- `_condamad/audits/frontend-layouts/2026-05-08-1405/01-evidence-log.md` - route and layout evidence.
- `_condamad/stories/regression-guardrails.md` - applicable invariants.
