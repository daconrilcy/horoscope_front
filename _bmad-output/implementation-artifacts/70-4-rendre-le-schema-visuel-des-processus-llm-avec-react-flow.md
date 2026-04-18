# Story 70.4: Rendre le schema visuel des processus LLM avec React Flow

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want un schema visuel interactif des processus LLM,
so that je comprenne rapidement la chaine de composition et les dependances runtime sans parser du texte brut.

## Acceptance Criteria

1. Etant donne qu une cible canonique est ouverte dans le detail, quand la section `Graphe logique` est affichee, alors elle rend un schema visuel avec une bibliotheque React reconnue, et la bibliotheque retenue est `React Flow` ou un equivalent de meme niveau de robustesse.
2. Etant donne le schema visuel, quand il est rendu, alors il relie au minimum `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages`, `runtime inputs` et le resultat operateur, et il distingue visuellement templates, policy, execution profile, sample payloads et fallbacks.
3. Etant donne la densite du graphe ou une contrainte de rendu, quand le composant ne peut plus rester lisible, alors un fallback texte ou une vue simplifiee reste disponible, et aucune information critique n est perdue pour l operateur.
4. Etant donne les stories 67.2, 70.2 et 70.3, quand le schema React Flow remplace l apercu texte actuel, alors les semantics existantes du graphe logique, les etats loading/error/empty et la position de la section dans le detail restent stables.
5. Etant donne les tests admin prompts existants, quand la story est livree, alors la couverture Vitest valide le rendu du graphe visuel nominal et le fallback dense, sans casser les flux runtime preview, sample payloads et execution manuelle.

## Tasks / Subtasks

- [x] Introduire le composant de graphe visuel dans la section `Graphe logique` (AC: 1, 2, 4)
  - [x] Ajouter la dependance officielle `@xyflow/react` dans `frontend/package.json` si elle n est pas deja presente
  - [x] Extraire un composant dedie sous `frontend/src/pages/admin/` plutot que de densifier davantage `AdminPromptsPage.tsx`
  - [x] Conserver l insertion du graphe en fin de detail, apres `Retour LLM`, conformement a `70.3`
- [x] Reutiliser la projection logique existante au lieu de reinventer la semantique du graphe (AC: 2, 4)
  - [x] Partir de `buildLogicGraphProjection` et de ses types (`LogicGraphProjection`, `LogicGraphNode`, `LogicGraphEdge`)
  - [x] Etendre cette projection seulement si necessaire pour fournir positions, type de noeud, handles et labels React Flow
  - [x] Preserver les categories existantes `layer`, `system`, `fallback`, `sample`, ainsi que les resumés `fallbackSummary`
- [x] Construire un rendu React Flow pedagogique et operable (AC: 1, 2)
  - [x] Mapper les noeuds minimums `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages`, `runtime inputs` et `resultat operateur`
  - [x] Ajouter les couches ou sous-noeuds visuels deja portés par la projection actuelle: `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`, `fallbacks registre`, `sample payloads`
  - [x] Definir un legendage FR lisible et des styles differencies sans styles inline, en reutilisant les tokens admin existants
- [x] Preserver un mode degrade robuste et explicite (AC: 3, 4)
  - [x] Garder un fallback texte ou une vue simplifiee pour les graphes denses ou les environnements de rendu contraints
  - [x] Conserver `fallbackSummary` comme socle de resilience et d accessibilite
  - [x] Afficher un message clair si le graphe visuel ne peut pas etre rendu, sans masquer les informations operatoires
- [x] Verrouiller accessibilite, comportement et tests (AC: 3, 5)
  - [x] Eviter les interactions excessives ou non necessaires; garder un zoom/pan sobre et compatible clavier
  - [x] Etendre `AdminPromptsPage.test.tsx` pour verifier le conteneur React Flow et le fallback dense
  - [x] Preserver les tests deja en place sur la section `Graphe logique`, les sample payloads et l execution manuelle

### Review Findings (code review 2026-04-18)

- [x] [Review][Decision] Masquer l attribution React Flow via `proOptions.hideAttribution` — confirmer conformite licence / politique produit (attribution visible vs UI admin epuree). **Résolu 2026-04-18 :** choix A — garder le masquage (MIT) ; commentaire dans `AdminPromptsLogicGraph.tsx`.

- [x] [Review][Patch] Reinitialiser l Error Boundary quand la projection change — `LogicGraphErrorBoundary` utilise `key="flow"` fixe ; apres une erreur de rendu React Flow, un changement d entree catalogue peut laisser l operateur bloque sur le fallback texte. **Corrigé :** `key={logicGraphRemountKey(projection)}` (detail noeud `manifest`).

- [x] [Review][Patch] `console.error` dans `componentDidCatch` — bruit ou fuite de stack en production ; preferer logger applicatif ou garde `import.meta.env.DEV`. **Corrigé :** log uniquement si `import.meta.env.DEV`.

- [x] [Review][Defer] Couverture tests accessibilite clavier (zoom/pan, AC « compatible clavier ») — pas de test automatisé ajouté ; smoke manuel ou story QA dediee. — deferred, gap de test

- [x] [Review][Defer] Churn `package-lock.json` (d3, zustand, `devOptional` sur `@types/react`) — surveiller build CI et `npm audit` apres merge. — deferred, hygiene supply-chain

## Dev Notes

- L etat actuel de `AdminPromptsPage.tsx` contient deja une projection metier exploitable pour le futur composant visuel: `LogicGraphProjection`, `LogicGraphNode`, `LogicGraphEdge` et `buildLogicGraphProjection(resolvedView)`. Cette story doit capitaliser dessus, pas rebatir une seconde logique parallele. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Le detail `70.3` affiche deja la section `Graphe logique` au bon endroit du parcours operateur et le texte d aide mentionne explicitement que React Flow est prevu en `70.4`. Il faut remplacer ce rendu provisoire sans casser la structure pedagogique deja livree. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-3-recomposer-le-detail-prompts-en-lecture-progressive-et-zone-d-actions.md, C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- La CSS actuelle contient deja un socle de classes `admin-prompts-logic-graph*` pour la legende, les noeuds, les aretes et le fallback texte. Cette base peut etre reemployee pour la legende et les degradations, mais le canvas React Flow doit avoir ses propres classes dediees sans styles inline. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Les stories 67.2 et 67.3 ont stabilise le concept de graphe logique inspectable et sa place dans le detail; `70.4` ameliore le medium visuel, pas la definition metier des noeuds ou des liens. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-2-exposer-construction-logique-graphe-inspectable.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-3-refondre-vue-detail-zones-pedagogiques-operables.md]

### Technical Requirements

- Utiliser la bibliotheque officielle `@xyflow/react` pour le rendu React Flow; ne pas installer l ancien package `reactflow`.
- Ne pas modifier le contrat backend `resolved`, ni les hooks `useAdminResolvedAssembly`, ni le flux `selectedManifestEntryId -> resolvedQuery`.
- Conserver les semantics existantes de `dense` et `fallbackSummary`; si le seuil de densite evolue, il doit rester derive de la projection et non disperse dans plusieurs composants.
- Le graphe doit rester strictement en lecture dans cette story: pas d edition de noeuds, pas de drag persistant, pas d ecriture dans Figma, pas de mutation backend.
- Eviter une explosion de complexite dans `AdminPromptsPage.tsx`; preferer un composant local du type `AdminPromptsLogicGraph.tsx` et, si besoin, une extraction de helper de projection partagee.

### Architecture Compliance

- Respecter l architecture frontend Vite + React + TypeScript du monorepo, avec logique de donnees dans hooks/services et presentation dans les composants UI. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture, C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Project-Structure--Boundaries]
- Rester conforme aux regles AGENTS du repo: aucun style inline, reutilisation des variables CSS existantes, petits deltas coherents, tests mis a jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Conserver des etats explicites `loading`, `error`, `empty` et `preview partielle`, y compris dans le mode degrade du graphe. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Library / Framework Requirements

- Dependances deja presentes:
  - `react` `^19.2.0`
  - `react-router-dom` `^6.30.3`
  - `@tanstack/react-query` `^5.90.21`
- Nouvelle dependance attendue pour cette story:
  - `@xyflow/react` version stable courante compatible React 19
- Le rendu visuel doit rester compatible avec les tests `jsdom`/Vitest du projet; si React Flow necessite des mocks mineurs de dimensions ou `ResizeObserver`, les introduire dans le scope des tests admin sans contaminer d autres suites.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/package.json`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers probablement a creer:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsLogicGraph.tsx`
  - eventuellement un fichier CSS associe si la separation ameliore la maintenabilite, sinon extension du CSS existant
- Si les helpers de projection doivent etre partages entre la page et le composant React Flow, extraire un module local simple sous `frontend/src/pages/admin/` plutot qu un utilitaire global premature.

### Testing Requirements

- Etendre les tests Vitest pour verifier au minimum:
  - la presence d un conteneur de graphe visuel nominal dans la region `Graphe logique`
  - la conservation des labels metier attendus (`manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages`, `runtime inputs`)
  - le fallback texte / vue simplifiee quand `logicGraph.dense === true`
  - l absence de regression sur la structure detail deja validee en `70.3`
- Si des APIs navigateur manquent dans `jsdom` pour React Flow, ajouter les stubs/minimocks les plus petits possibles dans le test ou le setup de test.
- Ne pas supprimer les assertions existantes sur les flux `runtime_preview`, sample payloads et execution manuelle; les adapter seulement si le DOM du graphe change.

### Previous Story Intelligence

- `70.1` a isole les routes dediees sous `/admin/prompts/*`; cette story reste strictement sur la route catalogue/detail et ne doit pas reouvrir le sujet navigation.
- `70.2` a pose le master-detail sticky; le graphe doit vivre dans ce detail sans le casser ni forcer un scroll horizontal global.
- `70.3` a deja transforme le detail en lecture progressive et laisse un emplacement naturel pour React Flow. Le message actuel "aperçu texte — React Flow prévu en story 70.4" doit disparaitre une fois le composant visuel livre.
- Le commit recent `00426b9e feat(admin): story 70.3 — détail prompts en sections, zone Actions et replis` confirme que la structure detail est la baseline immediate a respecter.

### Implementation Guardrails

- Prioriser une lecture pedagogique avant l exhaustivite graphique: un graphe simple, stable et lisible vaut mieux qu un canvas tres interactif mais charge cognitivement.
- Garder une direction de graphe explicite de gauche a droite ou de haut en bas; ne pas laisser un layout aleatoire brouiller la chaine de composition.
- Le resultat operateur n apparait pas encore comme noeud explicite dans la projection actuelle; il faudra probablement l ajouter dans la projection sans casser les assertions existantes ni dupliquer `provider_messages`.
- Le fallback texte doit rester disponible meme si React Flow charge correctement, au moins comme mode degrade pour densite forte ou contrainte de rendu.
- Toute nouvelle terminologie visible doit rester en francais produit coherent; seuls les identifiants techniques strictement necessaires (`manifest_entry_id`, etc.) peuvent rester bruts.

### UX Requirements

- Le schema doit aider un operateur a repondre rapidement a trois questions:
  - d ou vient le prompt
  - quelles couches et donnees runtime l enrichissent
  - a quel resultat operateur ou provider il conduit
- Les differenciations visuelles attendues doivent couvrir au minimum:
  - templates / couches de composition
  - politique systeme
  - execution profile provider/model
  - sample payloads
  - fallbacks
- Sur largeur contrainte, le composant doit se degrader proprement sans transformer la page en canvas inutilisable. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend et focalisee sur la visualisation du detail catalogue.

### References

- Epic 70 et story 70.4: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.1: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Intelligence 70.2: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md]
- Intelligence 70.3: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-3-recomposer-le-detail-prompts-en-lecture-progressive-et-zone-d-actions.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation detail actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Styles graphe actuels: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Dependances frontend actuelles: [Source: C:/dev/horoscope_front/frontend/package.json]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `00426b9e feat(admin): story 70.3 — détail prompts en sections, zone Actions et replis`
  - `dbea6f05 docs(70-2): artefact aligné avec périmètre 70.3 et master-detail`
  - `fe8c91df fix(admin): preserve runtime preview payloads in catalog detail`
  - `2dde2ae0 feat(admin): story 70.2 catalogue canonique master-detail`
  - `33a2831c feat(admin): story 70.1 — routes prompts dédiées et correctifs revue`

### Completion Notes List

- Story creee apres analyse de l implementation reelle de `AdminPromptsPage`, du rendu texte provisoire du graphe logique et des tests Vitest existants.
- La story verrouille le choix de la bibliotheque `@xyflow/react`, la reutilisation de `buildLogicGraphProjection` et le maintien d un fallback texte robuste.
- Implementation livree : extraction `adminPromptsLogicGraphProjection.ts` (projection + layout statique), composant `AdminPromptsLogicGraph.tsx` avec `@xyflow/react` (lecture seule, zoom/pan, legende FR, details avec liste des connexions sans dupliquer les noeuds), noeud `résultat opérateur` et arete depuis `provider_messages`, fallback dense et boundary de secours si echec rendu, stub `ResizeObserver` dans les tests Vitest admin.
- Revue code 2026-04-18 : correctifs (cle Error Boundary par `manifest_entry_id`, logs `componentDidCatch` en DEV, commentaire MIT `hideAttribution`) ; passe 2 sans nouveau finding bloquant.
- Artefacts synchronises avec le depot (commit `0088af8d`) : `sprint-status.yaml` (70-4 `done`), story sous `_bmad-output/implementation-artifacts/`, defer dans `67-To-69-deferred-work.md`.

### File List

- frontend/package.json
- frontend/src/pages/admin/adminPromptsLogicGraphProjection.ts
- frontend/src/pages/admin/AdminPromptsLogicGraph.tsx
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/tests/AdminPromptsPage.test.tsx
- _bmad-output/implementation-artifacts/70-4-rendre-le-schema-visuel-des-processus-llm-avec-react-flow.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-04-18 : Graphe logique admin rendu avec React Flow (`@xyflow/react`), projection extraite, tests et ResizeObserver jsdom.
- 2026-04-18 : Revue code — clé remontage Error Boundary (`manifest_entry_id`), `console.error` réservé au DEV, commentaire MIT `hideAttribution` ; story passée `done`.
- 2026-04-18 : Documentation artefacts alignée (`sprint-status`, notes de completion, defer 67–69). Dépôt : commit `0088af8d`.
