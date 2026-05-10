# Story CS-130 uniformiser-largeur-corps-central-frontend: Uniformiser la largeur du corps central frontend

Status: ready-to-review

## 1. Objective

Uniformiser la largeur utile du corps central des pages non-admin depuis le
layout global. La largeur doit maximiser l'espace disponible tout en gardant des
gouttieres laterales compatibles avec le menu lateral. Les pages applicatives
doivent heriter d'une meme enveloppe au lieu de redefinir localement des largeurs
concurrentes.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-10
- Reason for change: les pages de l'application presentent des largeurs
  centrales differentes, ce qui degrade la continuite de navigation. Le layout
  global doit devenir l'owner de cette largeur, les layouts/pages non-admin
  doivent en dependre, et les pages admin doivent conserver leurs propres
  largeurs.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-layouts`
- In scope:
  - Definir dans les tokens/layouts frontend une largeur centrale non-admin canonique et maximisee.
  - Faire porter cette largeur par l'enveloppe racine ou le shell applicatif (`RootLayout`, `AppLayout`, `PageLayout`, CSS associe).
  - Retirer ou remplacer les largeurs de conteneur concurrentes des pages non-admin qui contredisent le layout global.
  - Preserver des largeurs internes locales justifiees pour les textes, cartes, formulaires, side panels ou sous-composants.
  - Ajouter ou etendre un guard de layout/design-system qui bloque les nouvelles largeurs de page non-admin non classees.
  - Produire des artefacts before/after listant les largeurs de conteneur page-level avant et apres convergence.
- Out of scope:
  - Modifier les largeurs admin gerees par `AdminLayout`, `--layout-admin-max-width` ou les CSS sous `frontend/src/pages/admin/**`.
  - Refaire la navigation, les routes, les permissions, le header, la sidebar ou le bottom nav.
  - Modifier les contrats API, le backend, les textes i18n ou les contenus metier.
  - Refaire les pages landing en dehors de l'alignement necessaire sur une largeur globale non-admin.
  - Changer la densite ou la composition metier des composants internes.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047`, `RG-048`, `RG-059`, `RG-064`, `RG-068`, `RG-078` ou `RG-080`.
  - Ne pas migrer les largeurs admin vers la largeur non-admin.
  - Ne pas ajouter de styles inline pour compenser la convergence.
  - Ne pas creer plusieurs tokens concurrents de largeur page-level sans classification exacte.
  - Ne pas masquer un overflow horizontal avec `overflow-x: hidden` au lieu de corriger la largeur.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story deplace l'ownership des largeurs de corps page-level depuis des CSS de pages vers le layout frontend canonique et ses tokens.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: augmentation de la largeur utile non-admin, harmonisation des gouttieres et retrait des overrides page-level contradictoires.
  - Interdit: changement des routes, roles, donnees affichees, logique metier, largeur admin ou navigation visible hors effet direct de largeur.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une page non-admin requiert durablement une largeur
  page-level differente de la largeur globale pour une raison produit ou
  ergonomique non couverte par une largeur interne locale.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le DOM/CSS runtime doit prouver quelle enveloppe porte la largeur centrale effective. |
| Baseline Snapshot | yes | Les largeurs concurrentes actuelles doivent etre inventoriees avant/apres. |
| Ownership Routing | yes | La responsabilite page-level doit appartenir aux layouts, pas aux pages non-admin. |
| Allowlist Exception | yes | Toute exception durable de largeur non-admin doit etre exacte, sourcee et expiree ou permanente. |
| Contract Shape | no | Aucun DTO, payload, route HTTP, schema ou contrat de serialization n'est modifie. |
| Batch Migration | yes | Plusieurs surfaces CSS non-admin doivent converger vers le meme owner de largeur. |
| Reintroduction Guard | yes | Les largeurs page-level concurrentes doivent etre bloquees apres convergence. |
| Persistent Evidence | yes | Les inventaires before/after et la preuve finale doivent etre conserves. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AST guard` dans `frontend/src/tests/page-architecture-guards.test.ts` sur la route tree exportee par `frontend/src/app/routes.tsx`.
  - `AST guard` ou parser CSS dans `frontend/src/tests/design-system-guards.test.ts` sur les declarations CSS actives de largeur.
  - CSS actif charge par `frontend/src/App.css`, `frontend/src/styles/backgrounds.css`,
    `frontend/src/styles/app/layout.css`, `frontend/src/layouts/PageLayout.css`
    et `frontend/src/styles/design-tokens.css`.
  - DOM rendu des routes tests sous `RootLayout` et `AppLayout` avec `.app-bg-container`, `.app-shell-main` et `.page-layout`.
- Secondary evidence:
  - guards Vitest dans `frontend/src/tests/page-architecture-guards.test.ts` ou `frontend/src/tests/design-system-guards.test.ts`.
  - scans cibles des declarations `max-width`, `width`, `margin: 0 auto`, `!important` et `:has(.is-*)` sur les pages non-admin.
- Static scans alone are not sufficient because:
  - une declaration CSS peut etre surchargee par cascade; au moins une verification DOM/CSS ou un test de guard doit confirmer l'owner effectif.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-before.md`.
- Comparison after implementation: `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-after.md`.
- Required baseline content:
  - valeurs des tokens `--layout-page-max-width`, `--layout-admin-max-width`, `--layout-sidebar-width` et tout nouveau token de largeur centrale;
  - declarations page-level non-admin qui fixent `max-width`, `width`, ou contournent `PageLayout`/`.app-bg-container`;
  - exceptions admin explicitement exclues;
  - routes ou pages qui gardent une largeur interne justifiee.
- Expected invariant:
  - une seule largeur centrale page-level non-admin gouverne l'enveloppe principale; les pages non-admin n'ont plus d'overrides contradictoires.
- Allowed differences:
  - augmentation de la largeur centrale non-admin;
  - maintien de largeurs internes locales pour blocs de lecture, cartes, formulaires ou colonnes;
  - maintien des largeurs admin existantes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Largeur centrale non-admin | layout tokens/CSS canonique | CSS de page non-admin avec `max-width` page-level concurrent |
| Gouttieres du shell applicatif | `frontend/src/styles/app/layout.css` et tokens layout | overrides locaux avec padding/marge globale par page |
| Largeur admin | `frontend/src/layouts/AdminLayout.css` et tokens admin | largeur non-admin ou `PageLayout` |
| Largeur interne de lecture/composant | CSS owner du composant ou de la page | layout global si la largeur ne concerne pas le corps central |
| Exceptions | registre/guard frontend exact | commentaire libre, wildcard ou `!important` non justifie |

Rules:

- Les pages non-admin doivent consommer `PageLayout` ou une enveloppe rattachee au layout principal quand elles ont un corps central.
- Les classes page-level non-admin ne doivent pas redefinir une largeur de corps central si le layout global peut la porter.
- Les largeurs internes restent autorisees uniquement lorsqu'elles ciblent un sous-bloc nomme, pas l'enveloppe page.
- Les pages admin gardent leur chemin actuel via `AdminLayout`.

## 4e. Allowlist / Exception Register

Use a deterministic guard/register in `frontend/src/tests/design-system-allowlist.ts`,
`frontend/src/tests/page-architecture-allowlist.ts`, or a focused helper under
`frontend/src/tests/layout-width-guards.test.ts` when neither existing register
is the correct owner.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/layouts/AdminLayout.css` | `--layout-admin-max-width` | Owner canonique admin. | Permanent. |
| `frontend/src/pages/admin/AdminPromptsPage.css` | admin prompt local max widths | Page admin exclue; garde son owner admin. | Permanent until explicit admin layout story. |
| `frontend/src/pages/admin/AdminContentPage.css` | admin content local max widths | Page admin exclue; garde son owner admin. | Permanent until explicit admin layout story. |
| `frontend/src/pages/admin/AdminLogsPage.css` | admin logs local max widths | Page admin exclue; garde son owner admin. | Permanent until explicit admin layout story. |
| `frontend/src/layouts/AuthLayout.css` | auth form width | Largeur interne de formulaire, pas corps central applicatif. | Permanent unless auth layout redesign. |

Rules:

- No wildcard exception for all non-admin pages.
- No folder-wide exception.
- No `!important` to bypass the canonical width unless an existing exception is removed in the same story.
- Any retained non-admin page-level exception must name the exact selector, owner, reason, evidence and exit condition.
- Any retained internal width must be listed in `layout-width-after.md` with its exact selector and proof that it does not target the page-level wrapper.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, generated client, response envelope, status code or serialization contract is changed.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | layout caps | canonical width | `PageLayout` consumers | layout guard | no duplicate owner | sidebar overlap |
| 2 | page overrides | inherited width | affected pages | page tests | no wrapper cap | product width needed |
| 3 | public caps | layout or internal width | public pages | router tests | no duplicate cap | landing decision |
| 4 | guard gap | exact guard | future CSS | design-system guard | fails on unclassified cap | no exact register |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Width baseline | `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-before.md` | Capturer les largeurs concurrentes avant convergence. |
| Width result | `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-after.md` | Prouver l'owner canonique et les exceptions. |
| Final evidence | `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/generated/10-final-evidence.md` | Conserver commandes, tests, scans et resultats. |

## 4i. Reintroduction Guard

The implementation must add or preserve an architecture/design-system guard against reintroduction.

Deterministic guard sources:

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/**/*.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`

Required forbidden examples:

- A non-admin page wrapper defines `max-width: 900px`, `max-width: 1100px`,
  `max-width: 1200px`, `max-width: none !important`, or a local
  `--layout-max-width` as the page-level body width.
- `.app-bg-container:has(.is-chat-page)` bypasses the canonical non-admin width without an exact retained exception.
- A page-level selector uses `overflow-x: hidden` to hide a width defect.
- A new non-admin page-level width exception is accepted through wildcard, folder-wide rule, or unreviewed allowlist.
- Admin selectors are migrated to the non-admin width.

Guard evidence:

- `npm run test -- design-system page-architecture layout visual-smoke`
- targeted `rg` scans listed in the validation plan.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/styles/design-tokens.css` - `--layout-page-max-width` is `900px`, while `--layout-admin-max-width` and `--layout-sidebar-width` are distinct tokens.
- Evidence 2: `frontend/src/styles/backgrounds.css` - `.app-bg-container` caps non-admin content at `1100px` on desktop and has a separate `.app-bg-container--admin` cap.
- Evidence 3: `frontend/src/layouts/PageLayout.css` - `.page-layout` caps pages with `max-width: var(--layout-page-max-width)`.
- Evidence 4: `frontend/src/layouts/RootLayout.tsx` - admin routes receive `.app-bg-container--admin`, non-admin routes receive `.app-bg-container`.
- Evidence 5: `frontend/src/layouts/AppLayout.tsx` - app pages render inside `.app-shell-main`, with admin classified separately through `.app-shell-main--admin`.
- Evidence 6: `frontend/src/pages/ChatPage.css`,
  `frontend/src/pages/DailyHoroscopePage.css`,
  `frontend/src/pages/DashboardPage.css`,
  `frontend/src/pages/NatalChartPage.css`, `frontend/src/pages/HelpPage.css`,
  `frontend/src/pages/settings/Settings.css`,
  `frontend/src/pages/AstrologerProfilePage.css`,
  `frontend/src/pages/ConsultationResultPage.css` - current scans show
  page-local width overrides or caps that can compete with the global layout.
- Evidence 7: `frontend/src/tests/page-architecture-guards.test.ts` - existing route/layout guards protect `RootLayout`, `AppLayout` and page ownership.
- Evidence 8: `frontend/src/tests/design-system-guards.test.ts` - existing CSS guards protect App CSS modularity, inline styles, fallbacks and layout CSS syntax.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants
  `RG-047`, `RG-048`, `RG-059`, `RG-064`, `RG-068`, `RG-078` and `RG-080`
  consulted before story scope was finalized.

## 6. Target State

After implementation:

- A canonical non-admin central width token or layout rule maximizes usable width while keeping responsive side gutters.
- `.app-bg-container`, `.app-shell-main` and `.page-layout` agree on the central body width contract for non-admin routes.
- Non-admin pages inherit the central body width and keep only justified internal widths.
- Admin pages remain governed by `AdminLayout` and `--layout-admin-max-width`.
- Guard coverage fails if a future page reintroduces an unclassified page-level width override.
- Before/after evidence documents exact retained exceptions and allowed differences.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - no inline style may be introduced to adjust width.
  - `RG-048` - new CSS tokens or variables must not rely on unclassified `var(--token, value)` fallbacks.
  - `RG-059` - `App.css` and App CSS modules remain token-backed and guarded while layout width changes.
  - `RG-064` - page architecture guards must remain exact while page/layout ownership changes.
  - `RG-068` - `RootLayout` remains the route-level master layout and `AppLayout` remains a secondary shell.
  - `RG-078` - `App.css` remains limited to imports and the App CSS module structure remains bounded.
  - `RG-080` - `AstrologerProfilePage` must keep no horizontal overflow masking or inline styles while width is converged.
  - `RG-081` - non-admin central body width must remain owned by layout tokens/CSS, not page-local wrappers.
- Non-applicable invariants:
  - `RG-054` - no legacy admin redirect path is changed.
  - `RG-065` - admin prompts ownership is not modified.
  - `RG-073` - natal interpretation component ownership is not touched.
- Required regression evidence:
  - before/after width inventory;
  - `npm run test -- design-system page-architecture layout visual-smoke`;
  - `npm run lint`;
  - targeted scans for non-admin page-level width overrides and admin exclusions.
- Allowed differences:
  - wider non-admin central body and adjusted gutters only;
  - admin width unchanged;
  - retained internal component widths documented in `layout-width-after.md`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Canonical non-admin width owner exists. | Evidence profile: `ownership_routing`; `layout-width-after.md`; `npm run test -- design-system page-architecture layout`. |
| AC2 | Page wrapper uses the canonical width contract. | Evidence profile: `runtime_source_of_truth`; DOM/CSS guard; `npm run test -- AppShell page-architecture visual-smoke`. |
| AC3 | Width overrides are closed or exact. | Evidence profile: `baseline_before_after_diff`; `layout-width-after.md`; `rg -n "max-width|--layout-max-width|overflow-x" src`. |
| AC4 | Admin widths remain separate. | Evidence profile: `reintroduction_guard`; `npm run test -- AdminPage page-architecture`; admin width scan. |
| AC5 | Guard blocks unclassified width owners. | Evidence profile: `reintroduction_guard`; guard test; `npm run test -- design-system page-architecture`. |
| AC6 | No inline style width adjustment is introduced. | Evidence profile: `no_legacy_contract`; `npm run test -- design-system inline-style`. |
| AC7 | Frontend lint passes. | Evidence profile: `reintroduction_guard`; command `npm run lint`. |
| AC8 | Targeted layout smoke tests pass. | Evidence profile: `reintroduction_guard`; command `npm run test -- AppShell visual-smoke`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture the width baseline. (AC: AC1, AC3, AC4)
  - [x] Create `layout-width-before.md` with token values, layout container rules and page-level width overrides.
  - [x] Separate admin-owned widths from non-admin competing widths.

- [x] Task 2 - Define the canonical non-admin width contract at layout level. (AC: AC1, AC2)
  - [x] Update existing layout tokens/rules rather than creating duplicate ad hoc variables.
  - [x] Ensure `RootLayout`, `AppLayout` and `PageLayout` consume the same contract.
  - [x] Keep gutters responsive and account for the sidebar offset.

- [x] Task 3 - Converge non-admin page CSS consumers. (AC: AC2, AC3, AC6)
  - [x] Remove or replace page-level wrapper widths that compete with the layout.
  - [x] Convert retained widths to internal selectors when they govern text, cards, forms or component subregions.
  - [x] Eliminate `!important` width bypasses when they only compensate for the old layout cap.

- [x] Task 4 - Preserve admin width ownership. (AC: AC4)
  - [x] Verify `AdminLayout.css`, admin page CSS and `--layout-admin-max-width` remain admin-owned.
  - [x] Do not route admin pages through the non-admin width token.

- [x] Task 5 - Add or strengthen guards. (AC: AC5, AC6, AC8)
  - [x] Add a deterministic guard for non-admin page-level width overrides and exact exceptions.
  - [x] Keep existing design-system, inline-style, css-fallback and page-architecture guards green.

- [x] Task 6 - Capture after evidence and validate. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)
  - [x] Create `layout-width-after.md` and `generated/10-final-evidence.md`.
  - [x] Run all validation commands and record outcomes.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` for semantic layout values.
  - `frontend/src/styles/backgrounds.css` for `.app-bg-container` root width behavior.
  - `frontend/src/styles/app/layout.css` for shell and app layout primitives.
  - `frontend/src/layouts/PageLayout.css` as the generic page content wrapper.
  - existing Vitest guard files before adding a new test file.
- Do not recreate:
  - a second root layout;
  - page-specific central width tokens for each page;
  - admin width logic in non-admin CSS;
  - a new global CSS entrypoint outside the existing App CSS module structure.
- Shared abstraction required conditions:
  - it replaces multiple active page-level width declarations;
  - it is consumed by at least two non-admin layouts/pages immediately.

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

- non-admin page-level `max-width` competing with `PageLayout` or `.app-bg-container`;
- local `--layout-max-width` or page-specific equivalent used as central body width;
- `.app-bg-container:has(.is-*)` width bypass without exact retained exception;
- `max-width: none !important` on page wrappers as a central width escape hatch;
- `overflow-x: hidden` used to hide layout width defects;
- moving `--layout-admin-max-width` or `.admin-container` into the non-admin contract;
- editing `frontend/package.json` for this story.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Non-admin central body width | layout tokens, `backgrounds.css`, `PageLayout.css` | page-local wrapper max-widths and `!important` bypasses |
| App shell gutters and sidebar-aware spacing | `frontend/src/styles/app/layout.css` and `AppLayout` classes | page-local shell padding overrides |
| Admin central width | `frontend/src/layouts/AdminLayout.css` and admin tokens | non-admin layout token |
| Page internal readable width | page/component CSS owner | root layout unless it is true body width |
| Width guard ownership | `frontend/src/tests/design-system-guards.test.ts` or `page-architecture-guards.test.ts` | untested markdown-only convention |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/stories/regression-guardrails.md`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/PageLayout.tsx`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppShell.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/ConsultationResultPage.css`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/design-tokens.css` - adjust or add the canonical non-admin central width token.
- `frontend/src/styles/backgrounds.css` - align `.app-bg-container` with the canonical non-admin width while preserving admin modifier.
- `frontend/src/styles/app/layout.css` - align shell gutters/sidebar-aware spacing.
- `frontend/src/layouts/PageLayout.css` - make generic page wrapper depend on the canonical width.
- `frontend/src/tests/design-system-guards.test.ts` - add guard for width ownership and exceptions, or reuse an existing guard section.
- `frontend/src/tests/page-architecture-guards.test.ts` - update route/layout ownership guard when it owns the assertion.
- Non-admin page CSS files listed in section 18 - remove competing page-level width overrides or convert them to internal widths.
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-before.md` - baseline.
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-after.md` - result.
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/generated/10-final-evidence.md` - final evidence.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/AppShell.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- Targeted page tests for pages whose wrapper width changes, for example
  `AstrologersPage`, `AstrologerProfilePage`, `DailyHoroscopePage`,
  `NatalChartPage`, `SubscriptionGuidePage`, `ConsultationResultPage`.
  Missing test targets must be justified one by one in `generated/10-final-evidence.md`.

Files not expected to change:

- `backend/**` - no backend change.
- `frontend/package.json` - no dependency or script change.
- `frontend/src/pages/admin/**` - admin pages keep their own width unless a test fixture needs read-only evidence.
- `frontend/src/layouts/AdminLayout.css` - read-only unless an assertion/comment is strictly needed; do not change admin width.
- `frontend/src/app/routes.tsx` - route tree remains unchanged.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes require an explicit listing here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- design-system page-architecture layout
npm run test -- AppShell visual-smoke
npm run test -- AstrologersPage AstrologerProfilePage DailyHoroscopePage NatalChartPage SubscriptionGuidePage ConsultationResultPage
rg -n "max-width:\s*(900px|1100px|1200px|none\s*!important)|--layout-max-width|app-bg-container:has|overflow-x:\s*hidden" src/pages src/layouts src/styles -g "*.css"
rg -n "layout-admin-max-width|app-bg-container--admin|admin-container" src/layouts src/styles src/pages/admin -g "*.css" -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Expected scan handling:

- Non-admin page-level width hits must either be gone or listed as exact retained internal-width exceptions in `layout-width-after.md`.
- Admin hits are expected only under admin-owned files or admin layout selectors.
- Historical evidence under `_condamad/**` is not part of active frontend scans.

## 22. Regression Risks

- Risk: maximiser la largeur rend les pages trop proches des bords ou chevauche le menu lateral.
  - Guardrail: responsive gutters, sidebar-aware shell tests and visual-smoke checks.
- Risk: admin pages inherit the non-admin width.
  - Guardrail: admin modifier `.app-bg-container--admin`, `AdminPage` tests and admin scan.
- Risk: page-specific `max-width` values are removed from internal readable content by mistake.
  - Guardrail: before/after inventory distinguishes page wrapper width from internal text/card/form width.
- Risk: `ChatPage` or another wide page keeps a hidden bypass that becomes the new precedent.
  - Guardrail: exact exception register and no wildcard rule.
- Risk: App CSS modularity regresses while touching layout primitives.
  - Guardrail: `RG-078` and `npm run test -- design-system`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not modify admin width behavior except to prove it remains separate.
- Do not use inline styles.
- Do not hide horizontal overflow as a layout fix.
- Do not create compatibility shims, aliases, fallbacks, wrappers or re-exports.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- User brief 2026-05-10 - source request for uniform central body width.
- `frontend/src/layouts/RootLayout.tsx` - master route-level layout.
- `frontend/src/layouts/AppLayout.tsx` - application shell with sidebar state.
- `frontend/src/styles/design-tokens.css` - canonical layout tokens.
- `frontend/src/styles/backgrounds.css` - root visual container width.
- `frontend/src/layouts/PageLayout.css` - generic page wrapper width.
- `frontend/src/layouts/AdminLayout.css` - admin width owner excluded from convergence.
- `frontend/src/tests/page-architecture-guards.test.ts` - existing layout/page architecture guard owner.
- `frontend/src/tests/design-system-guards.test.ts` - existing CSS/design-system guard owner.
- `_condamad/stories/regression-guardrails.md` - applicable invariants and new `RG-081`.
