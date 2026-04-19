# Story 70.11: Elargir le layout Admin et retablir les contrastes light/dark

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want que la surface `/admin` exploite une largeur desktop beaucoup plus genereuse et que les couleurs d encre suivent correctement les themes light/dark,
so that les pages admin restent lisibles sur grand ecran, sans colonnes inutilement ecrasees ni textes insuffisamment contrastes selon le fond.

## Acceptance Criteria

1. Etant donne qu un admin consulte une page `/admin/*` sur desktop large, quand la page est rendue, alors le shell admin n est plus borne par un `max-width` trop restrictif, conserve des marges laterales de securite, et laisse les surfaces denses exploiter au maximum la largeur disponible de la fenetre.
2. Etant donne qu un admin consulte `/admin/prompts/*`, quand le catalogue master-detail, la route legacy, la route release ou la route consumption sont affiches, alors les colonnes, tableaux, panneaux sticky et zones d action beneficient de cet elargissement sans regression responsive ni scroll horizontal inutile introduit par le nouveau layout.
3. Etant donne que le theme bascule entre `light` et `dark`, quand les surfaces admin sont affichees, alors les textes, labels, aides, badges et etats de premier rang utilisent des tokens d encre/surface adaptes au fond courant, sans reliquat de couleurs figees qui deviennent trop pales, trop sombres ou incoherentes apres le switch.
4. Etant donne qu une surface admin utilise des fonds translucides, melanges ou semantiques (`glass`, panneau d erreur, warning, succes, detail, toolbar), quand elle est affichee en `light` puis en `dark`, alors les contrastes restent lisibles et homogenes pour les contenus principaux et secondaires, avec reutilisation des tokens existants avant toute creation de nouveaux tokens.
5. Etant donne la couverture frontend existante, quand la story est livree, alors les tests verifient au minimum le debridage du layout admin, la non-regression des surfaces `prompts`, et l existence/usage de tokens de theme explicites pour les encres critiques en `light` et `dark`.

## Tasks / Subtasks

- [x] Debrider le shell de layout admin sur desktop (AC: 1, 2, 5)
  - [x] Remplacer la borne fixe actuelle du conteneur admin par une largeur max beaucoup plus haute ou un systeme de largeur adaptative dedie au domaine admin
  - [x] Preserver des gouttieres lisibles et le comportement de la sidebar sur desktop, laptop compact et mobile
  - [x] Verifier que les pages admin hors prompts profitent aussi du shell elargi sans casser leur composition
- [x] Recalibrer les surfaces `/admin/prompts/*` pour la largeur disponible (AC: 2, 5)
  - [x] Ajuster si necessaire les grilles `catalog/master-detail`, `legacy`, `release` et `consumption` pour profiter du nouveau shell sans duplication CSS
  - [x] Eviter d empiler artificiellement des panneaux desktop qui peuvent rester cote a cote sur large fenetre
  - [x] Conserver les replis responsive deja livres par 70.8 a partir des breakpoints existants
- [x] Retablir une doctrine de contraste light/dark sur les surfaces admin (AC: 3, 4, 5)
  - [x] Identifier les classes admin qui utilisent encore des couleurs ou opacites figees non alignees sur `design-tokens.css` et `theme.css`
  - [x] Remapper les encres principales/secondaires et les surfaces semantiques vers des tokens adaptatifs plutot que des valeurs durcies
  - [x] Traiter prioritairement les zones de lecture dense, les meta strips, les panneaux de diff, les toolbars, les etats d erreur/succes et les liens de navigation admin
- [x] Verrouiller les tests et garde-fous de non-regression (AC: 1, 2, 3, 4, 5)
  - [x] Etendre les tests de shell admin/layout
  - [x] Etendre les tests `AdminPromptsPage` et/ou les tests CSS contractuels sur la largeur et les tokens de contraste
  - [x] Ajouter au moins un test de presence ou d usage des tokens light/dark critiques pour eviter une reintroduction de couleurs d encre figees

## Dev Notes

- Le principal goulot d etranglement de largeur se situe aujourd hui dans le shell admin: `.admin-container` est encore borne a `max-width: 1200px`, ce qui comprime inutilement les surfaces denses alors que `admin-main` occupe deja tout l espace disponible autour de la sidebar. La story doit partir de ce seam reel plutot que bricoler uniquement les pages enfants. [Source: C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.css]
- Le shell `/admin` est centralise dans `AdminPage.tsx` + `AdminLayout.tsx`; toute correction de largeur ou de contraste doit donc privilegier ce niveau shared avant d empiler des overrides page par page. [Source: C:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx, C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx]
- Les themes sont deja pilotes globalement par `ThemeProvider`, qui pose ou retire la classe `.dark` sur `document.documentElement`. La story ne doit pas reinventer un deuxieme mecanisme de theme; elle doit rendre les styles admin compatibles avec ce mecanisme existant. [Source: C:/dev/horoscope_front/frontend/src/state/ThemeProvider.tsx]
- Les tokens semantiques existent deja dans `design-tokens.css` et sont relayes dans `theme.css` (`--color-text-*`, `--glass-*`, `--color-bg-*`, `--success`, `--error`, etc.). Le probleme actuel vient surtout du melange entre ces tokens et des surfaces/couleurs semi-fixees (`rgba(...)`, `#...`, `color-mix(...)`) qui ne suivent pas toujours correctement le fond du theme courant. [Source: C:/dev/horoscope_front/frontend/src/styles/design-tokens.css, C:/dev/horoscope_front/frontend/src/styles/theme.css]
- `AdminPromptsPage.css` contient deja plusieurs panneaux translucides, diff, meta strips, toolbars, tableaux et banners avec des fonds derives de `rgba(...)` ou de `color-mix(...)`. `70.11` doit prioriser ces zones a forte densite de lecture, pas seulement les titres ou le shell global. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Les stories 70.8, 70.9 et 70.10 ont deja consolide respectivement le responsive, l edition admin et l historique des versions. `70.11` est une passe transversale de lisibilite et de shell; elle ne doit pas reouvrir les contrats metier de versioning ou de routing deja poses. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-9-editer-les-prompts-canoniques-via-des-formulaires-admin-guides.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-10-historiser-comparer-et-auditer-chaque-sauvegarde-de-prompt.md]

### Technical Requirements

- Corriger d abord le shell `AdminLayout` avant de multiplier les exceptions dans les pages.
- Introduire si necessaire un token dedie de largeur admin dans la couche de styles partagee, plutot qu un nouveau `max-width` magique disperse dans plusieurs fichiers.
- Les encres admin doivent etre derivees des tokens de texte et/ou de nouveaux tokens semantiques clairement relies aux themes `light` et `dark`.
- Toute couleur ou opacite figee conservee doit etre justifiee par un vrai besoin visuel et rester lisible dans les deux themes.
- Les surfaces admin critiques a revalider explicitement sont:
  - sidebar et header de retour du shell admin
  - catalogue et detail sticky de `/admin/prompts/catalog`
  - timeline et diff de `/admin/prompts/release`
  - historique, diff et meta strips de `/admin/prompts/legacy`
  - toolbar, tableaux et cartes mobiles de `/admin/prompts/consumption`

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript du monorepo et la centralisation des styles dans les fichiers CSS existants. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: aucun style inline, petit delta coherent, reutilisation des variables/couleurs existantes avant creation, pas de refactor massif hors perimetre. [Source: C:/dev/horoscope_front/AGENTS.md]
- Preserver les comportements responsive et accessibilite deja poses par 70.8; cette story doit elargir et clarifier, pas casser les replis existants. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise.
- Reutiliser la stack frontend existante:
  - React 19.2
  - `react-router-dom` 6.30
  - `@tanstack/react-query` 5.90
  - Vitest 4 pour les garde-fous frontend
- Ne pas introduire de systeme de theming tiers; conserver `ThemeProvider` + tokens CSS comme source de verite. [Source: C:/dev/horoscope_front/frontend/package.json, C:/dev/horoscope_front/frontend/src/state/ThemeProvider.tsx]

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.css`
  - `C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/styles/design-tokens.css`
  - `C:/dev/horoscope_front/frontend/src/styles/theme.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPage.test.tsx`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
  - `C:/dev/horoscope_front/frontend/src/tests/theme-tokens.test.ts`
- Fichiers potentiellement touches selon implementation:
  - autres pages admin si certaines surfaces locales utilisent encore des encres figees
  - tests CSS contractuels existants (`AppBgStyles.test.ts`, `visual-smoke.test.tsx`) si de nouveaux tokens admin sont introduits
- Eviter de disperser la logique dans `App.css` si le probleme concerne clairement le domaine admin et ses styles dedies.

### Testing Requirements

- Frontend:
  - test de shell admin confirmant que le layout n est plus borne a `1200px` ou a une valeur equivalent trop basse
  - test de non-regression `AdminPromptsPage` sur le rendu du master-detail et/ou des surfaces denses apres elargissement
  - test CSS contractuel sur les tokens de contraste admin light/dark si de nouveaux tokens sont crees
  - test confirmant que les themes `light` et `dark` conservent des valeurs distinctes et explicites pour les encres admin critiques
- Reutiliser les harness existants (`AdminPage.test.tsx`, `AdminPromptsPage.test.tsx`, `ThemeProvider.test.tsx`, `AppBgStyles.test.ts`) plutot que construire une nouvelle pile de tests parallele.

### Previous Story Intelligence

- `70.8` a deja traite la lisibilite responsive et l accessibilite de `/admin/prompts/*`; `70.11` doit capitaliser sur ce socle et corriger le shell trop etroit qui empeche d en tirer pleinement parti.
- `70.9` a ajoute un formulaire guide dans la surface legacy; ce panneau et son resume de changements font partie des zones a retester apres elargissement et recalibrage des encres.
- `70.10` a enrichi l historique, les meta strips et les feedbacks de version; ces nouveaux blocs ont augmente la densite visuelle et rendent le sujet de contraste encore plus sensible.

### Implementation Guardrails

- Ne pas regler le probleme de largeur par une cascade de `width: 100vw` fragile ou par suppression aveugle des marges de securite.
- Ne pas introduire des couleurs de texte figees directement dans les composants TSX.
- Ne pas casser la compatibilite mobile pour privilegier uniquement le desktop large.
- Ne pas dupliquer une palette admin parallele non reliee aux tokens semantiques globaux.
- Si certains panneaux conservent des fonds translucides specifiques, ajuster aussi l encre associee; ne pas supposer que `var(--color-text-primary)` suffit partout sans verification.

### UX Requirements

- Sur desktop large, l operateur doit voir davantage d information utile sans devoir ouvrir autant de replis ou scroller horizontalement.
- Le shell admin doit respirer, mais rester cadre: pleine largeur utile avec gouttieres, pas pleine largeur brute bord a bord.
- Le passage `light` -> `dark` ne doit plus creer d ambiguite sur ce qui est lecture principale, lecture secondaire, etat critique ou action.
- Les surfaces admin doivent conserver un niveau de contraste compatible avec une lecture de travail prolongee, en particulier dans les tableaux, diffs et meta informations.

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend, centree sur le shell admin, les styles admin prompts et les tokens de theme.

### References

- Shell admin actuel: [Source: C:/dev/horoscope_front/frontend/src/pages/AdminPage.tsx]
- Layout admin actuel: [Source: C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.tsx]
- Styles du layout admin: [Source: C:/dev/horoscope_front/frontend/src/layouts/AdminLayout.css]
- Surface admin prompts actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Styles admin prompts actuels: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Theme provider: [Source: C:/dev/horoscope_front/frontend/src/state/ThemeProvider.tsx]
- Tokens globaux: [Source: C:/dev/horoscope_front/frontend/src/styles/design-tokens.css]
- Tokens theme: [Source: C:/dev/horoscope_front/frontend/src/styles/theme.css]
- Tests admin existants: [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPage.test.tsx, C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx, C:/dev/horoscope_front/frontend/src/tests/AppBgStyles.test.ts]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `af433138 fix(admin-prompts): close story 70-10 residual risks`
  - `66928853 feat(admin-prompts): complete story 70.9`
  - `7f6a11b3 fix(admin-prompts): finalize story 70.8 review follow-ups`
  - `2ff7f718 test(admin-prompts): close residual coverage risk on consumption`
  - `f2b5dd79 feat(admin-prompts): story 70.7 — route consommation pilotable et artefacts BMAD`
- Constat codebase avant creation:
  - `.admin-container` borne encore le shell admin a `1200px`
  - `ThemeProvider` pilote uniquement la classe `.dark` globale
  - les tokens de texte/surfaces existent deja, mais plusieurs panneaux admin reposent encore sur des melanges `rgba(...)`/`color-mix(...)` qui degradent la lisibilite selon le theme
  - les tests admin et theme existent deja et peuvent etre etendus sans nouveau harness
- Validation implementation:
  - `npm run test -- --run src/tests/AdminPage.test.tsx src/tests/AdminPromptsPage.test.tsx src/tests/theme-tokens.test.ts`
  - `npm run lint`

### Completion Notes List

- Story creee a partir du besoin utilisateur de lisibilite admin: largeur desktop insuffisante et contrastes light/dark incoherents.
- Le cadrage privilegie une correction au niveau du shell `AdminLayout` puis des surfaces admin prompts les plus denses, afin d eviter des patches disperses page par page.
- Le principal garde-fou ajoute est d interdire toute palette admin parallele et de rebrancher les encres sur les tokens de theme existants ou sur un petit nombre de tokens admin explicites.
- Le shell admin utilise maintenant un token de largeur dedie (`--layout-admin-max-width`) et des gouttieres adaptatives pour exploiter davantage la largeur desktop sans passer en edge-to-edge.
- Les surfaces critiques de `/admin/prompts/*` ont ete remappees sur des tokens admin light/dark explicites pour les encres, surfaces info et surfaces danger, en supprimant les fonds fixes les plus fragiles.
- Les tests frontend verrouillent maintenant le debridage du shell admin, la grille desktop du master-detail prompts et la presence de tokens admin distincts entre `light` et `dark`.
- La passe de code review a ferme les reliquats restants sur le bandeau `resolved`, les disclosures associes, les panneaux `legacy` d edition et leurs resumes, afin d eliminer les derniers fonds figes qui cassaient encore le theme clair.
- Verification navigateur sur `http://localhost:5173/admin/` avec le compte admin fourni: le verrou principal de largeur etait en realite dans `AppLayout`, via `app-bg-container`, et non uniquement dans `.admin-container`.
- Une classe de shell admin large a ete ajoutee au layout applicatif pour desserrer `/admin/*` sans impacter les autres pages, puis les surfaces admin light ont ete eclaircies pour supprimer le grand panneau sombre encore visible en mode day.

### File List

- _bmad-output/implementation-artifacts/70-11-elargir-le-layout-admin-et-retablir-les-contrastes-light-dark.md
- frontend/src/styles/design-tokens.css
- frontend/src/layouts/AdminLayout.css
- frontend/src/layouts/AppLayout.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/styles/backgrounds.css
- frontend/src/tests/AdminPage.test.tsx
- frontend/src/tests/AdminPromptsPage.test.tsx
- frontend/src/tests/theme-tokens.test.ts
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-04-19 : creation de la story 70.11 pour elargir le shell admin et retablir les contrastes d encre light/dark sur les surfaces admin.
- 2026-04-19 : implementation de la story 70.11 avec elargissement du shell admin, remapping des surfaces/encres admin prompts et ajout des garde-fous Vitest associes.
- 2026-04-19 : cloture des findings de review sur `resolved` et `legacy`, avec revalidation frontend et passage de la story en `done`.
- 2026-04-19 : seconde passe sur constat navigateur reel pour lever la borne `app-bg-container` sur `/admin/*` et eclaircir le rendu day du shell admin.
