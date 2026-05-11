# Story CS-148 corriger-catalogue-astrologers-responsive-conversion: Corriger le catalogue /astrologers responsive et conversion

Status: ready-to-dev

## 1. Objective

Corriger la page `/astrologers` pour qu'elle presente les astrologues dans une
grille stable, lisible et actionnable sur desktop comme sur mobile:
neutralisation du layout featured pleine largeur casse, correction du
responsive mobile, retour de signaux de choix utiles, affordance visible vers
le profil, hauteur de carte robuste, et correction de la typo CSS qui empeche
la texture prevue.

## 2. Trigger / Source

- Source type: audit
- Source reference: diagnostic utilisateur colle dans la demande du
  2026-05-11 sur la page `/astrologers`.
- Reason for change: la premiere carte forcee en `span 2` cree une carte
  desktop vide et mal hierarchisee; le mobile `390px` reste en deux colonnes a
  cause de la specificite `.people-page .person-grid`; les cartes cliquables
  n'ont pas de CTA visible; les badges utiles sont masques; la hauteur fixe et
  la dette CSS rendent la page fragile.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-astrologers-catalog`
- In scope:
  - Repenser la grille de `/astrologers` dans les owners existants
    `AstrologerGrid.tsx`, `AstrologerCard.tsx`, `cards.css`, `tokens.css` et
    `media.css`.
  - Neutraliser l'effet de layout `featured` lie a `index === 0`, sauf decision
    produit explicite de conserver une vraie carte editoriale horizontale avec
    tests dedies.
  - Corriger le responsive mobile pour obtenir une colonne lisible sous mobile
    et aucun scroll horizontal.
  - Ajouter une affordance visible de type `Voir le profil` ou
    `Choisir cet astrologue` sans bouton imbrique.
  - Reintroduire les signaux utiles dans la liste compacte: IA ou humain,
    astrologue par defaut, specialite principale ou badge editorial sobre.
  - Stabiliser les hauteurs de cartes avec `min-height`, line clamp CSS et
    espacement vertical regulier.
  - Corriger `mix-alend-mode` en `mix-blend-mode` dans `media.css`.
  - Ajouter ou adapter les tests frontend cibles et les artefacts before/after.
- Out of scope:
  - Modifier le backend, les endpoints astrologues, les schemas API, les donnees
    astrologues ou le client HTTP.
  - Modifier la route `/astrologers/:id`, son CTA profil, ses avis ou son style
    profile page.
  - Modifier le fond global, `RootLayout`, `PageLayout` ou la largeur centrale
    globale.
  - Ajouter une dependance runtime ou de test.
  - Refaire le design de la landing, du chat, des consultations ou du dashboard.
- Explicit non-goals:
  - Ne pas ajouter de style inline.
  - Ne pas ajouter de styles actifs dans `frontend/src/App.css`.
  - Ne pas recreer de selecteurs `.astrologer-*`.
  - Ne pas conserver une carte featured full-width si elle reste seulement une
    carte compacte et non une vraie surface editoriale justifiee.
  - Ne pas masquer a nouveau tous les badges de choix sur `/astrologers`.
  - Ne pas contourner la specificite mobile par des hacks globaux non scopes.
  - Ne pas affaiblir `RG-079`, `RG-081`, `RG-084` ou `RG-087`.
  - Ne pas traiter les decisions CS-128 "featured full-width" et "badges
    caches" comme invariants durables; cette story les remplace par le nouveau
    contrat utilisateur.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story est une correction UX/UI page-scoped qui combine
  rendu React, cascade CSS, responsive runtime, guard design-system et preuves
  visuelles; aucun archetype API, route contract ou migration batch ne correspond
  exactement.
- Additional validation rules:
  - Le viewport `390x844` doit prouver une seule colonne catalogue, zero scroll
    horizontal et CTA carte visible.
  - Le viewport `1440x1000` doit prouver que la premiere carte ne cree plus une
    surface pleine largeur vide.
  - Le DOM doit prouver qu'une carte reste une action unique: aucun element
    interactif enfant n'est ajoute dans le bouton carte.
  - Les tests CS-128 qui imposent featured full-width ou badges caches doivent
    etre mis a jour, pas contournes.
  - Les tests doivent inclure un guard AST ou CSS dans
    `frontend/src/tests/design-system-guards.test.ts` contre le retour du
    featured span fragile, du mobile deux colonnes et de `mix-alend-mode`.
  - Les scans anti `App.css`, inline styles et `.astrologer-*` doivent rester
    zero-hit.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: grille catalogue, remplacement du prop `featured`, rendu des
    badges, libelles CTA, classes CSS locales `person-*`, tokens
    `--app-person-*`, tests visual-smoke et artefacts before/after.
  - Interdit: changement de route, changement d'API, changement de tri source
    hors rotation existante, fond global, `App.css`, style inline, selecteurs
    `.astrologer-*`, dependances nouvelles.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le produit demande de conserver une carte featured
  pleine largeur comme intention editoriale forte; dans ce cas la story doit
  transformer cette carte en layout horizontal complet avec preuve runtime, pas
  garder le span actuel habille.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La correction depend du rendu DOM/CSS de `/astrologers`, des viewports et de la navigation au clic. |
| Baseline Snapshot | yes | L'audit cite des dimensions desktop/mobile; la story doit comparer before/after. |
| Ownership Routing | yes | Les corrections doivent rester dans les owners astrologers/App primitives existants. |
| Allowlist Exception | no | Aucune exception large n'est autorisee; les guards existants doivent etre respectes. |
| Contract Shape | no | Aucun contrat API, DTO, schema ou client genere n'est modifie. |
| Batch Migration | no | La story traite une seule page catalogue, sans lot multi-domaines. |
| Reintroduction Guard | yes | Le retour du `span 2`, du mobile deux colonnes et du masquage complet des badges doit etre detecte. |
| Persistent Evidence | yes | Les captures, mesures et scans before/after doivent rester dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - rendu local de `/astrologers` via `AstrologersPage`, `AstrologerGrid` et
    `AstrologerCard`;
  - cascade effective de `frontend/src/styles/app/cards.css`,
    `frontend/src/styles/app/media.css` et `frontend/src/styles/app/tokens.css`;
  - tests Vitest/Testing Library de `AstrologersPage`;
  - AST guard/CSS guard charge par `frontend/src/tests/design-system-guards.test.ts`
    pour les selecteurs, declarations et destinations interdites;
  - visual smoke ou Playwright local sur viewports `390x844`, `768x1024` et
    `1440x1000`;
  - guards design-system pour `App.css`, styles inline, `.astrologer-*`,
    valeurs token-backed et fond global.
- Secondary evidence:
  - scans `rg` cibles sur `person-card--featured`, `.people-page .person-grid`,
    `mix-alend-mode`, `style=` et `.astrologer-`;
  - artefacts markdown before/after dans le dossier story.
- Static scans alone are not sufficient because:
  - la casse mobile vient de la specificite CSS runtime et la qualite de la
    grille depend des dimensions de viewport, du contenu variable et de la
    bottom nav.
- Runtime validation command:
  - `cd frontend; npm run test -- AstrologersPage design-system visual-smoke`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-after.md`
- Required baseline content:
  - viewport `1440x1000`: dimensions de `.person-grid`, premiere
    `.person-card`, presence ou absence de `.person-card--featured`,
    colonnes calculees et vide visuel constate;
  - viewport `390x844`: nombre de colonnes, largeur des cards, scroll
    horizontal, cards masquees par la bottom nav, textes/chips tronques;
  - viewport `768x1024`: nombre de colonnes et lisibilite intermediaire;
  - inventaire DOM des signaux visibles: provider type, default badge,
    featured badge ou specialite principale, CTA visuel;
  - scans CSS avant: `person-card--featured`, `.people-page .person-grid`,
    `display: none` des badges et `mix-alend-mode`.
- Expected invariant:
  - `/astrologers` affiche une grille egale et scannable, une seule colonne
    lisible sur mobile, des signaux de choix visibles et un CTA non imbrique.
- Allowed differences:
  - neutralisation de l'effet featured full-width; ajustement de densite,
    espacement, line clamp, tokens `--app-person-*`, libelle CTA localise et
    correction de texture CSS.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Page route, loading/error et navigation profil | `frontend/src/pages/AstrologersPage.tsx` | nouveau routeur, backend, `App.css` |
| Liste et decision featured | `frontend/src/features/astrologers/components/AstrologerGrid.tsx` | logique CSS implicite basee sur nth-child |
| Rendu carte, badges, CTA non imbrique | `frontend/src/features/astrologers/components/AstrologerCard.tsx` | bouton enfant, style inline, composant global |
| Libelles CTA et badges | `frontend/src/i18n/astrologers.ts` | texte hardcode non localise dans TSX |
| Grille, cartes et responsive catalogue | `frontend/src/styles/app/cards.css` | `frontend/src/App.css`, CSS landing, CSS profil |
| Texture/media visuelle catalogue | `frontend/src/styles/app/media.css` | pseudo-elements page-level concurrents hors owner |
| Tokens visuels catalogue | `frontend/src/styles/app/tokens.css` | literals disperses ou nouveaux prefixes non classes |
| Guards et smoke tests | `frontend/src/tests/visual-smoke.test.tsx`, `frontend/src/tests/design-system-guards.test.ts`, tests `AstrologersPage` | preuve manuelle seule |

Rules:

- Reutiliser les variables `--app-person-*`, `--app-people-*`,
  `--premium-*`, `--color-*`, `--space-*`, `--font-size-*` et `--line-height-*`
  existantes avant d'en creer de nouvelles.
- Toute nouvelle variable doit rester dans `tokens.css` avec un prefix owner
  coherent `--app-person-*` ou `--app-people-*`.
- Les changements TSX restent presentational; aucune logique metier ou appel
  API ne migre dans les composants.

## 4e. Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: cette story ne doit pas ajouter d'exception. Les corrections doivent
  satisfaire les guards existants sans wildcard, folder-wide allowlist ou
  residual actif non classe.

## 4f. Contract Shape

- Contract Shape: not applicable
- Reason: aucun contrat API, schema, route, payload, DTO, client genere ou type
  public partage n'est modifie; le type `Astrologer` existant est seulement lu.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: la story corrige une seule page catalogue et ses composants directs,
  sans migration multi-domaines.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline catalogue astrologues | `astrologers-catalog-before.md` | Captures, mesures, DOM visible et scans avant correction. |
| Preuve after catalogue astrologues | `astrologers-catalog-after.md` | Captures, mesures, tests, scans et differences autorisees apres correction. |

## 4i. Reintroduction Guard

- Guard target:
  - retour de `featured={index === 0}` si cela produit encore
    `.person-card--featured` pleine largeur;
  - retour de `.people-page .person-grid { grid-template-columns: repeat(2` sans
    override mobile plus specifique;
  - grille mobile `390px` en deux colonnes compressees;
  - badges provider/default tous caches sur `/astrologers`;
  - absence de CTA visuel dans `.person-card`;
  - hauteur fixe `height: 244px` ou `height: 256px` sur les cartes catalogue;
  - faute `mix-alend-mode`;
  - correction via `App.css`, style inline ou `.astrologer-*`.
  - tests gardant `toHaveClass("person-card--featured")` comme obligation de
    catalogue;
  - guards gardant `display: none` comme obligation pour tous les badges utiles.
- Forbidden examples:
  - `featured={index === 0}` sans carte editoriale horizontale testee;
  - `.people-page .person-card-provider-badge { display: none; }` applique a
    tous les badges utiles;
  - element `button` imbrique dans `.person-card`;
  - prop `style` dans `AstrologerCard.tsx` ou `AstrologerGrid.tsx`;
  - nouvelle classe `.astrologer-card` ou `.astrologer-grid`;
  - nouveau fond `.people-page` concurrent au fond global.
- Guard command/test:
  - `cd frontend; npm run test -- AstrologersPage design-system visual-smoke`
  - architecture guard: `frontend/src/tests/design-system-guards.test.ts`
    doit bloquer les selecteurs/declarations interdits afin que le span
    featured, l'override mobile deux colonnes et la typo CSS ne puissent pas
    etre reintroduced.
  - `cd frontend; npm run lint`
  - `rg -n "people-page|person-card" src/App.css`
  - `rg -n "astrologer-" src/styles/app src/features/astrologers`
  - `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers`
  - `rg -n "mix-alend-mode|height:\\s*24[0-9]px|height:\\s*25[0-9]px|featured=\\{index === 0\\}" src`

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: audit utilisateur du 2026-05-11, diagnostic et plan de mise
  en oeuvre pour `/astrologers`.
- Closure proof required: artefacts before/after, tests `AstrologersPage`,
  `visual-smoke`, `design-system`, scans anti `App.css`/inline/`.astrologer-*`,
  scan `mix-alend-mode`, captures desktop/mobile et verification de navigation
  vers `/astrologers/:id`; mise a jour explicite des assertions CS-128
  obsoletes sur featured full-width et badges caches.
- Known residual in-domain work: none
- Deferred non-domain concerns: mesure business reelle du taux de clic carte
  vers `/astrologers/:id` apres livraison; instrumentation analytique dediee
  hors scope si aucun event existant n'est disponible.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `frontend/src/pages/AstrologersPage.tsx` - la route charge les
  astrologues, applique la rotation locale et navigue vers
  `/astrologers/${id}` au clic.
- Evidence 2: `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
  - la premiere carte recoit `featured={index === 0}`, ce qui active le layout
  special.
- Evidence 3: `frontend/src/features/astrologers/components/AstrologerCard.tsx`
  - la carte est un element `button` unique avec badges provider/default/featured
  dans le DOM, specialites, bio et aria-label de profil.
- Evidence 4: `frontend/src/i18n/astrologers.ts` - les libelles provider,
  default, aria et profil existent deja; un libelle CTA visuel peut etre ajoute
  dans ce owner.
- Evidence 5: `frontend/src/styles/app/cards.css` - `.person-card--featured`
  force `grid-column: span 2`; `.people-page .person-grid` force deux colonnes;
  `.people-page .person-card` et `.people-page .person-card--featured` utilisent
  des hauteurs fixes `256px` et `244px`.
- Evidence 6: `frontend/src/styles/app/cards.css` - les badges
  `.person-card-provider-badge`, `.person-card-featured-badge` et
  `.person-default-badge` sont caches sous `.people-page`.
- Evidence 7: `frontend/src/styles/app/media.css` - `.people-page::after`
  contient `mix-alend-mode: multiply`, typo qui empeche l'effet CSS attendu.
- Evidence 8: `frontend/src/styles/app/tokens.css` - les tokens
  `--app-person-*`, `--app-people-*` et dark equivalents existent pour garder
  les corrections token-backed.
- Evidence 9: `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md`
  - la page `/astrologers` a deja un contrat anti `App.css`, anti inline styles
  et anti `.astrologer-*`.
- Evidence 10: `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md`
  - la largeur centrale non-admin est gouvernee par les tokens/layouts globaux
  et ne doit pas etre contournee par un override page-level non classe.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - invariants
  consultes avant cadrage; `RG-079`, `RG-081`, `RG-084` et `RG-087`
  s'appliquent directement.
- Evidence 12: `frontend/src/tests/visual-smoke.test.tsx` - des assertions
  actuelles verifient encore `person-card--featured` sur la premiere carte et
  doivent etre realignees sur le nouveau contrat.
- Evidence 13: `frontend/src/tests/design-system-guards.test.ts` - des guards
  actuels couvrent le material CS-128, dont les blocs featured/badges; ils
  doivent etre ajustes pour garder le relief sans imposer l'ancien layout.

## 6. Target State

After implementation:

- `/astrologers` utilise une grille responsive egale, de preference
  `repeat(auto-fit, minmax(min(100%, 280px), 1fr))`, avec largeur de contenu
  gouvernee par le layout existant.
- La premiere carte ne cree plus une surface pleine largeur vide; soit le
  featured layout est neutralise, soit il devient une vraie carte editoriale
  horizontale prouvee par captures et tests.
- Le viewport mobile `390x844` affiche une seule colonne lisible, sans scroll
  horizontal, sans texte casse incoherent et sans carte masquee par la bottom
  nav.
- Chaque carte affiche une action visuelle localisee, sans bouton imbrique,
  tout en gardant la carte entiere cliquable.
- Les signaux utiles IA/humain, astrologue par defaut et specialite principale
  sont visibles de facon sobre.
- Les cartes n'ont plus de hauteur fixe fragile; bio et specialites sont
  stabilisees par CSS.
- `mix-blend-mode` remplace la typo CSS visible et les guards design-system
  restent verts.
- Les assertions CS-128 conservees protegent la matiere visuelle; celles qui
  imposaient full-width featured ou badges caches sont remplacees par les
  nouveaux invariants de choix et conversion.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-079` - `/astrologers` doit conserver le relief visuel token-backed,
    rester hors `App.css` et ne pas recreer `.astrologer-*`.
  - `RG-081` - la largeur centrale non-admin doit rester gouvernee par les
    owners layout/tokens, pas par un override page-level opportuniste.
  - `RG-084` - la correction du catalogue ne doit pas creer de fond page-level
    concurrent au fond global canonique.
  - `RG-087` - la page ne doit pas destabiliser le fond viewport-fixed global.
  - `RG-058`, `RG-059`, `RG-060`, `RG-061`, `RG-078`, `RG-082` et `RG-083` -
    les corrections CSS doivent rester tokenisees, lisibles en dark mode, sans
    pollution `App.css`, fonts decoratives directes, vocabulaire No Legacy actif
    ou valeurs brutes non classees.
- Non-applicable invariants:
  - `RG-001` a `RG-057` - domaines backend/API/LLM/tests backend hors surface
    touchee.
  - `RG-062` a `RG-077` - pages, composants ou migrations frontend hors
    catalogue astrologues, sauf guards design-system globaux deja cites.
  - `RG-080` - la route `/astrologers/:id` n'est pas modifiee.
  - `RG-085`, `RG-086` et `RG-088` - fond dark astral, variante landing et
    complexite landing ne sont pas touches.
- Required regression evidence:
  - `npm run test -- AstrologersPage design-system visual-smoke`
  - `npm run lint`
  - captures/mesures before/after `390x844`, `768x1024`, `1440x1000`
  - scans zero-hit `people-page|person-card` dans `App.css`,
    `.astrologer-*`, `style=`, `mix-alend-mode` et retours de hauteur fixe.
- Allowed differences:
  - neutralisation du featured full-width, densite/espacement des cartes,
    affichage de badges utiles, ajout de CTA visuel, line clamp et correction
    texture; aucune difference de route, API, fond global ou profil detail.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Desktop: pas de carte pleine largeur vide. | Evidence profile: `baseline_before_after_diff`; `npm run test -- visual-smoke AstrologersPage` + capture. |
| AC2 | Mobile `390x844`: la grille rend une seule colonne. | Evidence profile: `runtime_contract`; `npm run test -- visual-smoke AstrologersPage` + capture. |
| AC3 | Mobile `390x844`: aucun scroll horizontal. | Evidence profile: `runtime_contract`; `npm run test -- visual-smoke AstrologersPage` + capture. |
| AC4 | Chaque carte affiche un CTA visuel localise. | Evidence profile: `frontend_accessibility`; `npm run test -- AstrologersPage` + scan inline/bouton. |
| AC5 | Les signaux de choix restent visibles. | Evidence profile: `dom_smoke`; `npm run test -- AstrologersPage` + capture before/after. |
| AC6 | Pas de hauteur fixe `244px/256px` sur les cartes. | Evidence profile: `reintroduction_guard`; `npm run test -- visual-smoke` + scan heights. |
| AC7 | Le clic carte navigue vers `/astrologers/:id`. | Evidence profile: `runtime_contract`; `npm run test -- AstrologersPage` avec assertion URL. |
| AC8 | La typo CSS `mix-alend-mode` est absente. | Evidence profile: `static_guard`; scan `rg -n "mix-alend-mode" frontend/src`. |
| AC9 | Les destinations interdites restent zero-hit. | Evidence profile: `design_system_guard`; `npm run test -- design-system` + scans. |
| AC10 | Les guardrails applicables restent satisfaits. | Evidence profile: `regression_guard`; `npm run test -- AstrologersPage design-system visual-smoke`. |
| AC11 | La bottom nav ne masque pas le CTA final. | Evidence profile: `runtime_contract`; `npm run test -- visual-smoke AstrologersPage` + capture. |
| AC12 | La carte ne contient aucun enfant interactif. | Evidence profile: `frontend_accessibility`; `npm run test -- AstrologersPage` + scan DOM. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline `/astrologers` (AC: AC1, AC2, AC3, AC5, AC6, AC8, AC9, AC11, AC12)
  - [ ] Subtask 1.1 - Lire les fichiers listes en section 18 et les stories
    `CS-128`, `CS-130`, `CS-137`, `CS-138` pertinentes pour les guardrails.
  - [ ] Subtask 1.2 - Creer `astrologers-catalog-before.md` avec mesures
    desktop/mobile/tablette, DOM visible, scans CSS et captures.
  - [ ] Subtask 1.3 - Identifier dans l'artefact si le featured full-width est
    neutralise ou transforme; la recommandation par defaut est alignement du
    layout sur les autres cartes.

- [ ] Task 2 - Corriger la grille et le responsive (AC: AC1, AC2, AC3, AC6, AC10, AC11)
  - [ ] Subtask 2.1 - Remplacer la grille catalogue par une formule responsive
    egale et token-backed dans `cards.css`.
  - [ ] Subtask 2.2 - Ajouter une regle mobile scoped `.people-page .person-grid`
    plus specifique que la regle desktop, sans override global.
  - [ ] Subtask 2.3 - Remplacer les hauteurs fixes des cartes catalogue au
    profit de `min-height`, contraintes de contenu et padding mobile stable.

- [ ] Task 3 - Neutraliser ou refondre le featured layout (AC: AC1, AC5, AC10)
  - [ ] Subtask 3.1 - Remplacer `featured={index === 0}` dans `AstrologerGrid.tsx`
    si aucune intention editoriale horizontale n'est implementee.
  - [ ] Subtask 3.2 - Nettoyer ou neutraliser les styles `.person-card--featured`
    qui creent le span pleine largeur sur `/astrologers`.
  - [ ] Subtask 3.3 - Conserver seulement un badge editorial sobre si utile au
    choix et prouve par le DOM, sans layout special fragile.

- [ ] Task 4 - Ajouter affordance et signaux de choix (AC: AC4, AC5, AC7, AC9, AC12)
  - [ ] Subtask 4.1 - Ajouter une cle i18n CTA visuel dans
    `i18n/astrologers.ts`.
  - [ ] Subtask 4.2 - Ajouter dans `AstrologerCard.tsx` un element `span` visuel
    d'action, pas un bouton enfant, et garder l'aria-label existant.
  - [ ] Subtask 4.3 - Rendre visibles les badges provider/default et une meta de
    specialite principale avec styles sobres et token-backed.
  - [ ] Subtask 4.4 - Verifier que le clic carte navigue toujours vers
    `/astrologers/:id`.

- [ ] Task 5 - Corriger la dette CSS visible (AC: AC8, AC9, AC10)
  - [ ] Subtask 5.1 - Remplacer `mix-alend-mode` par `mix-blend-mode` dans
    `media.css`.
  - [ ] Subtask 5.2 - Scanner les typos CSS directement voisines seulement si
    elles bloquent les tests; ne pas lancer de refactor global de `media.css`.
  - [ ] Subtask 5.3 - Verifier les scans interdits `App.css`, `.astrologer-*`,
    `style=` et heights fixes.

- [ ] Task 6 - Ajouter tests et preuves after (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [ ] Subtask 6.1 - Adapter `AstrologersPage` tests pour CTA visible, badges
    utiles, navigation et absence de bouton imbrique.
  - [ ] Subtask 6.2 - Adapter `visual-smoke.test.tsx` pour dimensions
    desktop/mobile, une colonne mobile, absence de scroll horizontal et contenu
    non masque.
  - [ ] Subtask 6.3 - Adapter `design-system-guards.test.ts` pour bloquer le
    retour du span featured fragile, du mobile deux colonnes, de la typo CSS et
    des destinations interdites.
  - [ ] Subtask 6.4 - Remplacer les assertions CS-128 obsoletes par les
    invariants CS-148 sans affaiblir le relief visuel.
  - [ ] Subtask 6.5 - Creer `astrologers-catalog-after.md` avec captures,
    mesures, tests executes, scans et differences autorisees.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstrologersPage.tsx` pour loading/error et navigation profile.
  - `AstrologerGrid.tsx` comme seul owner de la liste rendue.
  - `AstrologerCard.tsx` comme seul owner du rendu carte catalogue.
  - `tAstrologers` pour tout libelle visible ajoute.
  - `cards.css`, `media.css` et `tokens.css` comme owners CSS App deja actifs.
  - tokens `--app-person-*`, `--app-people-*`, `--premium-*`, `--color-*`,
    `--space-*`, `--font-size-*` existants.
- Do not recreate:
  - nouveau composant carte concurrent;
  - nouvelle grille globale;
  - styles dans `App.css`;
  - texte CTA hardcode directement en TSX;
  - nouvelle logique de tri ou rotation;
  - event analytics ad hoc non demande;
  - parser CSS ou librairie de layout.
- Shared abstraction allowed only if:
  - elle remplace une duplication prouvee entre `AstrologerCard` et un owner
    astrologers existant, reste dans `frontend/src/features/astrologers`, et
    dispose d'un test cible.

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

- `frontend/src/App.css` comme destination de fix catalogue
- `style=` dans `frontend/src/pages/AstrologersPage.tsx` ou
  `frontend/src/features/astrologers`
- `.astrologer-*` dans `frontend/src/styles/app` ou
  `frontend/src/features/astrologers`
- `featured={index === 0}` si cela preserve le layout pleine largeur actuel
- `.people-page .person-grid` deux colonnes sans override mobile specifique
- `height: 244px` ou `height: 256px` pour les cartes catalogue
- `mix-alend-mode`
- bouton interactif imbrique dans `.person-card`
- `PASS with limitation`, `TODO`, `fallback`, `compatibility`, `legacy`,
  `migration-only`, `shim`, `alias` comme justification d'un residuel actif

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Route catalogue et navigation profil | `frontend/src/pages/AstrologersPage.tsx` | backend, route profil, `App.css` |
| Grille catalogue | `frontend/src/features/astrologers/components/AstrologerGrid.tsx` + `cards.css` | nth-child global, layout page global |
| Carte catalogue | `frontend/src/features/astrologers/components/AstrologerCard.tsx` + `cards.css` | composant duplique, bouton enfant, inline style |
| Tokens carte/catalogue | `frontend/src/styles/app/tokens.css` | literals disperses, nouveaux prefixes non classes |
| Texture catalogue | `frontend/src/styles/app/media.css` | fond global concurrent, pseudo-element hors owner |
| Preuves de livraison | `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/**` | sortie console non persistante |

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

- `frontend/src/pages/AstrologersPage.tsx`
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/features/astrologers/index.ts`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- tests existants `AstrologersPage` ou tests route/page qui couvrent
  `/astrologers`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md`
- `_condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md`
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md`
- `_condamad/stories/CS-137-converger-dark-mode-surfaces-frontend/00-story.md`
- `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/00-story.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/features/astrologers/components/AstrologerGrid.tsx` - remplacer
  ou encadrer le featured layout base sur `index === 0`.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - ajouter
  CTA visuel non interactif, meta utile et rendu sobre des signaux.
- `frontend/src/i18n/astrologers.ts` - ajouter les libelles CTA/meta necessaires.
- `frontend/src/styles/app/cards.css` - grille responsive, mobile scoped,
  suppression des hauteurs fixes, badges visibles, CTA, line clamp.
- `frontend/src/styles/app/tokens.css` - ajouter uniquement les tokens
  `--app-person-*` ou `--app-people-*` manquants et justifies.
- `frontend/src/styles/app/media.css` - corriger `mix-alend-mode` et seulement
  les effets media directement lies.
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-before.md` - baseline.
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-after.md` - preuve after.

Likely tests:

- `frontend/src/tests/visual-smoke.test.tsx` - grille desktop/mobile, scroll
  horizontal, bottom nav, contenu variable et retrait des assertions
  full-width obsoletes.
- `frontend/src/tests/design-system-guards.test.ts` - guards anti `App.css`,
  `.astrologer-*`, typo CSS, heights fixes, featured fragile et badges caches
  obsoletes.
- test `AstrologersPage` existant ou nouveau sous `frontend/src/tests` -
  CTA visible, badges utiles, navigation au clic et absence de bouton imbrique.

Files not expected to change:

- `frontend/src/App.css` - destination interdite par `RG-079` et `RG-078`.
- `frontend/src/pages/AstrologerProfilePage.tsx` - route profil hors scope.
- `frontend/src/pages/AstrologerProfilePage.css` - route profil hors scope.
- `frontend/src/layouts/RootLayout.tsx` - fond global hors scope.
- `frontend/src/layouts/PageLayout.css` - largeur globale hors scope; une
  regression de largeur doit bloquer la story au lieu d'etre corrigee ici.
- `backend/**` - aucun changement backend attendu.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- New runtime dependencies: forbidden.
- New dev dependencies: forbidden.
- Python commands: if story validation scripts are run, activate the venv first:
  `.\.venv\Scripts\Activate.ps1`.
- Frontend commands: run from `frontend/` with npm scripts already present.

## 21. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run lint
npm run test -- AstrologersPage design-system visual-smoke
rg -n "people-page|person-card" src/App.css
rg -n "astrologer-" src/styles/app src/features/astrologers
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
rg -n "mix-alend-mode|featured=\\{index === 0\\}|height:\\s*24[0-9]px|height:\\s*25[0-9]px" src
rg -n "toHaveClass\\(\"person-card--featured\"\\)|badges stay hidden" src/tests/visual-smoke.test.tsx src/tests/design-system-guards.test.ts
rg -n "Provider default featured badges stay hidden" src/tests/visual-smoke.test.tsx src/tests/design-system-guards.test.ts
```

Required runtime/manual evidence:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Then capture or script checks for:

- viewport `390x844`: one column, no horizontal scroll, CTA visible, provider
  or human/AI signal visible, default signal visible when applicable, bottom nav
  does not hide actionable content;
- viewport `768x1024`: grid remains readable and cards do not collapse;
- viewport `1440x1000`: no broken full-width first card, grid cards scan
  evenly, no excessive empty card area;
- click on any card navigates to `/astrologers/:id`;
- dark mode: readable badges/CTA and no background regression.
- tests CS-128 realignes: aucune assertion restante n'impose featured
  full-width ou badges caches comme comportement catalogue attendu.

Story contract validation after drafting or editing this story:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/00-story.md
```

## 22. Regression Risks

- Risk: neutraliser le featured affaiblit un signal produit introduit par CS-128.
  - Guardrail: AC1/AC5 exigent de conserver les signaux utiles sans layout
    pleine largeur vide.
- Risk: corriger le mobile casse la densite tablette ou desktop.
  - Guardrail: captures `390x844`, `768x1024` et `1440x1000` obligatoires.
- Risk: afficher les badges surcharge les petites cartes.
  - Guardrail: AC5 impose une meta compacte et sobre, avec visual-smoke.
- Risk: ajouter un CTA dans une carte bouton cree une interaction imbriquee.
  - Guardrail: AC4 impose un element `span` visuel et scan/test anti bouton imbrique.
- Risk: les fixes CSS polluent `App.css` ou le fond global.
  - Guardrail: `RG-079`, `RG-081`, `RG-084`, `RG-087` et scans zero-hit.
- Risk: les hauteurs dynamiques creent des cards trop irregulieres.
  - Guardrail: min-height, line clamp et visual-smoke avec contenu long.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.
- Commencer par l'artefact before avec mesures runtime et scans.
- Appliquer la priorite du plan: responsive mobile, grille desktop, affordance
  visible, signaux de choix, hauteur robuste, dette CSS.
- La recommandation d'implementation est de neutraliser le span featured desktop
  et de passer a des cartes egales; ne conserver featured que si une vraie carte
  editoriale horizontale est implementee et prouvee.
- Respecter les instructions projet: aucun style inline; tout CSS dans le
  fichier approprie; reutiliser les variables existantes avant d'en creer.

## 24. References

- Diagnostic utilisateur du 2026-05-11 - probleme structurel et plan de
  correction `/astrologers`.
- `frontend/src/pages/AstrologersPage.tsx` - owner route catalogue.
- `frontend/src/features/astrologers/components/AstrologerGrid.tsx` - owner
  liste et featured actuel.
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` - owner
  carte, badges, CTA et action.
- `frontend/src/i18n/astrologers.ts` - owner libelles localises.
- `frontend/src/styles/app/cards.css` - owner grille/cartes catalogue.
- `frontend/src/styles/app/media.css` - owner texture et media visuels.
- `frontend/src/styles/app/tokens.css` - owner tokens App/person.
- `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` -
  relief visuel et interdits App.css/inline/`.astrologer-*`.
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md`
  - largeur centrale non-admin.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
