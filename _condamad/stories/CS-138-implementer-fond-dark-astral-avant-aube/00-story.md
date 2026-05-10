# Story CS-138 implementer-fond-dark-astral-avant-aube: Implementer le fond dark astral avant l'aube

Status: ready-to-dev

## 1. Objective

Mettre en oeuvre un fond dark global plus immersif pour le site, inspire d'une
nuit astrale avant l'aube, sans creer de fond decoratif concurrent. Le resultat
doit rester UI-friendly: lisible au centre, performant, actif uniquement en dark
mode, plus riche sur la landing et plus sobre sur les pages internes.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-11 + image de reference `.codex-artifacts/ChatGPT Image 11 mai 2026, 00_13_00.png`
- Reason for change: le fond dark existant utilise deja un gradient cosmique et
  un starfield, mais la direction souhaite une composition plus premium: ciel
  indigo profond, Voie lactee diffuse, lueur basse ambree et rares etoiles
  filantes, tout en preservant le fond canonique et les guardrails dark mode.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-theme-background`
- In scope:
  - Faire evoluer le fond dark canonique expose par `--premium-app-bg` et `--premium-app-bg-atmosphere`.
  - Reutiliser `frontend/src/components/StarfieldBackground.tsx` pour porter les
    couches non purement CSS.
  - Differencier une variante complete pour landing/home et une variante sobre
    pour pages internes via un scope route-level unique sous `RootLayout`.
  - Ajuster les surfaces UI partagees seulement quand la preuve before montre
    une perte de lisibilite causee par le nouveau fond.
  - Ajouter des tests/guards pour dark-only, reduced motion, absence de nouveaux
    styles inline, absence de nouvelle image de fond principale et respect du
    fond canonique.
  - Produire des preuves before/after dans le dossier de story.
- Out of scope:
  - Modifier le light mode, les routes, les contrats API, le backend, les donnees ou la navigation.
  - Refaire la landing page, les composants metier ou le design system complet.
  - Ajouter un asset 4K comme fond principal.
  - Introduire une librairie d'animation ou un canvas lourd sans decision explicite.
  - Corriger des dettes CSS non liees au fond dark ou a la lisibilite immediate.
- Explicit non-goals:
  - Ne pas recreer de paysage, montagnes, horizon realiste ou lever de soleil explicite.
  - Ne pas ajouter de styles inline.
  - Ne pas ajouter de nouveau fond page-level qui contourne `--premium-app-bg` / `--premium-app-bg-atmosphere`.
  - Ne pas affaiblir `RG-083` dark mode, `RG-084` fond global, `RG-061` App.css, `RG-068` layouts, `RG-078` modularite App.css, `RG-081` largeur centrale et `RG-082` polices.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: aucun archetype standard ne couvre une evolution visuelle
  frontend tokenisee; la story active les contrats necessaires pour proteger le
  rendu runtime, les snapshots, l'ownership CSS, les guards de reintroduction et
  les preuves persistantes.
- Additional validation rules:
  - La preuve runtime doit inclure le DOM rendu par Vitest/Testing Library pour `StarfieldBackground` et les guards AST/textuels existants des fichiers CSS.
  - Les preuves visuelles before/after doivent etre persistantes et liees aux viewports desktop/mobile.
  - Les scans de regression doivent comparer le baseline et l'after pour prouver
    zero nouveau hit sur styles inline, images raster de fond principal et fonds
    page-level concurrents.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: changement visuel du fond dark, couches atmospheriques, densite
    d'etoiles, Voie lactee diffuse, lueur basse, micro-animations rares et
    surfaces dark strictement liees a la lisibilite.
  - Interdit: changement de comportement metier, route, contrat API, structure de donnees, contenu affiche, largeur centrale, light mode ou navigation.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le dev agent estime qu'une grosse image raster, une dependance d'animation, une nouvelle taxonomie de theme ou un changement de layout est necessaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le rendu effectif depend de `html.dark`, de la cascade CSS, du layout route-level et du composant starfield. |
| Baseline Snapshot | yes | La story demande une evolution visuelle avec comparaison before/after desktop et mobile. |
| Ownership Routing | yes | Les couches de fond doivent rester sous les owners theme/layout existants, pas dans les pages ou `App.css`. |
| Allowlist Exception | no | Aucune exception large n'est autorisee; tout ecart doit bloquer ou etre documente dans les preuves after. |
| Contract Shape | no | Aucun DTO, payload, export public, route HTTP ou schema genere n'est modifie. |
| Batch Migration | no | Le changement porte sur un fond canonique unique, pas sur une migration par lots de consommateurs. |
| Reintroduction Guard | yes | Les anciens chemins invalides, images lourdes, styles inline et fonds page-level concurrents doivent rester bloques. |
| Persistent Evidence | yes | Les preuves visuelles et scans before/after doivent persister avec la story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DOM rendu par `frontend/src/layouts/RootLayout.tsx` avec `html.dark`.
  - CSS charges depuis `frontend/src/styles/premium-theme.css`, `frontend/src/styles/backgrounds.css`, `frontend/src/styles/app/*.css` et layouts.
  - AST/text guard dans `frontend/src/tests/design-system-guards.test.ts` pour le fond canonique et les styles interdits.
  - Generated manifest equivalent: inventaire `rg --files frontend/src` des owners CSS/TSX touches, conserve dans les artefacts before/after.
  - Tests frontend qui lisent les CSS et/ou rendent `StarfieldBackground`.
- Secondary evidence:
  - Image de reference `.codex-artifacts/ChatGPT Image 11 mai 2026, 00_13_00.png`.
  - Screenshots desktop/mobile before/after en dark mode.
  - Scans `rg` cibles sur images de fond, styles inline, `App.css` et variables de fond.
- Static scans alone are not sufficient because:
  - la lisibilite et la priorite des couches dependent de la cascade effective, du viewport et de `prefers-reduced-motion`.
- Runtime validation command:
  - `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-after.md`
- Required baseline content:
  - captures ou notes visuelles pour landing/home, une page interne, une page
    formulaire/auth existante, desktop et mobile;
  - inventaire des owners de fond: `premium-theme.css`, `backgrounds.css`, `RootLayout.tsx`, `LandingLayout.css`, `StarfieldBackground.tsx`;
  - etat des tests `StarfieldBackground`, `visual-smoke`, `theme-tokens` et `design-system`;
  - scans cibles des fonds page-level concurrents, styles inline et images de
    fond raster, avec classification des hits preexistants.
- Expected invariant:
  - un seul fond global canonique reste actif par theme; la version dark evoque une nuit astrale avant l'aube sans degrader la lisibilite centrale.
- Allowed differences:
  - teintes et gradients dark;
  - composition des couches de fond dark;
  - ajout de variables semantiques de fond dark;
  - ajustements limites des surfaces dark partagees pour conserver le contraste.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Fond global dark canonique | `frontend/src/styles/premium-theme.css` et `frontend/src/styles/backgrounds.css` | `frontend/src/App.css`, page CSS locale, style inline |
| Couches SVG/React non purement CSS | `frontend/src/components/StarfieldBackground.tsx` | composants de page, layout secondaire |
| Montage route-level du fond | `frontend/src/layouts/RootLayout.tsx` | pages individuelles ou wrappers ad hoc |
| Variante landing/home | classe/scope existant de `LandingLayout` ou attribut controle depuis layout | duplication du fond dans `LandingPage.css` |
| Variante pages internes | fond canonique global + modifier/scope sobre depuis `RootLayout` | halo page-level concurrent |
| Surfaces de lisibilite | tokens/surfaces partages existants `premium-theme.css`, `glass.css`, `styles/app/*.css` | valeurs hardcodees repetees ou overrides inline |
| Motion accessibility | CSS media query `prefers-reduced-motion` et tests associes | logique JS globale non testee |

Rules:

- Reutiliser les variables de couleurs et surfaces existantes avant d'en creer de nouvelles.
- Toute nouvelle variable doit avoir un nom semantique lie au fond astral, pas un nom mecanique.
- Les couleurs indicatives du brief doivent devenir des tokens ou rester
  encapsulees dans un seul owner CSS; elles ne doivent pas etre copiees dans
  plusieurs fichiers.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: la story ne permet aucune exception durable. Si un fond page-level
  concurrent, un style inline ou une grosse image est necessaire, le dev agent
  doit stopper et demander une decision utilisateur.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, DTO, payload, route, schema genere ou type public n'est modifie.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: un seul fond canonique dark est mis a jour; les variantes complete/sobre sont des scopes du meme systeme et non des lots de migration.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline visuelle et CSS | `dark-astral-background-before.md` | Etat actuel du fond dark, tests et owners. |
| Preuve after | `dark-astral-background-after.md` | Rendu final, screenshots, scans et tests. |
| Reference ambiance | `.codex-artifacts/ChatGPT Image 11 mai 2026, 00_13_00.png` | Inspirer l'ambiance sans reprendre paysage, montagnes ou horizon realiste. |

## 4i. Reintroduction Guard

- Guard target:
  - fond global canonique dark via `--premium-app-bg` / `--premium-app-bg-atmosphere`;
  - `StarfieldBackground` dark-only et non interactif;
  - absence de grosse image raster en fond principal;
  - absence de styles inline;
  - respect de `prefers-reduced-motion`.
- Forbidden examples:
  - nouveau `background-image: url(` pour une image raster principale;
  - nouveau `style=` dans les fichiers React touches;
  - nouveau fond `.landing-*`, `.people-*`, `*-bg-halo` qui remplace le fond canonique;
  - animation permanente qui ignore `prefers-reduced-motion`.
- Guard command/test:
  - `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system`
  - `rg -n "style=" src/layouts/RootLayout.tsx src/components/StarfieldBackground.tsx` depuis `frontend`
  - `rg -n "background-image:\\s*url\\(" src/styles/premium-theme.css src/styles/backgrounds.css src/layouts/LandingLayout.css` depuis `frontend`
  - `rg -n "prefers-reduced-motion|shooting|meteor|starfield" src/components src/styles src/layouts -g "*.tsx" -g "*.css"` depuis `frontend`
  - comparer les scans globaux before/after et prouver zero nouveau hit hors
    fichiers modifies et classifications preexistantes.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/layouts/RootLayout.tsx` - monte `StarfieldBackground` dans le shell global `app-bg`, puis rend le conteneur de route.
- Evidence 2: `frontend/src/components/StarfieldBackground.tsx` - rend aujourd'hui un SVG de 80 etoiles uniquement quand le theme vaut `dark`.
- Evidence 3: `frontend/src/styles/backgrounds.css` - definit `.app-bg`, `::before`, `::after` et `.starfield-bg`; le noise overlay est masque en dark mode.
- Evidence 4: `frontend/src/styles/premium-theme.css` - expose `--premium-app-bg` et `--premium-app-bg-atmosphere`, avec overrides dark existants.
- Evidence 5: `frontend/src/tests/StarfieldBackground.test.tsx` - teste le rendu dark-only et les proprietes deterministes du starfield.
- Evidence 6: `frontend/src/tests/visual-smoke.test.tsx` - contient deja des assertions sur le fond dark, le starfield et le fond canonique.
- Evidence 7: scans rapides du 2026-05-11 - `style=`, `background-image: url(`
  et `bg-halo|noise` ont des hits preexistants; la validation doit donc prouver
  zero nouveau hit au lieu d'exiger un scan global zero-hit.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-083` et `RG-084` sont applicables.

## 6. Target State

After implementation:

- Le dark mode affiche un ciel bleu noir/indigo profond, nuance violet sombre, sans noir pur dominant.
- Une lueur ambree basse, diffuse et subtile suggere l'aube sans horizon realiste.
- Le champ d'etoiles est irregulier, plus dense en haut et sur les bords, calme au centre.
- Une Voie lactee diffuse traverse lateralement ou diagonalement sans passer frontalement sur la zone principale de lecture.
- Les etoiles filantes sont rares, fines, non distrayantes et coupees ou figees avec `prefers-reduced-motion`; elles sont fortement reduites ou desactivees sur mobile.
- La landing/home utilise la version complete; les pages internes et formulaires
  utilisent une version plus sobre du meme fond canonique.
- Les cartes, champs et CTA restent lisibles avec surfaces dark bleu-noir,
  bordures lavande subtiles et CTA chauds sur les actions principales.
- Les variables ou classes du fond exposent des noms semantiques verifiables:
  `astral`, `dawn`, `milky`, `shooting` ou equivalents explicites.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-083` - la story touche directement le dark mode et doit eviter les surfaces light non classees, liens bleu navigateur et corrections dans `App.css`/inline styles.
  - `RG-084` - la story touche le fond arriere-plan global et doit conserver un seul fond canonique par theme via `--premium-app-bg` et `--premium-app-bg-atmosphere`.
  - `RG-061` - la story ne doit pas reintroduire de declarations visuelles actives dans `frontend/src/App.css`.
  - `RG-068` - le montage route-level doit rester sous `RootLayout`, sans layout concurrent.
  - `RG-078` - `App.css` doit rester minimal et les primitives globales doivent rester modulaires.
  - `RG-081` - le fond ne doit pas modifier la largeur utile centrale ni provoquer de scroll horizontal.
  - `RG-082` - la story ne doit pas modifier les familles de police.
- Non-applicable invariants:
  - `RG-001` a `RG-082` hors IDs cites - surfaces backend, API, prediction, billing, composants API ou routes frontend non touchees par ce fond.
- Required regression evidence:
  - tests `StarfieldBackground`, `visual-smoke`, `theme-tokens`, `design-system`;
  - screenshots ou notes before/after desktop/mobile;
  - scans `App.css`, `style=`, images raster de fond et `prefers-reduced-motion`;
  - absence de scroll horizontal dans l'audit visuel.
- Allowed differences:
  - differences visuelles dark mode du fond et surfaces strictement liees a la lisibilite; aucune difference de route, contenu, light mode ou layout width.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Fond dark reconstruit en couches astrales sobres. | `npm run test -- visual-smoke`; assertions CSS sur `astral/dawn/milky/shooting`. |
| AC2 | Light mode inchange hors ecarts documentes. | Evidence profile: `baseline_before_after_diff`; `npm run test -- theme-tokens design-system`; notes light after. |
| AC3 | Centre de lecture lisible. | screenshots desktop/mobile; `npm run test -- visual-smoke`. |
| AC4 | Variante complete activee sur landing. | `npm run test -- layout visual-smoke`; assertion sur le scope landing. |
| AC5 | Variante sobre activee hors landing. | `npm run test -- layout visual-smoke`; assertion sur le scope interne. |
| AC6 | `prefers-reduced-motion` est respecte. | `npm run test -- StarfieldBackground`; scan motion/starfield. |
| AC7 | Aucun nouveau fond page-level concurrent n'est introduit. | `npm run test -- design-system`; diff scan before/after des fonds concurrents. |
| AC8 | Aucune nouvelle image raster lourde ne pilote le fond principal. | `npm run test -- StarfieldBackground`; diff scan before/after `background-image`. |
| AC9 | Owners canoniques; aucun nouveau style inline ni correction active dans `App.css`. | `npm run test -- design-system visual-smoke`; diff scans `src/App.css`, `style=`. |
| AC10 | Preuves before/after presentes. | `rg -n "tests|screenshots|scans" dark-astral-background-before.md`; meme scan after. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et classifier les owners actuels (AC: AC1, AC2, AC10)
  - [ ] Subtask 1.1 - Lire `RootLayout.tsx`, `StarfieldBackground.tsx`, `backgrounds.css`, `premium-theme.css`, `LandingLayout.css` et les tests existants.
  - [ ] Subtask 1.2 - Rediger `dark-astral-background-before.md` avec screenshots/notes, tests actuels et scans cibles.

- [ ] Task 2 - Implementer les couches statiques du fond dark canonique (AC: AC1, AC3, AC4, AC5, AC7, AC8)
  - [ ] Subtask 2.1 - Ajuster les variables dark de `premium-theme.css` pour ciel indigo profond et lueur basse ambree.
  - [ ] Subtask 2.2 - Ajuster `backgrounds.css` pour atmosphere, Voie lactee diffuse, vignettage et protection de lisibilite.
  - [ ] Subtask 2.3 - Ajouter le scope complete/sobre via layouts ou classes existantes sans dupliquer le fond.

- [ ] Task 3 - Faire evoluer les etoiles et micro-animations (AC: AC1, AC6, AC8)
  - [ ] Subtask 3.1 - Enrichir `StarfieldBackground` comme owner unique, avec generation deterministe et faible DOM.
  - [ ] Subtask 3.2 - Ajouter les etoiles filantes rares seulement apres validation de la composition statique.
  - [ ] Subtask 3.3 - Ajouter `prefers-reduced-motion` et reductions mobile.

- [ ] Task 4 - Ajuster uniquement les surfaces UI affectees par la lisibilite (AC: AC3, AC9)
  - [ ] Subtask 4.1 - Verifier cartes, champs, boutons et CTA en dark mode sur les routes ciblees.
  - [ ] Subtask 4.2 - Modifier seulement les owners CSS dont le baseline prouve une perte de lisibilite causee par le nouveau fond.

- [ ] Task 5 - Renforcer tests, guards et preuves after (AC: AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 5.1 - Mettre a jour `StarfieldBackground.test.tsx`, `visual-smoke.test.tsx` et les guards design-system.
  - [ ] Subtask 5.2 - Executer les commandes de validation et rediger `dark-astral-background-after.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/premium-theme.css` pour les variables globales de fond premium.
  - `frontend/src/styles/backgrounds.css` pour les couches appliquees a `.app-bg` et `.starfield-bg`.
  - `frontend/src/layouts/RootLayout.tsx` pour le montage global du fond.
  - `frontend/src/components/StarfieldBackground.tsx` comme unique owner React/SVG du champ d'etoiles.
  - tokens existants `--premium-*`, `--glass-*`, `--color-*`, `--app-*` quand ils representent deja la surface ou le role.
- Do not recreate:
  - un second theme provider;
  - un fond page-level complet dans `LandingPage.css`, pages internes ou `App.css`;
  - une image de fond principale raster;
  - une librairie d'animation pour des etoiles filantes.
- Shared abstraction allowed only if:
  - elle remplace une responsabilite existante de `StarfieldBackground` ou factorise une variante complete/sobre consommee par `RootLayout` sans ajouter de chemin concurrent.

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

- `frontend/src/App.css` - aucun nouveau style actif de fond dark ou correction de surface.
- `style=` dans les fichiers React touches.
- `background-image: url(` pour une grosse image raster de fond principal sous `frontend/src/styles`, `frontend/src/layouts` ou `frontend/src/pages`.
- classes page-level qui remplacent le fond canonique: nouveaux `*-bg-halo`, `*-noise`, `landing-background`, `space-background`, `cosmic-background` hors decision documentee.
- animations qui changent `top`, `left`, `width`, `height`, `background-position` ou autre propriete layout pour les etoiles filantes.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Fond global par theme | `frontend/src/styles/premium-theme.css` + `frontend/src/styles/backgrounds.css` | pages CSS locales, `App.css`, styles inline |
| Montage du fond | `frontend/src/layouts/RootLayout.tsx` | layouts secondaires, pages |
| Etoiles SVG/React | `frontend/src/components/StarfieldBackground.tsx` | composants de page |
| Surface de lisibilite partagee | `frontend/src/styles/glass.css`, `frontend/src/styles/app/*.css`, owner composant/page exact | overrides globaux non scopes |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/components/StarfieldBackground.tsx`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/tests/StarfieldBackground.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/premium-theme.css` - mettre a jour les tokens dark du ciel, de l'aube basse et des surfaces premium.
- `frontend/src/styles/backgrounds.css` - composer les couches globales, la Voie lactee, la vignette, les restrictions mobile/reduced-motion.
- `frontend/src/components/StarfieldBackground.tsx` - enrichir le starfield SVG/React avec etoiles irregulieres et etoiles filantes rares.
- `frontend/src/layouts/RootLayout.tsx` - ajouter le scope de variante retenu.
- `frontend/src/layouts/LandingLayout.css` - exposer la variante complete sans dupliquer le fond.
- `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-before.md` - baseline.
- `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/StarfieldBackground.test.tsx` - dark-only, DOM raisonnable, reduced motion et classes attendues.
- `frontend/src/tests/visual-smoke.test.tsx` - fond dark astral, canonical background, pas de bokeh/orbes, pas de nouvelle image.
- `frontend/src/tests/design-system-guards.test.ts` - guards App.css, fond canonique et absence de nouveaux fonds concurrents.

Files not expected to change:

- `frontend/src/App.css` - protege par `RG-061`, `RG-078` et `RG-084`.
- `backend/**` - hors domaine.
- `frontend/src/api/**` - aucun contrat API touche.
- `frontend/src/pages/**/*.tsx` - pas de logique page necessaire pour un fond global.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- StarfieldBackground visual-smoke theme-tokens design-system
npm run test -- layout
rg -n "style=" src/layouts/RootLayout.tsx src/components/StarfieldBackground.tsx
rg -n "background-image:\s*url\(" src/styles/premium-theme.css src/styles/backgrounds.css src/layouts/LandingLayout.css
rg -n "prefers-reduced-motion|shooting|meteor|starfield" src/components src/styles src/layouts -g "*.tsx" -g "*.css"
rg -n "premium-app-bg|premium-app-bg-atmosphere|app-bg|starfield-bg" src/styles src/layouts src/components -g "*.css" -g "*.tsx"
rg -n "dark|html\.dark|starfield|premium-app-bg" src/App.css
npm run lint
npm run build
```

Before/after scan commands to record in artifacts:

```powershell
rg -n "style=" src -g "*.tsx" -g "*.jsx"
rg -n "background-image:\s*url\(" src/styles src/layouts src/pages -g "*.css" -g "*.scss"
rg -n "bg-halo|noise|landing-background|space-background|cosmic-background" src/styles src/layouts src/pages -g "*.css"
```

The after artifact must state whether each global scan has zero new hits versus
the before artifact. Existing classified hits are not blockers.

Manual/runtime checks required:

- Desktop large: landing/home en dark mode, verifier Voie lactee douce, centre lisible, lueur basse subtile.
- Laptop/tablet: densite reduite ou non envahissante, pas de scroll horizontal.
- Mobile: Voie lactee attenuee, etoiles reduites, etoiles filantes desactivees ou tres rares.
- Reduced motion: etoiles filantes et scintillements desactives ou figes.
- Light mode: fond light conserve.

## 22. Regression Risks

- Risk: le fond devient une illustration de paysage ou un wallpaper spatial.
  - Guardrail: AC1, AC3, AC8, screenshots before/after et interdiction de grosse image raster.
- Risk: une page recree un fond concurrent pour obtenir la variante landing.
  - Guardrail: `RG-084`, AC7, scans fonds page-level.
- Risk: les animations degradent mobile ou ignorent l'accessibilite motion.
  - Guardrail: AC6, media query `prefers-reduced-motion`, tests/scans.
- Risk: le nouveau fond degrade les contrastes dark mode.
  - Guardrail: `RG-083`, AC3, visual-smoke et screenshots cibles.
- Risk: des corrections opportunistes reviennent dans `App.css`.
  - Guardrail: `RG-061`, `RG-078`, AC9 et scan `src/App.css`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass guardrails through repointing, wrapper, alias, fallback, duplicate page-level background, inline style or `App.css` override.
- Implementer en deux passes: composition statique sobre d'abord, micro-animations ensuite seulement si la lisibilite est validee.
- Respecter les instructions projet: tout fichier applicatif nouveau ou modifie
  significativement doit contenir un commentaire global en francais en haut du
  fichier et des docstrings/commentaires publics ou non triviaux en francais.

## 24. References

- Demande utilisateur du 2026-05-11 - brief fonctionnel et visuel du fond dark astral avant l'aube.
- `.codex-artifacts/ChatGPT Image 11 mai 2026, 00_13_00.png` - reference d'ambiance uniquement; le paysage et l'horizon realiste sont explicitement hors scope.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-083` et `RG-084` applicables au dark mode et au fond global.
- `frontend/src/layouts/RootLayout.tsx` - montage actuel du fond global.
- `frontend/src/components/StarfieldBackground.tsx` - owner actuel du starfield dark-only.
- `frontend/src/styles/backgrounds.css` - owner CSS actuel des couches de fond global.
- `frontend/src/styles/premium-theme.css` - tokens premium et fond dark actuel.
