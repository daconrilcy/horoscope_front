# Story 47.3: Refondre le wizard consultations avec cadrage et collecte conditionnelle

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultations UX engineer,
I want transformer le wizard `/consultations/new` en parcours de cadrage et de collecte conditionnelle,
so that l'utilisateur ne saisisse que les informations nécessaires à la consultation choisie, avec une expérience cohérente avec le précheck et sans friction inutile.

## Acceptance Criteria

1. Le wizard consultations n'impose plus un choix d'astrologue comme étape bloquante de génération; si cette donnée est conservée, elle devient optionnelle ou purement liée à l'ouverture dans le chat.
2. Le parcours demande au minimum le type de consultation, la question / situation et l'horizon utile, puis affiche uniquement les compléments requis par le précheck et le type de consultation.
3. Le module "autre personne" n'apparaît que pour les parcours qui l'exigent, au minimum `relation`, accepte explicitement le cas "heure inconnue" et explicite que ces données sont utilisées pour le draft / run courant sans introduire de persistance backend dédiée en epic 47.
4. Les compléments utilisateur se limitent aux champs manquants pertinents; les données déjà connues ne sont pas redemandées.
5. Le wizard gère les choix "je ne connais pas cette information" et prépare un basculement vers un mode dégradé plutôt qu'un abandon brutal.
6. Les invariants du module consultations restent centralisés (`WIZARD_STEPS`, `canProceed`, draft state, deep links), et les tests couvrent les étapes dynamiques principales.

## Tasks / Subtasks

- [ ] Task 1: Redéfinir la structure du draft et des étapes du wizard (AC: 1, 2, 6)
  - [ ] Remplacer le flux `type -> astrologer -> validation` par un flux consultation-complete piloté par état métier
  - [ ] Étendre `ConsultationDraft` pour la question, l'horizon, les compléments utilisateur et les données tiers
  - [ ] Maintenir une source unique pour les étapes et règles `canProceed`

- [ ] Task 2: Intégrer le précheck et l'affichage des besoins de collecte (AC: 2, 4, 5)
  - [ ] Brancher l'état de précheck dans `ConsultationWizardPage`
  - [ ] Afficher les champs manquants et le niveau de précision avant génération
  - [ ] Éviter toute duplication de règle métier déjà calculée côté backend

- [ ] Task 3: Construire la collecte conditionnelle consultation-centric (AC: 3, 4, 5)
  - [ ] Ajouter un composant ou sous-flux pour les compléments utilisateur
  - [ ] Ajouter un composant "autre personne" dédié au parcours relationnel
  - [ ] Gérer la saisie "heure inconnue" et les états de validation minimaux
  - [ ] Rendre explicite la règle MVP de gouvernance: pas de persistance backend dédiée des données tiers, seulement un usage à la volée dans le draft / run
  - [ ] Réutiliser les clients API existants (`birthProfile`, `geocoding`) sans toucher au flow `/profile`

- [ ] Task 4: Réorganiser les composants UI sans régression (AC: 1, 6)
  - [ ] Adapter `WizardProgress`, `ValidationStep` et le layout consultations
  - [ ] Retirer les hypothèses codées en dur sur trois étapes fixes
  - [ ] Conserver l'accessibilité clavier et les boutons précédents / suivants / annuler

- [ ] Task 5: Tester les scénarios dynamiques essentiels (AC: 3, 4, 5, 6)
  - [ ] Ajouter un scénario mono-profil avec profil déjà complet
  - [ ] Ajouter un scénario utilisateur sans heure de naissance
  - [ ] Ajouter un scénario relation avec autre personne et heure inconnue
  - [ ] Vérifier que le choix d'astrologue n'est plus un bloquant artificiel

## Dev Notes

- Le backlog consultation complète n'inclut pas une étape persona / astrologer dans la logique métier. Le code actuel, lui, la rend bloquante alors que `guidance_contextual` ne la consomme pas. Cette dette doit être corrigée ici.
- La collecte conditionnelle doit vivre dans le code consultations. Éviter un refactor transverse de `BirthProfilePage` si cela élargit le scope.
- Les règles de validation doivent rester simples, explicites et centrées sur les champs réellement requis par consultation.
- Gouvernance MVP des données tiers: les champs bruts saisis pour "autre personne" restent limités au draft courant et au payload de génération; aucune persistance backend dédiée n'est introduite dans l'epic 47. Si un résultat est sauvegardé localement, il ne doit conserver que les métadonnées minimales nécessaires au réaffichage, pas un second profil tiers complet.

### Previous Story Intelligence

- La story 47.2 fournit la source de vérité sur `missing_fields`, `available_modes` et `precision_level`; le wizard ne doit pas re-déduire ces informations.
- L'epic 46 a déjà prouvé que les constantes centralisées du wizard sont un point de stabilité important.
- Le localStorage et la reprise de parcours dépendent fortement du store; toute refonte doit passer par lui plutôt que par des états locaux dispersés.

### Project Structure Notes

- Fichiers principalement concernés:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/features/consultations/components/*`
  - `frontend/src/api/consultations.ts`
  - `frontend/src/api/birthProfile.ts`
  - `frontend/src/api/geocoding.ts`
  - `frontend/src/tests/ConsultationsPage.test.tsx`
  - `frontend/src/tests/consultationStore.test.ts`

### Technical Requirements

- Ne pas recréer un second store local hors `consultationStore`.
- Le wizard doit tolérer des étapes dynamiques sans index magiques dispersés.
- Les champs tiers doivent être distincts des champs utilisateur dans le modèle de draft.
- La copie UI doit préciser quand une donnée tiers est utilisée uniquement pour cette consultation et non enregistrée comme profil global.

### Architecture Compliance

- La logique métier de complétude reste backend-driven.
- La logique d'UI conditionnelle reste dans le module consultations.
- Aucun changement requis dans le routeur global en dehors des pages consultations existantes.

### Testing Requirements

- Couvrir les scénarios dynamiques de progression.
- Couvrir les choix "heure inconnue" et "je ne sais pas".
- Préserver les garanties d'accessibilité déjà présentes sur les boutons et la progression.

### References

- [Source: docs/backlog_epics_consultation_complete.md#7-epic-cc-03-collecte-conditionnelle-des-donnees-manquantes]
- [Source: docs/backlog_epics_consultation_complete.md#13-epic-cc-09-integration-ux-front-de-lexperience-end-to-end]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: _bmad-output/implementation-artifacts/46-2-refondre-le-wizard-et-le-modele-de-donnees-des-consultations-sans-tirage.md]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/features/consultations/components/ValidationStep.tsx]
- [Source: frontend/src/api/birthProfile.ts]
- [Source: frontend/src/pages/BirthProfilePage.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 47 et du backlog consultation complète.

### Completion Notes List

- Artefact créé uniquement; aucun code applicatif n'a été modifié.
- La story retire explicitement le couplage artificiel entre génération consultation et choix d'astrologue.

### File List

- TBD pendant `dev-story`
