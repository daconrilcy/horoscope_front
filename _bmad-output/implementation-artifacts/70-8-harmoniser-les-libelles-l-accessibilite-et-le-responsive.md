# Story 70.8: Harmoniser les libelles, l accessibilite et le responsive

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want une surface `/admin/prompts/*` coherente en francais, accessible au clavier et exploitable sur largeur contrainte,
so that je puisse administrer les prompts sans ambiguite de libelles, sans blocage d accessibilite et sans rupture de lecture sur mobile ou laptop compact.

## Acceptance Criteria

1. Etant donne que l admin navigue sur `catalog`, `legacy`, `release`, `consumption`, `personas` et `sample_payloads`, quand la story est livree, alors tous les libelles visibles, aides contextuelles, CTA et statuts de premier niveau sont harmonises en francais produit coherent, sans reliquat de wording anglais ou d intitulés techniques ambigus.
2. Etant donne que l admin utilise la navigation clavier ou un lecteur d ecran, quand il parcourt `/admin/prompts/*`, alors les controles critiques, la sous-navigation locale, les sections majeures, les tableaux interactifs, les disclosures et les dialogues ont une semantique explicite, des labels compréhensibles et des etats focus visibles sans regression sur les stories 70.1 a 70.7.
3. Etant donne que l interface est ouverte sur largeur contrainte ou mobile, quand une surface dense est affichee, alors le catalogue, le detail, les routes secondaires et les blocs d investigation se replient proprement sans scroll horizontal subi, sans perte d informations critiques ni d actions operateur.
4. Etant donne les etats `loading`, `error`, `empty`, `preview partielle`, `runtime incomplete` et `execution en cours`, quand ils sont affiches sur `/admin/prompts/*`, alors ils sont compréhensibles en francais metier, visibles au bon endroit et ne demandent pas la lecture de JSON brut pour comprendre la situation.
5. Etant donne la couverture frontend existante, quand la story est livree, alors les tests Vitest valident au minimum l harmonisation de wording cle, les attributs/accessibilite critiques et les replis responsive principaux sans casser les routes et composants deja consolides en 70.1 a 70.7.

## Tasks / Subtasks

- [x] Harmoniser les libelles et microcopies de la surface admin prompts (AC: 1, 4)
  - [x] Recenser les reliquats FR/EN et intitulés techniques encore visibles dans `AdminPromptsPage.tsx`
  - [x] Stabiliser un vocabulaire metier commun pour le catalogue, le detail, la release, la legacy, la consommation et les etats d inspection
  - [x] Centraliser les libelles repetes dans les fichiers i18n admin existants plutot que laisser des chaines inline dispersées
- [x] Fiabiliser l accessibilite clavier et lecteur d ecran (AC: 2, 5)
  - [x] Verifier les labels visibles et/ou `aria-*` des filtres, selects, disclosures, tableaux interactifs, sections et dialogues
  - [x] Renforcer les etats `focus-visible`, l ordre de tabulation et les annonces utiles sans transformer la sous-navigation route-aware en pseudo-tabs incomplets
  - [x] Ne garder un pattern `tablist/tab/tabpanel` que s il est complet; sinon assumer un vrai pattern de navigation avec `nav`, `link` et `aria-current`
- [x] Consolider le responsive des surfaces denses (AC: 3, 5)
  - [x] Verifier le repli master-detail du catalogue, les zones resolved, les panneaux release/legacy et la surface consumption sur les largeurs critiques deja ciblees en CSS
  - [x] Eliminer les debordements evitables et les zones de scroll horizontal subi
  - [x] Preserver les actions operateur et la lisibilite des etats dans les modes replis
- [x] Verrouiller les etats de premier rang et la non-regression (AC: 4, 5)
  - [x] Revoir les messages `loading/error/empty` et les etats incomplets pour les rendre coherents et localises
  - [x] Etendre les tests Vitest sur le wording cle, les attributs d accessibilite et les replis responsive existants
  - [x] Verifier que les stories 70.1 a 70.7 restent stables apres la passe de finition transverse

## Dev Notes

- `70.8` est une story de finition transverse. Les routes dediees, le master-detail catalogue, la zone d actions, le schema React Flow, la route `legacy`, la route `release` et la route `consumption` existent deja; cette story ne doit pas re-ouvrir leur architecture, seulement harmoniser la surface finale. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-7-refondre-la-route-consumption-pour-le-pilotage-operable.md]
- Le code actuel laisse encore des libelles mixtes ou trop techniques dans le catalogue et le detail, par exemple `Source of truth`, `Release health`, `Execution profile`, `Output contract`, `Visibility`, ou encore des raccourcis de mode d inspection peu pedagogiques. La story doit les stabiliser en francais metier coherent sans casser les identifiants techniques internes. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- La sous-navigation locale sous `/admin/prompts/*` est aujourd hui une vraie navigation `nav` + `NavLink`, pas un vrai systeme d onglets ARIA complets. Le developer ne doit pas introduire un hybride fragile: soit la navigation reste une navigation route-aware bien etiquee, soit elle devient un vrai `tablist/tab/tabpanel` complet. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- La CSS contient deja un socle responsive significatif (`catalog-master-detail`, replis `@media`, cartes mobiles consumption, focus-visible sur plusieurs elements). `70.8` doit completer et homogeniser ce socle, pas le remplacer par une nouvelle couche parallele. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Les routes `legacy` et `consumption` ont deja introduit des fichiers i18n dedies. `70.8` doit s inscrire dans cette direction et eviter de re-disperser des chaines visibles directement dans le JSX. [Source: C:/dev/horoscope_front/frontend/src/i18n/admin.ts, C:/dev/horoscope_front/frontend/src/i18n/adminPromptsLegacy.ts, C:/dev/horoscope_front/frontend/src/i18n/adminPromptsConsumption.ts]

### Technical Requirements

- Ne pas modifier les contrats backend, les hooks React Query ni les parametres de routing des routes `/admin/prompts/*`.
- Conserver le comportement etabli par les stories 70.1 a 70.7 sur:
  - le routage dedie
  - la selection catalogue/detail
  - le detail resolved et ses actions
  - le schema React Flow
  - les flows `legacy`, `release` et `consumption`
- Si des libelles doivent etre derives d un statut technique (`source_of_truth_status`, `catalog_visibility_status`, etc.), garder la valeur brute pour la logique et mapper seulement l affichage utilisateur.
- Les messages d etat doivent rester explicites et de premier rang sur toutes les routes admin prompts: `loading`, `error`, `empty`, preview partielle, runtime incomplet, execution en cours.

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript du monorepo et la separation existante entre hooks/data-fetching et presentation. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: aucun style inline, reutilisation des variables et classes CSS existantes avant creation de nouveaux styles, petit delta coherent, tests mis a jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Conserver des etats `loading/error/empty` explicites et coherents, conformes au cadre UX. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut pour cette story.
- Reutiliser en priorite:
  - `react-router-dom` pour la sous-navigation route-aware
  - les styles CSS admin prompts deja en place
  - l infrastructure i18n admin existante
- Ne pas introduire une solution accessibilite/responsive tierce lourde pour une passe de finition qui peut etre resolue dans le code actuel.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/i18n/admin.ts`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement a creer si la centralisation des chaines le justifie vraiment:
  - `C:/dev/horoscope_front/frontend/src/i18n/adminPromptsCatalog.ts`
  - `C:/dev/horoscope_front/frontend/src/i18n/adminPromptsRelease.ts`
- Rester dans le domaine `frontend/src/pages/admin/` et `frontend/src/i18n/`.

### Testing Requirements

- Etendre les tests Vitest pour verifier au minimum:
  - la presence des libelles FR harmonises sur les surfaces critiques
  - la semantique/annonces de la sous-navigation locale et des sections critiques
  - la presence d etats focus/accessibilite sur les elements interactifs les plus sensibles
  - le repli responsive d au moins un cas catalogue/detail et un cas route secondaire deja denses
  - la non-regression des routes `legacy`, `release` et `consumption`
- Reutiliser les patterns de tests deja etablis dans `AdminPromptsPage.test.tsx` plutot que reconstruire un harness parallele.

### Previous Story Intelligence

- `70.1` a deja separe `legacy`, `release` et `consumption` en routes dediees: `70.8` ne doit pas recompactifier ces surfaces dans un ecran unique.
- `70.2` et `70.3` ont pose la hierarchie catalogue/detail et la separation lecture/actions: toute harmonisation de wording ou responsive doit preserver cette structure.
- `70.4` a introduit React Flow avec un fallback; `70.8` doit seulement s assurer que le rendu et ses textes restent lisibles et accessibles dans les largeurs contraintes.
- `70.5` et `70.7` ont deja investit dans l i18n FR/EN/ES. La story doit prolonger cette approche plutot que la contourner avec de nouvelles chaines inline.

### Implementation Guardrails

- Ne pas confondre harmonisation de surface et refonte fonctionnelle supplementaire.
- Ne pas traduire en dur des identifiants techniques servant aux requetes, aux comparaisons ou aux cles de tri; ne traduire que la presentation.
- Ne pas introduire un pattern ARIA incomplet pour la sous-navigation des routes admin prompts.
- Ne pas casser la lisibilite desktop sous pretexte de mieux servir le mobile; viser un repli propre, pas un appauvrissement brutal.
- Les correctifs CSS doivent reutiliser les tokens existants (`--color-*`, `--glass-*`, espacements/rayons deja presents) et rester concentres dans `AdminPromptsPage.css`.

### UX Requirements

- L operateur doit comprendre en un scan:
  - ou il se trouve dans `/admin/prompts/*`
  - ce que chaque etat signifie
  - quelle action est possible ensuite
- Les messages et libelles doivent employer un francais produit stable, sans jargon interne non explicite.
- Les surfaces denses doivent rester exploitables sur laptop compact et sur mobile sans tableau horizontal illisible ni actions cachees. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Les etats focus et la navigation clavier doivent etre visibles et coherents sur toute la surface admin prompts. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend et transverse a la surface admin prompts.

### References

- Epic 70 et UX-DR associes: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.3: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-3-recomposer-le-detail-prompts-en-lecture-progressive-et-zone-d-actions.md]
- Intelligence 70.4: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-4-rendre-le-schema-visuel-des-processus-llm-avec-react-flow.md]
- Intelligence 70.7: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-7-refondre-la-route-consumption-pour-le-pilotage-operable.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Surface admin prompts actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Styles admin prompts actuels: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- I18n admin actuelle: [Source: C:/dev/horoscope_front/frontend/src/i18n/admin.ts]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `2ff7f718 test(admin-prompts): close residual coverage risk on consumption`
  - `f2b5dd79 feat(admin-prompts): story 70.7 — route consommation pilotable et artefacts BMAD`
  - `b4bea5ff test(admin-prompts): intégration release→catalogue et hint manifeste complet`
  - `cf4b3eef feat(admin-prompts): story 70.6 — route release investigation, revue code`
  - `98f4d761 fix(admin-prompts): story 70.5 — legacy sans actif inventé, i18n complète, tests`
- Constat codebase avant creation:
  - reliquats visibles FR/EN dans le catalogue/detail (`Source of truth`, `Release health`, `Execution profile`, `Output contract`, `Visibility`)
  - sous-navigation locale deja route-aware via `nav` + `NavLink`
  - socle CSS responsive/focus deja present mais encore heterogene
  - i18n dediee deja en place pour `legacy` et `consumption`

### Completion Notes List

- Story creee apres analyse de `epics.md`, du sprint courant, de l etat reel de `AdminPromptsPage.tsx/.css`, de l i18n admin existante et des stories 70.1 a 70.7.
- Le cadrage positionne `70.8` comme une passe de finition transverse centree sur wording, accessibilite et responsive, sans reopen de l architecture fonctionnelle deja livree.
- Le principal garde-fou ajoute pour l implementation est d eviter une fausse conversion de la sous-navigation route-aware en pseudo-tabs ARIA incomplets.
- Implementation 2026-04-18 : nouveau module `adminPromptsCatalog.ts` (FR/EN/ES) branche sur `translateAdmin` ; `AdminPromptsPage.tsx` consomme `tAdmin.promptsCatalog` pour catalogue, detail resolu, release, consommation (libelles statuts), disclosures et messages d etat ; suppression de `aria-selected` sur les lignes catalogue au profit d un `aria-label` explicite par ligne ; libelle bouton detail avec accent ; CSS `min-width:0` sur la page et cellule sante avec retour a la ligne ; correctif `router.tsx` (retrait `v7_startTransition` non supporte par les types RR) pour `npm run lint` ; tests `AdminPromptsPage.test.tsx` alignes sur les libelles FR harmonises.

### File List

- frontend/src/i18n/adminPromptsCatalog.ts
- frontend/src/i18n/admin.ts
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/app/router.tsx
- frontend/src/tests/AdminPromptsPage.test.tsx
- frontend/src/tests/AdminPromptsPage.releaseCatalog.integration.test.tsx
- _bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-04-18 : creation de la story 70.8 de finition transverse (libelles, accessibilite, responsive) et alignement sprint.
- 2026-04-18 : implementation complete — i18n catalogue/release, accessibilite lignes catalogue et navigation, ajustements CSS, tests Vitest mis a jour, statut sprint passe en review.
- 2026-04-18 : code review BMAD — findings documentes (patch + defer), statut repasse en in-progress jusqu a correction ou arbitrage des patch.
- 2026-04-18 : correction post-review — i18n tri asc/desc et bouton reinitialisation filtres catalogue (`adminPromptsCatalog` + `AdminPromptsPage`), statut repasse en review.
- 2026-04-18 : code review BMAD (passe 2) — nouveau finding patch (reliquats FR hors catalogue dans `AdminPromptsPage.tsx`), statut repasse en in-progress.
- 2026-04-18 : correction patch passe 2 — i18n FR/EN/ES pour modale LLM, erreurs assembly résolue, leads d erreur rendu, libellés diff release, repli execution generique (`adminPromptsCatalog.ts` + `AdminPromptsPage.tsx`), tests verts, statut repasse en review.
- 2026-04-18 : correction finale post-review — restauration du flag `v7_startTransition` sans casser le typage, harmonisation FR des libelles `Assembly/Runtime/Live`, mapping metier de la timeline release et couverture Vitest additionnelle pour clavier + contrat responsive ; lint/tests frontend verts, statut passe en done.

### Review Findings (code review 2026-04-18)

- [x] [Review][Patch] Ordre de tri et reinitialisation catalogue encore en francais en dur — **Corrigé** (2026-04-18) : `sortOrderAsc` / `sortOrderDesc` / `resetCatalogFilters` dans `adminPromptsCatalog.ts` (FR/EN/ES), branchement dans `AdminPromptsPage.tsx`.

- [x] [Review][Defer] Onglets Personas et echantillons runtime (`PersonasAdmin`, `AdminSamplePayloadsAdmin`) — l AC1 mentionne ces routes ; le diff 70-8 ne les couvre pas. A traiter si une passe transverse supplementaire est validee. — deferred, hors perimetre du diff actuel

- [x] [Review][Patch] Timeline release : pastilles `proof.proof_type` / verdicts API encore affiches en valeurs brutes pour l operateur — **Corrigé** (2026-04-18) : mapping metier ajoute pour `event_type`, `current_status`, `proof_type`, `verdict/status` dans `adminPromptsCatalog.ts`, branchement dans `AdminPromptsPage.tsx` et tests release mis a jour.

- [x] [Review][Patch] Reliquats francais en dur sur flux critiques hors onglet catalogue (modale confirmation execution LLM, messages erreurs assembly, leads echec execution manuelle, lead erreur rendu, categories diff release, presentation erreur resolue) — **Corrigé** (2026-04-18) : constantes et fonctions dans `adminPromptsCatalog.ts` (`MANUAL_LLM_MODAL`, `RESOLVED_ASSEMBLY_ERRORS`, `MANUAL_EXEC_FAILURE_LEADS`, `RENDER_ERROR_LEADS`, `RELEASE_DIFF_CATEGORY`), exposition via `adminPromptsCatalogStrings`, branchement dans `AdminPromptsPage.tsx`.

- [x] [Review][Patch] Retrait hors perimetre de `future.v7_startTransition`, ce qui change le comportement global du routeur sans lien avec la story de wording/accessibilite [frontend/src/app/router.tsx:4] — **Corrigé** (2026-04-18) : opt-in routeur restaure via objet `future` partage et compatible avec le typage actuel.

- [x] [Review][Patch] Reliquats de wording anglais/technique encore visibles sur la surface admin prompts (`Assembly`, `Runtime`, `Live`) alors que la story exige une harmonisation FR coherente [frontend/src/i18n/adminPromptsCatalog.ts:899] — **Corrigé** (2026-04-18) : libelles FR harmonises dans `adminPromptsCatalog.ts` pour detail, diff release et modes d inspection.

- [x] [Review][Patch] Route release : `event_type`, `current_status`, `proof_type` et `verdict/status` restent affiches bruts cote operateur, ce qui laisse des statuts techniques non harmonises en premier rang [frontend/src/pages/admin/AdminPromptsPage.tsx:2249] — **Corrigé** (2026-04-18) : timeline release branchee sur les mappings metier `labelRelease*` et badges verifies par tests.

- [x] [Review][Patch] Couverture de test insuffisante sur les interactions clavier et le repli responsive catalogue/detail ; les nouveaux tests couvrent surtout les libelles et un cas mobile consommation [frontend/src/tests/AdminPromptsPage.test.tsx:2164] — **Corrigé** (2026-04-18) : ajout d un test clavier sur ligne catalogue et d un test de contrat CSS pour le repli responsive catalogue/detail.
