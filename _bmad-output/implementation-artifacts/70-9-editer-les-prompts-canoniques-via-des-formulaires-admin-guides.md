# Story 70.9: Editer les prompts canoniques via des formulaires admin guides

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want editer un prompt canonique depuis un formulaire admin guide et comprehensible,
so that je puisse preparer une nouvelle version sans manipuler de payload brut, avec validation explicite et un workflow coherent avec l historique et la publication.

## Acceptance Criteria

1. Etant donne qu un admin consulte une cible canonique sur `/admin/prompts`, quand il ouvre le flux d edition d un prompt, alors il accede a un formulaire structure affichant au minimum le prompt developpeur, le modele, la temperature, le budget de sortie et le fallback use case ou un equivalent explicite aligne sur le contrat backend existant.
2. Etant donne qu un formulaire d edition est affiche, quand l admin modifie une valeur invalide ou oublie une information requise, alors la surface montre des messages de validation clairs cote client et relaie proprement les erreurs metier/backend sans renvoyer l operateur a du JSON brut.
3. Etant donne qu un prompt existant est utilise comme base de travail, quand l admin entre en edition, alors le formulaire est pre-rempli a partir de la version de reference la plus pertinente, expose le statut courant du prompt et affiche un resume lisible des changements avant sauvegarde.
4. Etant donne qu une sauvegarde est confirmee, quand l operation reussit, alors la surface confirme qu une nouvelle version non publiee a ete creee, invalide les requetes utiles et rend cette nouvelle version visible dans les surfaces d historique sans publication implicite.
5. Etant donne que le workflow de cycle de vie des versions est traite par la story 70.10, quand 70.9 est implemente, alors le flux de formulaire reste compatible avec `draft/inactive -> published`, ne contourne pas l historique, le diff, le rollback ni l audit existants, et les tests frontend couvrent rendu, validation, sauvegarde et etats de succes/erreur sans regression sur les stories 70.2, 70.3, 70.5 et 70.8.

## Tasks / Subtasks

- [x] Exposer le socle frontend de creation de version depuis la surface admin prompts (AC: 1, 4, 5)
  - [x] Etendre `frontend/src/api/adminPrompts.ts` avec une mutation de creation de draft rebranchant l endpoint admin existant plutot qu un flux parallele
  - [x] Definir ou ajuster les types TypeScript du payload/reponse de creation de version de prompt
  - [x] Invalider proprement les queries catalogue, historique et detail utiles apres sauvegarde
- [x] Construire un formulaire admin guide pour l edition de prompt (AC: 1, 2, 3)
  - [x] Introduire une surface d edition dediee dans `AdminPromptsPage.tsx` ou un composant extrait du domaine admin prompts
  - [x] Pre-remplir les champs depuis la version de reference retenue sans dupliquer la logique de selection de version
  - [x] Afficher le statut courant, les champs editables et les aides contextuelles en francais produit coherent
- [x] Verrouiller validation, feedback et resume de changements (AC: 2, 3, 4)
  - [x] Valider les champs critiques avant soumission avec messages operateur compréhensibles
  - [x] Afficher un resume lisible des changements saisis avant ou au moment de la sauvegarde
  - [x] Afficher des retours explicites `succes`, `erreur`, `sauvegarde en cours` et `nouvelle version creee`
- [x] Garantir la compatibilite avec le workflow d historisation/publication (AC: 4, 5)
  - [x] Ne jamais publier automatiquement depuis le formulaire de sauvegarde
  - [x] Rendre la nouvelle version visible dans les surfaces d historique deja existantes ou prevues
  - [x] Verifier l articulation explicite avec la story 70.10 pour les statuts, le diff, l audit et la publication
- [x] Etendre les tests frontend et les garde-fous de non-regression (AC: 2, 4, 5)
  - [x] Couvrir le rendu du formulaire et le prefill a partir d une version existante
  - [x] Couvrir les erreurs de validation et de mutation
  - [x] Couvrir le succes de sauvegarde avec invalidation/refetch et visibilite de la nouvelle version

### Review Findings

- [x] [Review][Patch] Champ temperature vide accepte comme `0` au lieu d etre rejete [frontend/src/pages/admin/AdminPromptEditorPanel.tsx:71]
- [x] [Review][Patch] Compatibilite `inactive` absente dans le contrat de statut frontend [frontend/src/api/adminPrompts.ts:81]
- [x] [Review][Patch] Le draft cree n est pas conserve comme version comparee apres refetch [frontend/src/pages/admin/AdminPromptsPage.tsx:745]
- [x] [Review][Defer] Rollback legacy n invalide pas l etat actif derive des use cases [frontend/src/pages/admin/AdminPromptsPage.tsx:707] — deferred, pre-existing
- [x] [Review][Defer] Le modal de rollback peut survivre a un changement de use case [frontend/src/pages/admin/AdminPromptsPage.tsx:447] — deferred, pre-existing

## Dev Notes

- Le backend expose deja le seam principal necessaire a `70.9`: `POST /v1/admin/llm/use-cases/{key}/prompts` cree une nouvelle version draft a partir de `LlmPromptVersionCreate`. La story doit reutiliser cet endpoint et ses validations existantes, pas inventer un nouveau contrat de sauvegarde. [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py]
- Le frontend dispose deja des briques de lecture autour des versions de prompt: `AdminPromptVersion`, `useAdminPromptHistory()` et `useRollbackPromptVersion()` sont presents dans `frontend/src/api/adminPrompts.ts`, et la route `legacy` de `AdminPromptsPage.tsx` sait deja lire, comparer et restaurer des versions. `70.9` doit prolonger cette fondation vers l edition, sans dupliquer un second systeme de version. [Source: C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts, C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Les champs deja materialises dans le contrat frontend/backend sont un bon point de depart pour le formulaire: `developer_prompt`, `model`, `temperature`, `max_output_tokens`, `fallback_use_case_key`, `created_by`, `created_at`, `published_at`. Le formulaire ne doit pas exposer de champs hors contrat sans besoin explicite. [Source: C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts, C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py]
- La decision produit validee pour l epic 70 est explicite: sauvegarde => nouvelle version non publiee, publication => action distincte, ancienne version publiee => inactive. Le modele technique visible dans le code est encore en `draft | published | archived`; `70.9` doit donc rester compatible avec cette transition et ne pas figer durablement la mauvaise terminologie dans le nouveau formulaire. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md, C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py, C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts]
- Les tests frontend existants couvrent deja l historique legacy avec des fixtures `AdminPromptVersion` en `published` et `archived`. `70.9` doit s appuyer sur ce harness existant pour ajouter les cas formulaire/creation de version, au lieu de reconstruire une pile de mocks parallele. [Source: C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx]

### Technical Requirements

- Reutiliser l endpoint backend de creation de draft existant pour la sauvegarde du formulaire admin.
- Le flux de sauvegarde doit creer une nouvelle version non publiee; la publication reste une action distincte, hors du bouton de sauvegarde.
- Le formulaire doit manipuler les champs deja supportes par le contrat de prompt version et ne pas introduire de second schema local divergent.
- Les invalidations React Query doivent couvrir au minimum:
  - le catalogue admin prompts
  - l historique du prompt/use case concerne
  - toute surface detail ou route secondaire affichant l etat des versions
- Le flux doit rester compatible avec la story 70.10, qui consolidera le cycle de vie, l historisation, le diff, l audit et la terminologie finale des statuts.

### Architecture Compliance

- Respecter l architecture frontend React/TypeScript et la centralisation data-fetching dans `frontend/src/api/`. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Respecter `AGENTS.md`: petit delta coherent, pas de style inline, reutilisation des classes/tokens CSS existants, tests mis a jour. [Source: C:/dev/horoscope_front/AGENTS.md]
- Preserver les patterns deja poses en 70.2 a 70.8: master-detail, zone d actions separee, i18n admin centralisee, lecture historique legacy et accessibilite de premier rang. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md, C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md]

### Library / Framework Requirements

- Aucune nouvelle bibliotheque n est requise par defaut pour cette story.
- Reutiliser en priorite:
  - `@tanstack/react-query` via `frontend/src/api/adminPrompts.ts`
  - les composants/form patterns deja presents dans le frontend admin si reutilisables
  - l infrastructure i18n admin existante
- Ne pas introduire une bibliotheque de formulaire lourde si le pattern actuel du repo couvre deja le besoin avec un delta maitrise.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/i18n/admin.ts`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
- Fichiers potentiellement a creer selon le decoupage retenu:
  - composant local de formulaire d edition dans `frontend/src/pages/admin/` ou `frontend/src/components/admin/`
  - helpers i18n admin prompts si les textes de formulaire meritent une centralisation dediee
- Eviter de disperser la logique d edition en dehors du domaine admin prompts.

### Testing Requirements

- Frontend:
  - test de rendu du formulaire d edition depuis une version existante
  - test de prefill des champs depuis la version de reference
  - test de validation locale et d affichage des erreurs backend
  - test de succes de sauvegarde avec message de confirmation et invalidation/refetch
  - test de non-regression sur l historique legacy et la zone d actions existante
- Backend:
  - aucun nouveau contrat n est requis par defaut pour cette story, mais si le payload de creation evolue il faut ajuster les tests du router `admin_llm` en consequence
- Reutiliser les fixtures/history mocks deja presents dans `AdminPromptsPage.test.tsx`.

### Previous Story Intelligence

- `70.8` a termine l harmonisation FR/accessibilite/responsive. Toute nouvelle UI de formulaire doit reutiliser ce vocabulaire et ces garde-fous, pas reintroduire des labels techniques ou un focus pauvre.
- `70.5` a consolide la route `legacy` comme surface de comparaison/rollback. `70.9` doit faire converger la sauvegarde vers cette surface d historique, pas inventer une vue annexe des versions.
- `70.3` a separe lecture et actions. Le flux d edition doit s inscrire dans cette logique et rester clairement identifie comme action sensible/modifiante.
- `70.10` existe deja comme story de suite pour historisation, statuts explicites, publication et audit. `70.9` ne doit donc pas embarquer une implementation concurrente de ces regles, mais rester compatible avec elles.

### Implementation Guardrails

- Ne pas confondre edition de prompt et edition de la taxonomie catalogue: `manifest_entry_id` et la structure canonique restent la verite d exploration.
- Ne pas introduire un mode "save and publish" implicite dans le formulaire.
- Ne pas exposer un textarea brut sans structure ni aides contextuelles; l objectif de la story est un formulaire guide, pas un simple champ libre nu.
- Ne pas figer `archived` comme wording final visible si la transition metier vers `inactive` est en cours; mapper l affichage utilisateur de facon compatible avec `70.10`.
- Ne pas contourner le systeme de queries existant par des `window.location.reload()` ou une remise a zero globale de page.

### UX Requirements

- L operateur doit comprendre rapidement:
  - quelle version il edite comme base
  - quels champs il modifie
  - si la sauvegarde cree une nouvelle version ou publie une version existante
- Le formulaire doit rester lisible et guidant, avec labels visibles, aides courtes et retours d erreur/action de premier rang.
- Le resultat attendu apres sauvegarde doit etre explicite: une nouvelle version non publiee est creee et devient consultable dans l historique. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story principalement frontend, avec dependance explicite au seam backend deja existant pour la creation de draft.

### References

- Epic 70 et FR52: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.3: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-3-recomposer-le-detail-prompts-en-lecture-progressive-et-zone-d-actions.md]
- Intelligence 70.5: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md]
- Intelligence 70.8: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-8-harmoniser-les-libelles-l-accessibilite-et-le-responsive.md]
- Story de suite 70.10: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-10-historiser-comparer-et-auditer-chaque-sauvegarde-de-prompt.md]
- API prompts admin: [Source: C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py]
- Modele prompt versions: [Source: C:/dev/horoscope_front/backend/app/infra/db/models/llm_prompt.py]
- API frontend admin prompts: [Source: C:/dev/horoscope_front/frontend/src/api/adminPrompts.ts]
- UI admin prompts existante: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `7f6a11b3 fix(admin-prompts): finalize story 70.8 review follow-ups`
  - `2ff7f718 test(admin-prompts): close residual coverage risk on consumption`
  - `f2b5dd79 feat(admin-prompts): story 70.7 — route consommation pilotable et artefacts BMAD`
  - `b4bea5ff test(admin-prompts): intégration release→catalogue et hint manifeste complet`
  - `cf4b3eef feat(admin-prompts): story 70.6 — route release investigation, revue code`
- Constat codebase avant creation:
  - endpoint de creation de draft deja present dans `admin_llm.py`
  - types frontend des versions encore en `draft | published | archived`
  - UI legacy deja branchee sur `useAdminPromptHistory()` et `useRollbackPromptVersion()`
  - harness Vitest existant deja capable de mocker l historique des versions de prompt
- Verification implementation:
  - `npm run test -- AdminPromptsPage`
  - `npm run lint`

### Completion Notes List

- Story creee apres analyse du workflow BMAD, de `epics.md`, du sprint courant, des stories 70.5, 70.8 et 70.10, ainsi que du code reel backend/frontend autour des prompt versions.
- Le cadrage positionne `70.9` comme la couche operateur de saisie et de sauvegarde, en laissant a `70.10` la consolidation du cycle de vie, des statuts, de l audit et du diff.
- Le principal garde-fou ajoute pour l implementation est d utiliser le seam backend existant de creation de draft et d eviter toute publication implicite depuis le formulaire.
- Le frontend legacy expose maintenant un formulaire guide extrait dans `AdminPromptEditorPanel.tsx`, pre-rempli depuis la version de reference, avec resume de changements, validation locale et feedback operateur sans JSON brut.
- La creation de draft reutilise `POST /v1/admin/llm/use-cases/{key}/prompts` via `useCreatePromptDraft()`, invalide catalogue/historique/detail et rend la nouvelle version visible dans l historique legacy apres refetch.
- La validation HTML native du formulaire a ete desactivee (`noValidate`) pour laisser la validation locale React couvrir correctement les erreurs operateur, y compris sur les champs numeriques.
- Les regressions critiques sont couvertes dans `AdminPromptsPage.test.tsx`: prefill + succes de sauvegarde, blocage de validation locale, et message backend formate.
- La passe de revue 70.9 a ete fermee avec trois correctifs: refus explicite d une temperature vide, compatibilite frontend avec le statut `inactive`, et conservation immediate du draft cree comme version de comparaison via mise a jour optimiste du cache d historique.

### File List

- _bmad-output/implementation-artifacts/70-9-editer-les-prompts-canoniques-via-des-formulaires-admin-guides.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/67-To-69-deferred-work.md
- frontend/src/api/adminPrompts.ts
- frontend/src/i18n/admin.ts
- frontend/src/i18n/adminPromptsEditor.ts
- frontend/src/i18n/adminPromptsLegacy.ts
- frontend/src/pages/admin/AdminPromptEditorPanel.tsx
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/tests/AdminPromptsPage.test.tsx

## Change Log

- 2026-04-18 : creation de la story 70.9 (formulaire admin guide pour edition de prompt canonique, validation, sauvegarde de nouvelle version non publiee et compatibilite avec 70.10).
- 2026-04-18 : implementation frontend de l edition guidee des prompts legacy, mutation de creation de draft avec invalidation React Query, i18n dediee, tests Vitest de succes/validation/erreur et finalisation en statut `review`.
- 2026-04-18 : corrections post-code-review sur la validation numerique, le statut `inactive`, la conservation du draft cree dans la comparaison legacy et cloture en statut `done`.
