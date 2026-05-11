# Story CS-146 corriger-responsive-accessibilite-landing: Corriger le responsive et l'accessibilite critique de la landing

Status: done

## 1. Objective

Corriger les defauts UX/UI critiques observes sur la landing publique: la
navbar ne doit plus deborder en tablette, le menu mobile doit se comporter
comme une vraie surface modale accessible, le hero mobile doit exposer plus vite
les preuves et sections suivantes, et le H1 doit rester lisible visuellement et
correct semantiquement. Le rendu doit rester aligne au style global premium
existant, sans nouveau fond dedie, sans style inline et sans refonte marketing
globale.

## 2. Trigger / Source

- Source type: code-review
- Source reference: rapport UX/UI Codex du 2026-05-11, avec revue Bob
  React/TypeScript et Merlin CSS.
- Reason for change: la revue a mesure un overflow navbar a `768px`, une
  absence de focus trap dans le menu mobile `aria-modal`, un hero mobile de plus
  de deux viewports avant la preuve sociale, et un H1 accessible concatene sans
  espace.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-landing-page`
- In scope:
  - Corriger le breakpoint desktop de `LandingNavbar` pour garder le menu
    compact jusqu'a `1023px`.
  - Ajouter une gestion modale accessible au menu mobile landing.
  - Ajuster le hero landing mobile/tablette pour reduire sa hauteur sans
    supprimer la preview produit.
  - Corriger le nom accessible du H1 hero sans changer la promesse marketing.
  - Ajouter ou adapter les tests landing pertinents et les preuves
    before/after.
- Out of scope:
  - Modifier le backend, les routes API, le pricing catalogue, Stripe,
    l'authentification ou les contenus SEO/head.
  - Refaire le copywriting global de la landing ou changer les plans tarifaires.
  - Modifier `RootLayout`, le fond global, `App.css`, le starfield ou la
    strategie theme provider.
  - Traiter les dettes CSS mineures non bloquantes hors navbar/hero/menu.
- Explicit non-goals:
  - Ne pas recreer `app-bg--landing`.
  - Ne pas ajouter de style inline ni d'override global opportuniste.
  - Ne pas introduire de nouvelle dependance modal/drawer.
  - Ne pas affaiblir `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087` ou
    `RG-088`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: le catalogue ne contient pas d'archetype dedie a une
  correction UX responsive/a11y page-scoped; cette story active runtime,
  baseline, ownership, reintroduction guard et preuves persistantes.
- Additional validation rules:
  - Les corrections doivent etre prouvees sur desktop, tablette `768px` et
    mobile `390px`.
  - Les tests clavier doivent prouver que le focus ne sort plus du menu mobile
    ouvert.
  - Le debut de `#social-proof` doit remonter d'au moins `240px` sur mobile
    `390x844` par rapport au baseline. Condition de sortie alternative:
    `#social-proof` est deja avant `y=1560` dans l'artefact after.
  - Les corrections visuelles restent dans les owners landing existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: changement de breakpoint navbar, gestion focus/scroll du menu
    mobile, dimensions/espacements hero mobile, nom accessible du H1, tests et
    artefacts de preuve.
  - Interdit: changement de route, fond global, SEO/head, analytics existants,
    contenu tarifaire, provider theme, backend ou API.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la correction impose de supprimer la preview hero,
  retirer un CTA public, changer la promesse marketing ou modifier le fond
  global canonique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le probleme est visible au runtime: overflow, focus clavier, hauteur hero et DOM accessible. |
| Baseline Snapshot | yes | Les mesures before/after desktop/tablette/mobile sont necessaires pour prouver la correction UX. |
| Ownership Routing | yes | Les changements doivent rester dans les owners landing React/CSS existants. |
| Allowlist Exception | no | Aucune exception large ou wildcard n'est autorisee pour contourner les guards. |
| Contract Shape | no | Aucun contrat API, schema, payload ou type public partage n'est modifie. |
| Batch Migration | no | La correction reste dans un seul domaine landing, sans lots multi-domaines. |
| Reintroduction Guard | yes | Le retour de l'overflow tablette, du focus leak menu ou des styles interdits doit etre detecte. |
| Persistent Evidence | yes | Les captures, mesures Playwright et scans doivent etre conserves dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - rendu local de `/` via `LandingLayout`, `LandingNavbar`, `LandingPage` et
    `HeroSection`;
  - AST guard dans `frontend/src/tests/design-system-guards.test.ts` pour les
    interdits CSS et ownership landing;
  - DOM runtime Playwright de `/` pour `document.documentElement.scrollWidth`,
    `document.documentElement.clientWidth`, `document.activeElement`,
    `getBoundingClientRect()` et roles accessibles;
  - tests RTL/Playwright ou Vitest simulant clavier, menu mobile et breakpoints;
  - mesures DOM `scrollWidth/clientWidth`, bounding boxes navbar et sequence de
    focus.
- Secondary evidence:
  - scans cibles sur `style=`, `app-bg--landing`, `letter-spacing` negatif
    landing sur les fichiers touches, et roles `--landing-*` non classes.
- Static scans alone are not sufficient because:
  - l'overflow et le focus leak dependent du viewport, de l'etat menu et de la
    cascade runtime.
- Runtime validation command:
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-after.md`
- Required baseline content:
  - captures desktop `1440x1000`, tablette `768x1024`, mobile `390x844` et menu
    mobile ouvert;
  - mesures `scrollWidth/clientWidth`, rectangles navbar/actions/hero/CTA et
    position du debut de `#social-proof`;
  - sequence de tabulation menu ouvert;
  - texte accessible du H1.
- Expected invariant:
  - aucun overflow horizontal, focus confine au menu ouvert, CTA hero visible
    dans le premier viewport mobile, preuve sociale mobile au moins `240px`
    plus haute qu'avant ou deja avant `y=1560`, fond global inchange.
- Allowed differences:
  - breakpoint navbar, espacements/dimensions hero mobile/tablette, opacite de
    surface menu mobile et comportement focus/scroll du menu.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Structure et etat menu landing | `frontend/src/pages/landing/sections/LandingNavbar.tsx` | composant global non reutilise, `App.tsx`, inline handlers disperses |
| Styles navbar/menu landing | `frontend/src/pages/landing/sections/LandingNavbar.css` | `frontend/src/App.css`, style inline, overrides globaux |
| Structure hero landing | `frontend/src/pages/landing/sections/HeroSection.tsx` | composant marketing duplique |
| Styles hero landing | `frontend/src/pages/landing/LandingPage.css` | CSS de section voisine, `App.css`, inline styles |
| Tests landing | `frontend/src/tests/**` existants ou nouveaux tests landing adjacents | tests qui encodent un comportement legacy comme nominal |
| Preuves persistantes | `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/**` | console output non persiste |

Rules:

- Les corrections CSS doivent reutiliser les tokens/roles landing existants.
- Toute nouvelle variable `--landing-*` doit avoir un owner exact et etre
  testee ou documentee dans l'artefact after.
- Aucun composant modal generique ne doit etre cree sans preuve de reuse hors
  landing.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune nouvelle exception n'est attendue; les interdits doivent
  rester exacts et zero-hit.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO, client genere ou type
  public partage n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la correction ne migre pas plusieurs domaines ou lots de
  consommateurs.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline responsive/a11y landing | `landing-responsive-a11y-before.md` | Captures et mesures avant correction. |
| Preuve after responsive/a11y landing | `landing-responsive-a11y-after.md` | Captures, mesures, tests, scans et differences autorisees apres correction. |

## 4i. Reintroduction Guard

- Guard target:
  - la navbar ne deborde pas a `768px`;
  - le focus ne sort pas du menu mobile ouvert;
  - le H1 accessible contient un separateur lisible entre lead et accent;
  - le hero mobile respecte le seuil `#social-proof` documente;
  - les interdits landing restent absents.
- Forbidden examples:
  - `app-bg--landing`;
  - `style=` sous `frontend/src/pages/landing` ou `frontend/src/layouts`;
  - breakpoint desktop navbar qui expose simultanement liens, langue, login et
    CTA a `768px` si cela recree l'overflow;
  - `aria-modal="true"` sans confinement du focus;
  - focus clavier atteignant `.hero-cta-primary` pendant que
    `#landing-mobile-menu` est ouvert.
- Guard command/test:
  - test RTL ou Playwright landing pour sequence de tabulation menu ouvert;
  - test/mesure responsive `scrollWidth === clientWidth` a `768px` et `390px`;
  - `cd frontend; npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`;
  - `cd frontend; npm run lint`;
  - `rg -n "app-bg--landing|style=" frontend/src/pages/landing frontend/src/layouts`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding; it is sourced from a
  repo-informed UX/UI code review.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/pages/landing/sections/LandingNavbar.css` - le
  layout desktop est active des `min-width: 768px`, alors que les actions
  debordent sur tablette dans la mesure runtime.
- Evidence 2: `frontend/src/pages/landing/sections/LandingNavbar.tsx` - le menu
  mobile rend `role="dialog"` et `aria-modal="true"` sans focus trap, scroll
  lock ni restauration du focus.
- Evidence 3: `frontend/src/pages/landing/LandingPage.css` - le H1 mobile est
  contraint a `max-width: 9ch`, contribuant a un hero mobile tres haut.
- Evidence 4: `frontend/src/pages/landing/sections/HeroSection.tsx` - le H1 est
  compose de deux `span` sans separateur textuel accessible.
- Evidence 5: `.codex-artifacts/landing-desktop.png`,
  `.codex-artifacts/landing-mobile.png` et
  `.codex-artifacts/landing-mobile-menu.png` - captures generees pendant la
  revue UX/UI initiale.
- Evidence 6: `_condamad/stories/CS-139-refactoriser-ownership-css-landing/00-story.md` -
  l'ownership CSS landing est deja classifie et doit rester respecte.
- Evidence 7: `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/00-story.md` -
  le theme landing light/dark est deja garde et ne doit pas etre contourne.
- Evidence 8: `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/00-story.md` -
  le menu mobile a deja un contrat visuel; cette story ajoute le comportement
  accessible et le responsive.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-083` a `RG-088` s'appliquent.

## 6. Target State

After implementation:

- La landing ne produit aucun scroll horizontal en desktop, tablette ou mobile.
- A `768px`, la navigation utilise un layout qui tient dans le viewport.
- Le menu mobile est une surface modale accessible: focus initial, focus trap,
  Escape, fermeture explicite, restauration du focus, scroll lock et absence de
  tabulation vers le contenu arriere-plan.
- Le hero mobile reste premium mais plus compact; le CTA principal reste visible
  dans le premier viewport et la preuve sociale remonte de facon mesurable.
- Le H1 garde son rendu visuel en deux lignes/blocs mais son nom accessible est
  comprehensible.
- Les tests et artefacts after prouvent la correction sans changer le fond
  global, les routes, le SEO/head, l'analytics ou le backend.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - la landing doit rester lisible en dark mode et ne pas corriger
    ses surfaces via `App.css` ou inline styles.
  - `RG-084` - la correction ne doit pas creer de fond page-level concurrent.
  - `RG-085` - le fond dark astral global doit rester canonique et dark-only.
  - `RG-086` - `app-bg--landing` ne doit pas revenir.
  - `RG-087` - la page longue landing ne doit pas modifier la peinture du fond
    global attache au viewport.
  - `RG-088` - les CSS landing ne doivent pas ajouter motion/filter
    non classes.
- Non-applicable invariants:
  - `RG-001` a `RG-082` - domaines backend, API, pages hors landing,
    composants hors surface landing ou dettes deja non touchees par cette story.
- Required regression evidence:
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles`,
    `page-architecture` et tests d'interaction menu mobile;
  - captures et mesures before/after desktop/tablette/mobile;
  - scans `app-bg--landing`, `style=`, `@keyframes|animation|filter|backdrop-filter`
    sur les fichiers landing touches par l'implementation.
- Allowed differences:
  - breakpoint navbar, focus/scroll menu mobile, dimensions hero mobile et
    surface menu; aucune difference de route, fond global, SEO/head, analytics
    ou backend.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Navbar sans overflow aux viewports cibles. | Profile: `baseline_before_after_diff`; command: `npm run test -- LandingPage`; artifact boxes. |
| AC2 | Focus confine dans le menu mobile ouvert. | Profile: `reintroduction_guard`; command: `npm run test -- LandingPage`; focus trap, Escape, restoration. |
| AC3 | Hero mobile respecte le seuil `#social-proof`. | Profile: `baseline_before_after_diff`; command: `npm run test -- visual-smoke LandingPage`; y-position. |
| AC4 | H1 hero expose un nom accessible avec separateur. | Profile: `frontend_typecheck_no_orphan`; command: `npm run test -- LandingPage`; name assertion. |
| AC5 | Interdits landing absents des fichiers touches. | Profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- design-system AppBgStyles`; scans. |
| AC6 | Validation frontend cible OK. | Command: `npm run lint`; command: `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline responsive/a11y (AC: AC1, AC2, AC3, AC4)
  - [ ] Subtask 1.1 - Lire `LandingNavbar.tsx`, `LandingNavbar.css`,
    `HeroSection.tsx`, `LandingPage.css`, tests landing et guardrails.
  - [ ] Subtask 1.2 - Creer `landing-responsive-a11y-before.md` avec captures,
    mesures viewport, sequence de focus et nom accessible H1.

- [ ] Task 2 - Corriger le responsive navbar (AC: AC1, AC5)
  - [ ] Subtask 2.1 - Passer l'affichage desktop de la navbar a un seuil
    `min-width: 1024px` ou equivalent plus strict.
  - [ ] Subtask 2.2 - Ajouter une preuve testee ou mesuree a `768x1024` et
    `390x844`.

- [ ] Task 3 - Rendre le menu mobile modal accessible (AC: AC2, AC5)
  - [ ] Subtask 3.1 - Ajouter focus initial, focus trap, restauration du focus,
    Escape et scroll lock dans `LandingNavbar.tsx`.
  - [ ] Subtask 3.2 - Renforcer le test clavier pour prouver que le focus ne
    sort pas du menu ouvert.
  - [ ] Subtask 3.3 - Conserver le rendu menu existant; seule une correction
    minimale de lisibilite documentee dans l'artefact after est autorisee.

- [ ] Task 4 - Compactifier le hero mobile et corriger le H1 (AC: AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Ajuster les contraintes mobile/tablette du H1 et de la
    preview dans `LandingPage.css`.
  - [ ] Subtask 4.2 - Corriger le nom accessible du H1 dans `HeroSection.tsx`
    sans ajouter de deuxieme H1.
  - [ ] Subtask 4.3 - Verifier que le CTA principal reste visible avant `y=844`
    et que `#social-proof` respecte le seuil AC3.

- [ ] Task 5 - Produire preuves after et validation (AC: AC1, AC2, AC3, AC4, AC5, AC6)
  - [ ] Subtask 5.1 - Creer `landing-responsive-a11y-after.md` avec captures,
    mesures, scans et differences autorisees.
  - [ ] Subtask 5.2 - Executer lint, tests cibles et scans interdits.
  - [ ] Subtask 5.3 - Documenter toute commande non executee avec raison et
    risque.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `LandingNavbar.tsx` comme owner unique de l'etat menu/langue landing.
  - `LandingNavbar.css` et `LandingPage.css` comme owners CSS existants.
  - variables/tokens `--landing-*`, `--premium-*`, `--font-*` et guards
    existants avant toute nouvelle variable.
  - tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles` et
    `page-architecture` comme points d'extension.
- Do not recreate:
  - un composant modal global sans reutilisation prouvee;
  - une deuxieme navbar mobile;
  - un theme/fond dedie landing;
  - des helpers DOM dupliques si une primitive locale simple suffit.
- Shared abstraction allowed only under this condition:
  - elle remplace une duplication prouvee entre surfaces landing, reste dans le
    domaine landing, et possede un test cible.

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

- `app-bg--landing`
- `style=` dans `frontend/src/pages/landing` ou `frontend/src/layouts`
- modifications opportunistes dans `frontend/src/App.css`
- `aria-modal="true"` sans focus trap teste
- correction de l'overflow par `overflow-x: hidden` global
- ajout d'une dependance npm modal/drawer

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Navbar et menu mobile landing | `frontend/src/pages/landing/sections/LandingNavbar.tsx` / `.css` | `App.css`, layouts globaux, composants dupliques |
| Hero landing | `frontend/src/pages/landing/sections/HeroSection.tsx` et `frontend/src/pages/landing/LandingPage.css` | sections voisines, styles inline |
| Fond global | `frontend/src/layouts/RootLayout.tsx`, `frontend/src/styles/backgrounds.css`, tokens premium | variante `app-bg--landing`, fond page-level landing |
| Preuves de correction | `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/**` | sortie console seule |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or
  generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/pages/landing/sections/LandingNavbar.tsx`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/tests/LandingPage.test.tsx`
- `frontend/src/tests/FaqSection.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppBgStyles.test.ts`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-139-refactoriser-ownership-css-landing/00-story.md`
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/00-story.md`
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/00-story.md`
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/00-story.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/landing/sections/LandingNavbar.tsx` - focus trap, scroll
  lock, focus restoration and Escape behavior.
- `frontend/src/pages/landing/sections/LandingNavbar.css` - breakpoint and
  menu/mobile responsive surface adjustments.
- `frontend/src/pages/landing/sections/HeroSection.tsx` - accessible H1 name or
  separator.
- `frontend/src/pages/landing/LandingPage.css` - mobile/tablet hero constraints.
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-before.md` - baseline evidence.
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-after.md` - final evidence.

Likely tests:

- `frontend/src/tests/LandingPage.test.tsx` - render/layout assertions for
  landing hero and H1.
- `frontend/src/tests/visual-smoke.test.tsx` - responsive/no-overflow or visual
  guard for landing responsive evidence.
- `frontend/src/tests/design-system-guards.test.ts` - forbidden style/fond guard
  updates for exact landing interdits.
- `frontend/src/tests/AppBgStyles.test.ts` - expected unchanged; run to prove
  no global background regression.

Files not expected to change:

- `frontend/src/App.css` - forbidden destination for landing fixes.
- `frontend/src/layouts/RootLayout.tsx` - fond global hors scope.
- `frontend/src/pages/landing/LandingHead.tsx` - SEO/head hors scope.
- `frontend/src/config/pricingConfig.ts` - pricing catalogue hors scope.
- `backend/**` - aucun changement backend attendu.

## 20. Dependency Policy

- New dependencies: forbidden.
- Justification: les outils existants React, Vitest, Testing Library et
  Playwright couvrent deja les assertions DOM, clavier et responsive requises.
- New runtime dependencies: forbidden.
- New dev dependencies: forbidden unless the dev agent proves existing
  Playwright/Vitest/Testing Library cannot express the check.
- Python commands: if a story validation script is run, activate `.venv` first:
  `.\.venv\Scripts\Activate.ps1`.
- Frontend commands: run from `frontend/` with npm scripts already present.

## 21. Validation Plan

Required commands:

```powershell
cd frontend
npm run lint
npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture
rg -n "app-bg--landing|style=" src/pages/landing src/layouts
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
```

Required runtime/manual evidence:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Then capture or script checks for:

- `1440x1000`, `768x1024`, `390x844`;
- `document.documentElement.scrollWidth === document.documentElement.clientWidth`;
- focus sequence while `#landing-mobile-menu` is open;
- single H1 with accessible name containing a separator between title lead and
  accent;
- screenshots before/after stored or referenced in the story artifacts.

Story contract validation after drafting or editing this story:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-146-corriger-responsive-accessibilite-landing/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-146-corriger-responsive-accessibilite-landing/00-story.md
```

## 22. Regression Risks

- Le breakpoint navbar peut masquer trop longtemps la navigation desktop:
  verifier que le menu mobile reste clair et rapide jusqu'a `1023px`.
- Le focus trap peut bloquer des interactions langue/menu si les boutons ne sont
  pas inclus dans la liste focusable.
- Le scroll lock peut rester actif apres fermeture si le cleanup React est
  incomplet.
- La compactification du hero peut affaiblir la preview produit; comparer les
  captures before/after et conserver le signal produit dans le premier ecran.
- Une correction CSS par `overflow-x: hidden` global masquerait le symptome sans
  corriger la cause; ce chemin est interdit.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker instead of
  weakening the AC.
- Do not preserve legacy behavior as a compatibility path.
- Commencer par produire l'artefact before avec les mesures de la revue si elles
  sont encore reproductibles.
- Modifier par petits deltas: navbar responsive, menu modal, hero/H1, puis
  tests.
- Ne pas toucher aux textes marketing sauf pour l'accessibilite du H1.
- Ne pas traiter `pricingConfig`, `LandingRedirect` fallback ou dette CSS
  globale dans cette story; creer une story separee pour ces sujets.
- Avant de conclure, mettre a jour l'artefact after avec commandes executees,
  captures, mesures et limites restantes.

## 24. References

- `frontend/src/pages/landing/sections/LandingNavbar.tsx`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-139-refactoriser-ownership-css-landing/00-story.md`
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark/00-story.md`
- `_condamad/stories/CS-144-converger-contrat-visuel-landing-menu-mobile/00-story.md`
- `_condamad/stories/CS-145-ajouter-garde-complexite-visuelle-landing/00-story.md`
