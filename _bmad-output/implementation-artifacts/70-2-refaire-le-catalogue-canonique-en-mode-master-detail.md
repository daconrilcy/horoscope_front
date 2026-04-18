# Story 70.2: Refaire le catalogue canonique en mode master-detail

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a admin ops,
I want un catalogue canonique simplifie avec liste filtrable et panneau detail sticky,
so that je puisse inspecter rapidement une cible sans perdre le contexte de la selection.

## Acceptance Criteria

1. Etant donne qu un admin ouvre la route catalogue prompts, quand la page charge sur desktop, alors la surface affiche une liste canonique filtrable a gauche et un panneau detail sticky a droite, et la selection courante reste visible pendant la lecture du detail.
2. Etant donne le tableau catalogue, quand il est affiche, alors il n expose que les colonnes de premier niveau `tuple`, `snapshot actif`, `provider/modele`, `sante` et `action`, et les metadonnees secondaires sont reservees au panneau detail.
3. Etant donne la barre de filtres, quand l admin interagit avec elle, alors elle presente des labels visibles, un bouton `Reinitialiser`, des filtres actifs lisibles et une zone `Filtres avances` repliable sans perdre les capacites de filtrage actuelles.
4. Etant donne une entree du catalogue, quand l admin la selectionne, alors le panneau detail affiche au minimum le resume de cible, les metadonnees canoniques utiles et l acces au detail resolved sans reintroduire les univers `legacy`, `release` ou `consumption` dans la colonne liste.
5. Etant donne un usage mobile ou ecran etroit, quand le master-detail ne tient plus en deux colonnes, alors la surface se replie en une seule colonne lisible sans casser la selection, les filtres ni l acces au detail.

## Tasks / Subtasks

- [x] Recomposer la surface catalogue en vrai layout master-detail (AC: 1, 5)
  - [x] Reutiliser la route catalogue issue de `70.1` sans casser `/admin/prompts` et `/admin/prompts/catalog`
  - [x] Construire une colonne liste a gauche et un panneau detail a droite avec comportement sticky sur desktop
  - [x] Definir un comportement mono-colonne coherent sur viewport etroit
- [x] Simplifier la grille catalogue et deplacer l information secondaire dans le detail (AC: 2, 4)
  - [x] Reduire la vue liste aux 5 colonnes cibles
  - [x] Conserver l action d inspection vers le detail resolved
  - [x] Recomposer le panneau detail pour afficher les metadonnees utiles de la cible selectionnee
- [x] Refaire les filtres pour reduire la charge cognitive sans perte fonctionnelle (AC: 3)
  - [x] Ajouter des labels visibles aux champs
  - [x] Introduire un reset explicite
  - [x] Rendre les filtres avances repliables
  - [x] Afficher les filtres actifs de facon scannable
- [x] Preserver les comportements de selection et de chargement existants (AC: 1, 4, 5)
  - [x] Garder `selectedManifestEntryId` comme ancre de selection
  - [x] Eviter les regressions sur `resolvedInspectionMode`, `selectedSamplePayloadId` et l execution manuelle deja en place
  - [x] Ne pas reintroduire les univers `legacy`, `release`, `consumption` dans la surface catalogue
- [x] Etendre la couverture de tests UI et responsive (AC: 1, 2, 3, 5)
  - [x] Ajouter des tests sur les colonnes visibles du catalogue
  - [x] Ajouter des tests sur la reinitialisation des filtres et le panneau detail
  - [x] Ajouter un test de comportement route catalogue / selection apres navigation

### Review Findings

- [x] [Review][Patch] Lignes du tableau sélectionnables à la souris mais sans équivalent clavier explicite — `AdminPromptsPage.tsx` [`<tr onClick>`] — corrigé : `tabIndex={0}`, `onKeyDown` Entrée/Espace, `aria-selected`, `:focus-visible` CSS ; `stopPropagation` sur le bouton d’action
- [x] [Review][Patch] `resetCatalogFilters` ne remet pas `catalogAdvancedFiltersOpen` à `false` — après reset, la section « Filtres avancés » peut rester ouverte de façon incohérente — `AdminPromptsPage.tsx` — corrigé : `setCatalogAdvancedFiltersOpen(false)` dans `resetCatalogFilters`
- [x] [Review][Patch] Couverture tests AC5 / Testing Requirements : pas d’assertion sur le conteneur master-detail (`admin-prompts-catalog-master-detail`) ni sur le repli mono-colonne — `AdminPromptsPage.test.tsx` — corrigé : assertion sur le conteneur dans le test catalogue principal
- [x] [Review][Defer] Fichier `AdminPromptsPage.tsx` déjà volumineux avant ce diff ; dette structurelle hors périmètre strict 70.2 — `AdminPromptsPage.tsx` — deferred, pre-existing

## Dev Notes

- Cette story intervient apres `70.1`, qui a deja pose les sous-routes `/admin/prompts/*`, la sous-navigation locale et la derive `activeTab` depuis le routeur. Le catalogue doit maintenant etre refondu uniquement dans le sous-espace `catalog`, sans toucher a la structure de routage deja stabilisee. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Le code actuel de `AdminPromptsPage` rend encore le catalogue comme une grosse table dense avec beaucoup de filtres et injecte le detail resolved dans le meme flux vertical. C est ce couplage que cette story doit casser en faveur d un vrai layout master-detail. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx, C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Les stories 66.45 et 66.46 ont deja etabli la vue catalogue canonique et le detail resolved. Cette story doit les rendre plus operables, pas redefinir le backend ni le contrat des hooks existants. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Requirements-Inventory]
- Les stories 67 a 69 ont ajoute les statuts placeholders, le graphe logique, les sample payloads et l execution manuelle. Rien de cela ne doit etre perdu quand le detail change d emplacement visuel. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]

### Technical Requirements

- Conserver la route catalogue existante et son integration avec `resolvePromptsTabFromPath`. Cette story ne doit pas modifier la taxonomie des routes prompts.
- Ne pas changer le contrat backend `resolved` ni les hooks data (`useAdminLlmCatalog`, `useAdminResolvedAssembly`, `useAdminLlmSamplePayloads`, etc.).
- La liste gauche doit rester basee sur le catalogue canonique existant et continuer a piloter `selectedManifestEntryId`.
- Le detail droite doit etre decouple de la table mais continuer a exposer le detail resolved deja present.
- Les actions sensibles d execution manuelle peuvent rester visuellement dans le detail catalogue pour l instant, tant qu elles ne regressent pas; leur rationalisation complete appartient surtout a `70.3`.

### Architecture Compliance

- Rester dans l architecture frontend React + TypeScript du projet et dans la structure `frontend/src/pages/admin`, `frontend/src/tests`, `frontend/src/i18n`. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- Conserver la separation entre UI et logique de fetch. Les composants UI s appuient sur les hooks API existants, sans logique metier repliquée dans le rendu. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Project-Structure--Boundaries]
- Respecter les patterns du projet: loading/error/empty states explicites, conventions de nommage frontend et tests Vitest/Testing Library. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Implementation-Patterns--Consistency-Rules]

### Library / Framework Requirements

- `react-router-dom` est deja utilise pour le domaine prompts; ne pas recreer un tab-state parallele pour le catalogue.
- `@tanstack/react-query` reste la source de verite des chargements.
- Aucun ajout de bibliotheque UI n est requis pour cette story. Utiliser les classes CSS existantes et les tokens du design system du repo.

### File Structure Requirements

- Fichiers tres probablement touches:
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsPage.test.tsx`
  - `C:/dev/horoscope_front/frontend/src/tests/AdminPromptsRouting.test.tsx` si la selection catalogue depend de la route
  - eventuellement `C:/dev/horoscope_front/frontend/src/i18n/admin.ts` si des labels de filtres ou de panneaux doivent etre centralises
- Si le detail catalogue devient assez gros pour etre extrait, preferer un composant dedie sous `frontend/src/pages/admin/` plutot qu un composant generique premature.

### Testing Requirements

- Mettre a jour la couverture Vitest pour verifier:
  - la presence d une liste catalogue et d un detail a cote sur desktop logique
  - les 5 colonnes visibles attendues
  - la reinitialisation des filtres
  - la persistance de la selection courante et l affichage du detail
  - le repli en experience mono-colonne via assertions de structure / classes si le test visuel complet n est pas raisonnable
- Attention: les tests existants de `AdminPromptsPage` et `AdminPromptsRouting` ont deja ete ajustes par `70.1`. Les etendre, ne pas les casser inutilement. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]

### Previous Story Intelligence

- `70.1` a retire la navigation globale `Persona` et centralise le domaine sous `/admin/prompts` avec une sous-navigation locale. Cette story doit s inserer dans cette structure, pas la contourner.
- `70.1` a aussi rendu `useAdminLlmUseCases` conditionnel a l onglet `legacy`. Pour le catalogue, eviter d activer des requetes non necessaires par simple presence de composants caches.
- Les correctifs de revue de `70.1` ont montre que les regressions les plus probables viennent des appels data inutiles et des titres/i18n non alignes sur la sous-route active. Garder cette vigilance sur le catalogue.
- Le fichier story `70.1` contient deja la liste de fichiers reels modifies; s en servir comme point de depart pour limiter le delta. [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]

### Implementation Guardrails

- `AdminPromptsPage.css` contient deja des bases inutilisees ou sous-utilisees pour un layout de type master-detail (`.admin-prompts-layout`, `.admin-prompts-sidebar`, `.admin-prompts-card`, `.admin-prompts-detail`). Les reutiliser en priorite plutot que recreer un nouveau systeme CSS. [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]
- Aujourd hui, la table catalogue a `min-width: 1100px` et beaucoup trop de colonnes pour l usage principal. La simplification doit toucher le JSX et la structure CSS, pas seulement masquer visuellement des colonnes au hasard.
- `selectedManifestEntryId` est deja utilise comme clef de selection. Le master-detail doit se construire autour de cette source de verite.
- Le detail resolved contient beaucoup de contenu dense. Dans cette story, l objectif est surtout le repositionnement ergonomique du detail dans un panneau stable. La pedagogie progressive complete arrive surtout en `70.3`.
- Respecter la regle projet: pas de styles inline; reutiliser les variables/tokens CSS existants. [Source: C:/dev/horoscope_front/AGENTS.md]

### UX Requirements

- La barre de filtres doit devenir scannable: labels visibles, reset clair, filtres avances repliables et etats actifs lisibles.
- Le catalogue doit privilegier la rapidite de lecture et la decision: colonnes limitees, detail contextualise, pas de scroll horizontal impose pour comprendre l essentiel.
- En mobile ou petit ecran, le detail doit rester accessible apres selection sans perdre le contexte. [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Requirements-Inventory, C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]

### Project Structure Notes

- Aucun `project-context.md` n a ete detecte dans le workspace.
- La story est strictement frontend/UX. Aucun changement backend n est attendu.

### References

- Epic 70 et story 70.2: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/epics.md#Epic-70]
- Story precedente 70.1 et intelligence implementation: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/70-1-reorganiser-la-navigation-admin-prompts-en-routes-dediees.md]
- Architecture frontend: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- UX responsive/accessibilite: [Source: C:/dev/horoscope_front/_bmad-output/planning-artifacts/ux-design-specification.md#Responsive-Design--Accessibility]
- Non-regression 67-69: [Source: C:/dev/horoscope_front/_bmad-output/implementation-artifacts/67-To-69-deferred-work.md]
- Implementation actuelle catalogue/detail: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.tsx]
- Styles actuels admin prompts: [Source: C:/dev/horoscope_front/frontend/src/pages/admin/AdminPromptsPage.css]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Recent git context:
  - `33a2831c feat(admin): story 70.1 — routes prompts dédiées et correctifs revue`
  - `43c18fec docs(67-69): artefact non-régression + epics; tests intégration et Vitest alignés`
  - `79ee3af3 feat(admin-llm): clôturer 67-69 deferred work, facettes samples et placeholders`
  - `5bab55a1 fix(admin): share execute-sample route template for manual header`
  - `e9bd389e feat(admin): story 69.3 — exécution manuelle LLM sécurisée et QA`

### Completion Notes List

- Story creee apres implementation reelle de `70.1`, avec reprise des garde-fous de routage, de data-loading conditionnel et d i18n.
- Story centree sur la transformation UX du catalogue uniquement, sans glisser vers la refonte pedagogique complete du detail ni vers les routes secondaires.
- **Implémentation (2026-04-18)** : layout `admin-prompts-catalog-master-detail` (liste + panneau sticky), tableau à 5 colonnes, filtres avec labels / liste d’état actif / section « Filtres avancés » repliable / « Réinitialiser les filtres », résumé de cible au-dessus du détail résolu, sélection par ligne + état visuel ; CSS dans `AdminPromptsPage.css` ; tests Vitest étendus (colonnes, panneau détail, reset).
- **Revue code (2026-04-18)** : correctifs appliqués — activation clavier des lignes catalogue (`tabIndex`, Entrée/Espace, `aria-selected`, focus visible), reset qui referme les filtres avancés, test sur le conteneur master-detail ; story passée en `done`.
- **Revue code — 2ᵉ passe (2026-04-18)** : aucun nouveau finding ; périmètre fonctionnel et AC validés sur l’état courant du code.

### File List

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `_bmad-output/implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md`

### Change Log

- 2026-04-18 : Implémentation master-detail catalogue admin + mise à jour tests et sprint (`70-2` → review).
- 2026-04-18 : Revue code — correctifs patch (a11y clavier ligne, reset + filtres avancés, test conteneur master-detail) ; statut `done`.
- 2026-04-18 : Revue code — 2ᵉ passe : clean ; documentation artefact / epics alignées ; prêt livraison git.
