# Story 70.3: Recomposer le detail prompts en lecture progressive et zone d actions

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want un detail structure en sections progressives et une zone d actions dediee,
so that je distingue immediatement ce que je lis de ce que je peux executer.

## Acceptance Criteria

1. Etant donne qu une cible canonique est selectionnee, quand le panneau detail est rendu, alors les sections apparaissent dans l ordre `Resume`, `Mode d inspection`, `Etat d execution`, `Prompts`, `Placeholders`, `Retour LLM`, `Graphe logique`, et cette hierarchie reste stable quel que soit le mode de preview.
2. Etant donne les blocs de texte longs du detail, quand ils depassent un volume de lecture confortable, alors ils sont presentes dans des accordions, onglets secondaires ou sections repliables equivalentes, et la page reste lisible sans scroll excessif dans un seul bloc.
3. Etant donne des actions sensibles disponibles, quand le detail est affiche, alors elles sont regroupees dans une zone `Actions` distincte du contenu de lecture, et le niveau de risque ainsi que les preconditions d execution sont explicitement visibles.
4. Etant donne les modes `assembly_preview`, `runtime_preview` et `live_execution`, quand l utilisateur change de mode, alors le detail conserve la meme structure globale et adapte seulement le contenu et les messages d etat necessaires.
5. Etant donne les mecanismes deja livres pour sample payloads, placeholders et execution manuelle, quand la refonte du detail est livree, alors aucune capacite 67 a 69 n est perdue et les etats loading/error/empty restent explicites.

## Tasks / Subtasks

- [x] Reordonner le panneau detail selon la hierarchie cible (AC: 1, 4)
  - [x] Construire un `Resume` immediat de la cible canonique
  - [x] Isoler un bloc `Mode d inspection` distinct du reste
  - [x] Introduire un bloc `Etat d execution` lisible avant les contenus profonds
  - [x] Conserver ensuite `Prompts`, `Placeholders`, `Retour LLM`, `Graphe logique` dans cet ordre
- [x] Introduire une lecture progressive des contenus denses (AC: 2)
  - [x] Rendre les longs prompts et les sections verbeuses repliables ou tabulees
  - [x] Eviter les murs de texte continus dans le detail sticky
  - [x] Preserver l accessibilite clavier et les libelles semantiques des sections repliables
- [x] Separarer clairement lecture et actions (AC: 3, 5)
  - [x] Creer une zone `Actions` dediee
  - [x] Y regrouper l execution manuelle LLM, les CTA sample payloads et les actions sensibles associees
  - [x] Afficher explicitement preconditions, confirmations, risques et messages de statut
- [x] Stabiliser la coherence multi-mode et les etats systeme (AC: 4, 5)
  - [x] Garantir une structure visuelle constante entre `assembly_preview`, `runtime_preview` et `live_execution`
  - [x] Conserver les messages d erreur, d incompletude runtime et de retour provider deja etablis
  - [x] Verifier que les sample payloads restent disponibles meme si la ligne catalogue source n est plus visible
- [x] Etendre la couverture de tests du detail (AC: 1, 2, 3, 4, 5)
  - [x] Ajouter des tests sur l ordre et la presence des sections
  - [x] Ajouter des tests sur l ouverture/repli des sections denses
  - [x] Ajouter des tests sur la zone `Actions` et ses preconditions visibles
  - [x] Ajouter des tests de non-regression sur `runtime_preview` et l execution manuelle

## Dev Notes

- `70.2` a deja transforme le catalogue en master-detail et a rendu le panneau detail sticky. `70.3` ne doit pas refaire cette base, mais restructurer le contenu du detail lui-meme. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md]
- Le detail actuel dans `AdminPromptsPage.tsx` contient beaucoup de blocs denses (`provider_messages`, placeholders, raw output, graphe logique) encore juxtaposes dans une seule surface. Cette story doit organiser cette profondeur sans casser les flux runtime. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Les stories 67 a 69 ont deja durci les statuts placeholders, la preview runtime, les sample payloads et l execution manuelle LLM. `70.3` doit rester une refonte ergonomique du detail, pas une redefinition fonctionnelle de ces mecanismes. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- La story 70.4 prendra ensuite en charge le schema visuel React Flow. `70.3` doit donc preparer un emplacement logique propre pour la section `Graphe logique`, sans tenter de livrer React Flow elle-meme.

### Technical Requirements

- Ne pas modifier la taxonomie de routes ni le layout master-detail deja livres en `70.1` et `70.2`.
- Ne pas changer le contrat backend `resolved`, ni les hooks `useAdminResolvedAssembly`, `useAdminLlmSamplePayloads`, `executeAdminCatalogSamplePayload`, `isAdminRuntimePreviewExecutable`.
- Le detail doit continuer a reposer sur `selectedManifestEntryId`, `resolvedInspectionMode`, `selectedSamplePayloadId` et les mutations existantes.
- Les actions sensibles doivent rester dans la surface detail catalogue uniquement; ne pas les disperser dans la colonne liste.
- Les sections repliables ou onglets secondaires doivent rester compatibles avec l usage sticky et avec le repli mobile.

### Architecture Compliance

- Rester dans la structure frontend existante: `frontend/src/pages/admin`, `frontend/src/tests`, `frontend/src/i18n`. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Conserver la separation entre data hooks React Query et rendu UI; ne pas remonter de logique metier dans les composants de presentation. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Project-Structure--Boundaries]
- Respecter les patterns du projet: loading/error/empty states explicites, accessibilite WCAG 2.1 AA cible, pas de styles inline, reutilisation des tokens CSS existants. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility, C:/dev/horoscope_front/AGENTS.md]

### Library / Framework Requirements

- `react-router-dom` reste deja integre au domaine prompts, mais cette story ne doit pas introduire un nouveau mecanisme de navigation.
- `@tanstack/react-query` reste la source de verite des chargements et mutations.
- Aucun ajout de bibliotheque n est requis pour les sections repliables si le projet peut s appuyer sur des composants existants ou sur du JSX/CSS leger. Si un composant reusable existe deja dans le repo, le reutiliser.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
  - eventuellement `C:/dev/horoscope_front/frontend/src/i18n/admin.ts` si les libelles de sections et de zone actions sont centralises
- Si le detail devient trop massif, extraire des sous-composants locaux sous `frontend/src/pages/admin/` plutot que d ajouter encore de la densite dans `AdminPromptsPage.tsx`.

### Testing Requirements

- Etendre les tests Vitest pour verifier:
  - l ordre stable des sections detail
  - la presence d une zone `Actions` distincte
  - la possibilite d ouvrir/replier les sections longues
  - la stabilite des messages entre `assembly_preview`, `runtime_preview` et `live_execution`
  - la non-regression des flux sample payload / execution manuelle / retour LLM
- Reutiliser la base de tests deja etendue par `70.1` et `70.2` plutot que creer une nouvelle strategie de test parallele. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md]

### Previous Story Intelligence

- `70.1` a centralise le domaine sous `/admin/prompts/*`, ajoute une sous-navigation locale et a evite les appels inutiles hors sous-route active. `70.3` doit maintenir cette discipline.
- `70.2` a deja introduit le conteneur `admin-prompts-catalog-master-detail`, le panneau sticky et un detail catalogue mieux ancre autour de `selectedManifestEntryId`.
- Les correctifs de revue de `70.2` ont mis en evidence deux points a ne pas regresser:
  - accessibilite clavier des elements interactifs
  - persistance des sample payloads runtime meme quand la ligne catalogue sort de la page courante
- `70.2` note aussi une dette structurelle: `AdminPromptsPage.tsx` est deja volumineux. Si la refonte detail grossit trop, preferer extraire des blocs.

### Implementation Guardrails

- La structure detail actuelle reutilise beaucoup de classes `admin-prompts-resolved__*`. Recomposer l ordre et la lisibilite avant de renommer massivement tout le CSS.
- Les messages d erreur `resolvedAssemblyErrorPresentation` et les leads d erreur de `manualExecutionFailureLead` sont deja stabilises; la refonte detail doit les preserver visuellement.
- La zone `Actions` doit rendre le risque explicite sans noyer les CTA dans le contenu de lecture. L execution manuelle LLM doit rester visiblement distincte et confirmee.
- Les blocs tres longs (`provider_messages`, raw output, prompts rendus) sont de bons candidats pour des sections repliables; les metadonnees courtes doivent rester visibles sans clic.
- La story 70.4 ajoutera React Flow. Dans `70.3`, garder la section `Graphe logique` compatible avec un remplacement futur du rendu actuel.

### UX Requirements

- La lecture doit suivre une logique operateur:
  - comprendre la cible
  - comprendre le mode courant
  - voir l etat d execution
  - approfondir prompt / placeholders / retour LLM
  - finir par le graphe logique
- La page ne doit plus donner l impression d un bloc unique de debug brut.
- Les contenus longs doivent etre consultables a la demande, pas imposes d entree.
- Les actions sensibles doivent etre clairement separees du contenu explicatif. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- Story strictement frontend / UX sur la route catalogue prompts.

### References

- Epic 70 et story 70.3: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Intelligence 70.1: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Intelligence 70.2: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation detail actuelle: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Styles detail actuels: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `fe8c91df fix(admin): preserve runtime preview payloads in catalog detail`
  - `2dde2ae0 feat(admin): story 70.2 catalogue canonique master-detail`
  - `33a2831c feat(admin): story 70.1 — routes prompts dédiées et correctifs revue`
  - `43c18fec docs(67-69): artefact non-régression + epics; tests intégration et Vitest alignés`
  - `79ee3af3 feat(admin-llm): clôturer 67-69 deferred work, facettes samples et placeholders`

### Completion Notes List

- Story creee apres implementation reelle de `70.2`, avec reprise explicite des apprentissages de revue et du correctif runtime preview payload.
- Story centree sur la structure de lecture du detail et la separation des actions, sans anticiper indecemment React Flow ni les routes secondaires.

- Implementation 70.3 : panneau detail reordonne (Resume, Mode d inspection, Etat d execution, Actions, puis Prompts / Placeholders / Retour LLM / Graphe logique). Prompts, retours LLM denses et sources de composition passes en `<details>` via `PromptDisclosure`. Zone Actions dediee avec risque, sample payloads, CTA gestion et execution manuelle. Graphe inspectable et sources en fin de parcours. Tests Vitest etendus (ordre des regions, Actions, repli prompts).

### File List

- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/AdminPromptsPage.css
- frontend/src/tests/AdminPromptsPage.test.tsx
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/70-3-recomposer-le-detail-prompts-en-lecture-progressive-et-zone-d-actions.md

### Change Log

- 2026-04-18 : Detail catalogue admin prompts — structure en sections, zone Actions, contenus repliables, graphe en fin de flux ; tests mis a jour.
- 2026-04-18 : Livraison git (implémentation + sprint + artefact) ; revues code documentées.

### Review Findings

- [x] [Review][Patch] Media query 960px : `admin-prompts-resolved__zones` est en `display: flex` ; la règle `grid-template-columns: 1fr` dans le bloc `@media (max-width: 960px)` ne s’applique plus (sélecteur à retirer de cette liste pour éviter CSS mort / confusion) [AdminPromptsPage.css:1017] — corrigé 2026-04-18

- [x] [Review] Repasse ciblée **70-3** (2026-04-18) : aucun nouveau finding (correctif CSS media query vérifié en fichier ; AC couverts par l’implémentation et les tests Vitest ; pas de styles inline sur le périmètre).

- [x] [Review] Pass workflow **bmad-code-review** explicite **70-3** : aucun nouveau finding ; diff `HEAD` cohérent avec les AC ; correctif CSS media query confirmé.
