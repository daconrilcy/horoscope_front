# Story 70.12: Refondre la lecture admin des prompts en couches observables

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / prompt governor,
I want que l admin affiche la chaine de prompting comme une composition de couches distinctes et des artefacts runtime reels,
so that je comprenne ce qui selectionne la cible, quels blocs textuels sont effectivement actifs, et quel payload est reellement envoye au provider sans pipeline trompeur ni noeuds decoratifs.

## Acceptance Criteria

1. Etant donne qu un admin ouvre `/admin/prompts/catalog` ou le detail d une cible canonique, quand la page charge, alors la lecture est structuree en niveaux distincts `Activation`, `Composants selectionnes`, `Artefacts runtime` et n affiche plus un faux pipeline ou plusieurs etats textuels sans difference observable.
2. Etant donne qu une cible canonique est resolue, quand l admin consulte `Activation`, alors il voit au minimum `feature`, `subfeature`, `plan`, `locale`, `manifest_entry_id`, `active snapshot`, `execution profile`, `provider target`, `policy family`, `output schema` et les selections d injecteurs/persona pertinentes, sans gros blocs de texte a ce niveau.
3. Etant donne qu une cible dispose de briques textuelles versionnees, quand l admin consulte `Composants selectionnes`, alors les blocs sont affiches par responsabilite claire parmi `domain instructions`, `use case overlay` optionnel, `plan overlay` uniquement s il existe comme couche distincte, `persona overlay` optionnel, `output contract`, `style / lexicon rules`, `error handling rules`, `hard policy`, et un bloc vide ou purement nominal n est pas rendu comme un prompt autonome.
4. Etant donne que le pipeline runtime compose plusieurs etapes, quand l admin consulte `Artefacts runtime`, alors il voit uniquement des etats reels et differenciables au minimum `developer prompt assembled`, `developer prompt after persona` si applicable, `developer prompt after injectors`, `system prompt(s)`, `final provider payload`, avec un delta ou une explication visible de ce qui change entre chaque etape.
5. Etant donne la cible `natal / interpretation / free / fr-FR`, quand l admin la consulte, alors la lecture admin expose honnetement la surcharge textuelle effectivement versionnee (`use case overlay` ou `plan overlay` si une couche de formule distincte existe) et ne presente plus un bloc baptise `plan overlay` sans preuve textuelle autonome.
6. Etant donne une cible premium avec persona, quand l admin la consulte, alors la `persona overlay` expose sa source, sa version ou reference, son contenu resolu, son mode de fusion et un before/after lisible entre `developer prompt assembled` et `developer prompt after persona`.
7. Etant donne que la `hard policy` peut etre envoyee en `system` ou injectee dans le developer prompt, quand l admin consulte les artefacts runtime, alors son emplacement reel d injection est explicite et observable, et elle n apparait plus comme un simple noeud flottant ambigu relie au rendu final.
8. Etant donne qu un composant source ou un artefact runtime ne change pas le texte, quand il est affiche, alors l UI indique clairement qu il est absent, inactif ou sans impact au lieu de simuler un nouvel etat textuel equivalent au precedent.
9. Etant donne la couverture admin existante, quand la story est livree, alors les tests verrouillent au minimum la nouvelle taxonomie d affichage, l absence du faux noeud `prompt use case` si aucun overlay textuel n existe, l honnetete du composant editorial free (`use case overlay` vs `plan overlay` selon la source effective), l observabilite de `persona` et `hard policy`, et la distinction reelle entre `assembled`, `after persona`, `after injectors`, `system`, `payload final`.

## Tasks / Subtasks

- [x] Recentrer le contrat d inspection admin sur trois niveaux lisibles (AC: 1, 2, 3, 4, 7, 8, 9)
  - [x] Introduire ou exposer cote backend un contrat detail admin qui separe explicitement `activation`, `selected_components` et `runtime_artifacts`
  - [x] Eviter de reutiliser des champs ambigus du payload `resolved` existant quand ils melangent selection canonique, contenu texte et payload provider
  - [x] Preserver `manifest_entry_id` comme cle nominale de lecture
- [x] Eclater la lecture des composants source selon leurs responsabilites (AC: 2, 3, 5, 6, 7, 8, 9)
  - [x] Remplacer le faux noeud `prompt use case` par un vrai `use case overlay` optionnel, affiche seulement s il apporte un contenu textuel distinct
  - [x] Rendre visible un `plan overlay` autonome uniquement quand une couche de formule distincte est observable; sinon conserver un `use case overlay` honnete
  - [x] Isoler `output contract`, `style / lexicon rules` et `error handling rules` plutot que de les laisser noyes dans un template monolithique
  - [x] Rendre `persona overlay` observable avec reference/source/version, texte resolu et mode de fusion
- [x] Rendre les artefacts runtime reels et differenciables (AC: 1, 4, 6, 7, 8, 9)
  - [x] Exposer `developer prompt assembled` puis `developer prompt after persona` uniquement si la persona modifie reellement le contenu
  - [x] Exposer `developer prompt after injectors` avec ses apports runtime observables
  - [x] Exposer `system prompt(s)` et `final provider payload` comme artefacts distincts du developer prompt
  - [x] Ajouter une presentation de delta ou de resume de changement entre etapes pour eviter les duplications opaques de texte
- [x] Refondre la surface admin prompts pour la nouvelle lecture (AC: 1, 2, 3, 4, 5, 6, 7, 8, 9)
  - [x] Reprojeter le schema React Flow du catalogue pour representer `Activation -> Selected components -> Runtime artifacts`
  - [x] Supprimer les noeuds purement nominaux ou trompeurs et conserver seulement les couches reelles et/ou les selections de pilotage
  - [x] Revoir la modale par noeud pour qu elle montre soit un composant source versionne, soit un artefact runtime, avec vocabulaire clair et sans sur-affichage de details hors contexte
- [x] Verrouiller les tests et garde-fous documentaires (AC: 5, 6, 7, 8, 9)
  - [x] Ajouter ou etendre des tests backend sur le nouveau contrat detail admin pour les cas `free` et `premium`
  - [x] Etendre les tests frontend du catalogue/detail pour verifier la nouvelle taxonomie et les deltas observables
  - [x] Mettre a jour la documentation d artefact et, si le pipeline runtime ou sa lecture de reference change, `docs/llm-prompt-generation-by-feature.md`

## Dev Notes

### Technical Requirements

- La refonte doit corriger le defaut de fond identifie en revue produit: l admin melange aujourd hui trois niveaux differents, `configuration d activation`, `assemblage logique` et `payload reellement envoye au provider`, ce qui rend le graphe trompeur meme quand il est techniquement coherent avec la projection actuelle.
- Le futur contrat admin doit partir du runtime reel deja documente dans `docs/llm-prompt-generation-by-feature.md`: un message `system` pour la hard policy, un ou plusieurs messages `developer`, puis le payload utilisateur/historique. L admin ne doit plus inventer un faux `prompt final` textuel si l artefact reel est en fait un ensemble de messages provider.
- Le `feature template` actuel porte trop de responsabilites. La story doit pousser une lecture ou une decomposition observable qui distingue au minimum le coeur metier (`domain instructions`) du contrat de sortie, des regles de style/lexique et des regles de gestion d erreur, meme si certains blocs restent physiquement stockes ensemble dans un premier temps.
- Le `plan free` ne doit etre affiche comme `plan overlay` que si une couche textuelle distincte existe reellement. Sinon, l admin doit conserver un `use case overlay` et rendre explicite l absence de couche de formule autonome.
- La `persona` et la `hard policy` ne doivent plus etre "prouvees" seulement par la presence d un noeud. L admin doit montrer leur contenu resolu et leur point d injection effectif.

### Architecture Compliance

- Respecter la doctrine canonique de l Epic 66: le pipeline documente dans `docs/llm-prompt-generation-by-feature.md` reste la source de verite. La surface admin doit s aligner sur ce pipeline, pas construire une lecture parallele divergente. [Source: C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md]
- Respecter les acquis des stories 66.45, 66.46, 67.2, 68.x, 69.x et 70.x: on refond la lisibilite et le contrat d inspection, pas la taxonomie canonique `manifest_entry_id` ni la separation preview/execution deja posee. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-45-vue-catalogue-canonique-prompts-actifs.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-46-vue-detail-resolved-prompt-assembly.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-2-exposer-construction-logique-graphe-inspectable.md]
- Respecter `AGENTS.md`: petit delta coherent, pas de style inline, reutilisation des variables CSS existantes, pas de duplication de logique si un contrat ou un composant existant peut etre etendu. [Source: C:/dev/horoscope_front/AGENTS.md]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut.
- Reutiliser la stack existante:
  - Backend FastAPI / Pydantic / SQLAlchemy deja en place pour exposer la nouvelle lecture admin
  - Frontend React 19.2 / React Router / React Query pour la projection et l inspection
  - React Flow reste la bibliotheque de schema pour la visualisation admin tant qu elle represente des noeuds semantiquement justifies
- Ne pas introduire une seconde surface de visualisation parallele au detail admin existant si une projection plus saine peut etre derivee du contrat actuel.

### File Structure Requirements

- Fichiers backend probablement touches:
  - `C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py`
  - `C:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py`
  - `C:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py`
  - `C:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py`
  - `C:/dev/horoscope_front/backend/tests/integration/test_admin_llm_catalog.py`
- Fichiers frontend probablement touches:
  - `C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/adminPromptCatalogFlowProjection.ts`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsLogicGraph.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptCatalogNodeModal.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`

### Testing Requirements

- Backend:
  - test sur la separation `activation / selected_components / runtime_artifacts`
  - test `natal / interpretation / free / fr-FR` verifiant qu un `plan overlay` n apparait que s il existe comme couche distincte et que l admin retombe sinon sur un `use case overlay` honnete
  - test premium verifiant la presence d une `persona overlay` observable et la position reelle de la `hard policy`
- Frontend:
  - test de projection du graphe et/ou de la vue detail sur la nouvelle taxonomie
  - test d absence du faux noeud `prompt use case` quand il n y a pas d overlay textuel
  - test d affichage du composant editorial free reel (`use case overlay` ou `plan overlay` selon la source effective)
  - test de distinction entre `developer prompt assembled`, `after persona`, `after injectors`, `system`, `final provider payload`

### Previous Story Intelligence

- `67.2` a deja introduit un graphe inspectable, mais sa projection actuelle reste pedagogique plutot qu une preuve stricte des couches runtime. Cette story doit partir de ce seam au lieu de recreer un deuxieme graphe. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-2-exposer-construction-logique-graphe-inspectable.md]
- `70.11` a reoriente le catalogue vers un flux `feature / formule / locale` puis React Flow + modale par noeud. La presente story doit capitaliser sur cette interaction, sans regresser sur la largeur, le theming ou les fixes React Flow deja livres. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-11-elargir-le-layout-admin-et-retablir-les-contrastes-light-dark.md]
- Les stories 68 et 69 ont deja fixe les notions de `runtime preview`, `sample payloads` et `live execution`. La nouvelle lecture admin doit les reutiliser au bon niveau, pas les reinterpreter comme des blocs de prompt supplementaires. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md]

### Implementation Guardrails

- Ne pas conserver un noeud textuel `prompt use case` si son contenu n est qu un label fonctionnel ou une cle de mapping.
- Ne pas montrer plusieurs etats textuels consecutifs si leur contenu est strictement identique sans signaler explicitement qu il n y a pas de delta.
- Ne pas afficher la `hard policy` comme simple noeud decoratif sans prouver son point d injection reel.
- Ne pas enterrer `plan free` et `persona` dans des libelles ou badges abstraits; leur contenu observable doit etre lisible.
- Ne pas casser la separations preview/execution: `final provider payload` reste une lecture d inspection, pas une execution implicite.

### UX Requirements

- Le graphe et la modale doivent repondre a une question operatoire simple: "pourquoi ce prompt part ainsi au provider ?"
- Les informations de selection (`feature`, `plan`, `locale`, `snapshot`, `provider`) doivent etre visibles sans ouvrir une cascade de noeuds textuels.
- Les etapes textuelles doivent etre peu nombreuses, chacune justifiee, et porter un libelle directement comprehensible pour un operateur non auteur du code.

## Follow-up Notes

- Le besoin utilisateur ayant declenche cette story est explicite: la pipeline admin actuelle reste conceptuellement trompeuse, car elle montre des etats ou noeuds textuels qui ne correspondent pas a de vraies transformations semantiques distinctes.
- La story doit traiter comme priorite produit le cas `natal_interpretation free` afin de prouver que la restriction business du plan est enfin visible comme une couche textuelle reelle, et non comme une simple etiquette.
- Si une decomposition physique plus fine des prompts canoniques s avere trop large pour un seul delta, l implementation peut d abord exposer une lecture admin fiabilisee a partir des artefacts existants, a condition de rendre les dettes restantes explicites et testees.

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story mixte backend + frontend, centre sur le contrat admin de lecture des prompts et sa projection UI.

### References

- Pipeline runtime reel: [Source: C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md]
- Epic admin LLM preview/execution: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md]
- Epic 66 orchestration canonique: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md]
- Catalogue admin prompts actuel: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Projection catalogue actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/adminPromptCatalogFlowProjection.ts]
- Graphe React Flow actuel: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsLogicGraph.tsx]
- Modale de noeud actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptCatalogNodeModal.tsx]
- Route admin backend detail prompts: [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Sprint status ne contenait plus de story `backlog` explicite apres `70.11`; `70.12` est creee comme suite logique de l epic 70 pour traiter la refonte semantique demandee sur la surface admin prompts.
- Le besoin produit source vient du retour utilisateur sur la lecture du schema `natal free`, valide ensuite par une proposition cible de structuration en trois niveaux: activation canonique, composants selectionnes, artefacts runtime.
- Implémentation 2026-04-19: extension additive du payload `resolved` backend avec `activation`, `selected_components`, `runtime_artifacts`, conservation des anciens champs pour compatibilité avec l exécution manuelle et les vues héritées.
- Validation 2026-04-19: `pytest -q backend/tests/integration/test_admin_llm_catalog.py -k "resolved_detail_exposes_sources_pipeline_and_placeholders or effective_runtime_use_case_for_natal_free or exposes_persona_overlay_and_runtime_delta"`, `ruff check backend/app/api/v1/routers/admin_llm.py backend/tests/integration/test_admin_llm_catalog.py`, `npm run test -- --run src/tests/AdminPromptsCatalogFlow.test.tsx`, `npm run lint`.
- Correctifs review 2026-04-19: `activation.persona_policy` est maintenant derivee de la persona effectivement resolue, et l admin n etiquete plus un prompt de use case comme `plan overlay` en l absence de couche de formule distincte.

### Completion Notes List

- Story creee pour remplacer la lecture admin actuelle basee sur des noeuds parfois nominaux par une representation en couches observables alignee sur le runtime reel.
- Le cadrage impose un contrat admin plus explicite et une projection frontend plus honnete, sans reintroduire une pipeline parallele au gateway canonique.
- Le cas `natal free` reste le scenario de reference pour verifier que la lecture admin n attribue jamais a tort un `plan overlay` a un simple prompt de use case.
- Le detail admin expose maintenant trois sections lisibles et testees: `Activation`, `Composants selectionnes`, `Artefacts runtime`.
- Le graphe React Flow n affiche plus de faux noeud `prompt use case`; il projette les composants réellement sélectionnés, y compris un `use case overlay` pour `natal/free` tant qu aucune couche de plan distincte n est matérialisée, `persona overlay` pour les cibles premium, puis les artefacts runtime différenciés jusqu au `final provider payload`.
- La modale par noeud réutilise l édition directe uniquement pour les composants réellement éditables (`editable_use_case_key`) et reste en lecture pour les artefacts runtime.
- La review finale a verrouille deux garde-fous de vérité: la `persona_policy` ne peut plus contredire une `persona_overlay` réellement affichée, et `natal/free` n est plus relabellisé abusivement en `plan overlay` tant qu il reste un simple prompt de use case actif.

### File List

- _bmad-output/implementation-artifacts/70-12-refondre-la-lecture-admin-des-prompts-en-couches-observables.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/api/v1/routers/admin_llm.py
- backend/tests/integration/test_admin_llm_catalog.py
- docs/llm-prompt-generation-by-feature.md
- frontend/src/api/adminPrompts.ts
- frontend/src/pages/admin/AdminPromptCatalogNodeModal.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/adminPromptCatalogFlowProjection.ts
- frontend/src/tests/AdminPromptsCatalogFlow.test.tsx

### Change Log

- 2026-04-19 : creation de la story 70.12 pour refondre la lecture admin des prompts en couches observables alignees sur le runtime reel.
- 2026-04-19 : implementation backend/frontend de la nouvelle lecture `activation / selected_components / runtime_artifacts`, refonte du graphe catalogue, extension de la modale et des tests, mise a jour de la documentation runtime.
- 2026-04-19 : correctifs post-review pour aligner `persona_policy` sur la persona effectivement resolue et supprimer le faux relabelling `plan overlay` des prompts de use case.
