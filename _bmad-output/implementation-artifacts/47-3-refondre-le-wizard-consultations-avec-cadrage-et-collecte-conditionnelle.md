# Story 47.3: Refondre le wizard consultations avec cadrage et collecte conditionnelle

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a consultations UX engineer,
I want transformer le wizard `/consultations/new` en parcours de cadrage et de collecte conditionnelle,
so that l'utilisateur ne saisisse que les informations nécessaires à la consultation choisie, avec une expérience cohérente avec le précheck et sans friction inutile.

## Acceptance Criteria

1. Le wizard consultations n'impose plus un choix d'astrologue comme étape bloquante de génération; si cette donnée est conservée, elle devient optionnelle ou purement liée à l'ouverture dans le chat.
2. Le parcours demande au minimum le type de consultation, la question / situation et l'horizon utile, puis affiche uniquement les compléments requis par le précheck et le type de consultation.
3. Le module "autre personne" n'apparaît que pour les parcours qui l'exigent, au minimum `relation`, accepte explicitement le cas "heure inconnue" et explicite que ces données sont utilisées pour le draft / run courant sans introduire de persistance backend dédiée en epic 47.
4. Le lieu de naissance d'un tiers suit le même protocole que le thème natal: saisie `ville + pays`, tentative `geocoding/search -> geocoding/resolve`, propagation de `birth_place`, `birth_city`, `birth_country`, `place_resolved_id`, `birth_lat`, `birth_lon` quand la résolution aboutit, et fallback dégradé non bloquant si elle échoue.
5. Les compléments utilisateur se limitent aux champs manquants pertinents; les données déjà connues ne sont pas redemandées.
6. Le wizard gère les choix "je ne connais pas cette information" et prépare un basculement vers un mode dégradé plutôt qu'un abandon brutal.
7. Les invariants du module consultations restent centralisés (`WIZARD_STEPS`, `canProceed`, draft state, deep links), et les tests couvrent les étapes dynamiques principales.

## Tasks / Subtasks

- [x] Task 1: Redéfinir la structure du draft et des étapes du wizard (AC: 1, 2, 6)
  - [x] Remplacer le flux `type -> astrologer -> validation` par un flux consultation-complete piloté par état métier
  - [x] Étendre `ConsultationDraft` pour la question, l'horizon, les compléments utilisateur et les données tiers
  - [x] Maintenir une source unique pour les étapes et règles `canProceed`

- [x] Task 2: Intégrer le précheck et l'affichage des besoins de collecte (AC: 2, 4, 5)
  - [x] Brancher l'état de précheck dans `ConsultationWizardPage`
  - [x] Afficher les champs manquants et le niveau de précision avant génération
  - [x] Éviter toute duplication de règle métier déjà calculée côté backend

- [x] Task 3: Construire la collecte conditionnelle consultation-centric (AC: 3, 4, 5)
  - [x] Ajouter un composant ou sous-flux pour les compléments utilisateur
  - [x] Ajouter un composant "autre personne" dédié au parcours relationnel
  - [x] Gérer la saisie "heure inconnue" et les états de validation minimaux
  - [x] Rendre explicite la règle MVP de gouvernance: pas de persistance backend dédiée des données tiers, seulement un usage à la volée dans le draft / run
  - [x] Réutiliser les clients API existants (`birthProfile`, `geocoding`) sans toucher au flow `/profile`
  - [x] Aligner la saisie du lieu tiers sur le protocole natal (`birth_city`, `birth_country`, géocodage, `place_resolved_id`, `birth_lat`, `birth_lon`)

- [x] Task 4: Réorganiser les composants UI sans régression (AC: 1, 6)
  - [x] Adapter `WizardProgress`, `ValidationStep` (repurposed as FrameStep) et le layout consultations
  - [x] Retirer les hypothèses codées en dur sur trois étapes fixes
  - [x] Conserver l'accessibilité clavier et les boutons précédents / suivants / annuler

- [x] Task 5: Tester les scénarios dynamiques essentiels (AC: 3, 4, 5, 6)
  - [x] Ajouter des scénarios de progression dynamique dans les tests frontend
  - [x] Vérifier que le choix d'astrologue n'est plus un bloquant artificiel

## Dev Notes

- Wizard refactored from 3 to 4 steps: `type` -> `frame` -> `collection` -> `summary`.
- `OtherPersonForm` added for `relation` type.
- `OtherPersonForm` aligne le lieu tiers sur le protocole natal de géocodage: saisie `ville/pays`, résolution de lieu et fallback dégradé non bloquant.
- Astrologer selection moved to `summary` step and made optional.
- Precheck integrated to inform user about precision and missing data.

### Previous Story Intelligence

- Story 47.2 provided the `useConsultationPrecheck` hook used here.
- Story 47.1 defined the new taxonomy used for conditional logic.

### Project Structure Notes

- New components in `frontend/src/features/consultations/components/`:
  - `ConsultationFrameStep.tsx`
  - `DataCollectionStep.tsx`
  - `ConsultationSummaryStep.tsx`
  - `OtherPersonForm.tsx`
- Modified files:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/i18n/consultations.ts`

### Technical Requirements

- State management via `consultationStore` preserved.
- React Query mutation used for precheck.
- Type safety for `OtherPersonDraft`.

### Architecture Compliance

- Logic for "what's missing" comes from backend precheck.
- Optional astrologer aligns with `guidance_contextual` requirement.

### Testing Requirements

- Verified with 6 tests covering the new flow.

### References

- [Source: docs/backlog_epics_consultation_complete.md#7-epic-cc-03-collecte-conditionnelle-des-donnees-manquantes]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Wizard refactor to 4 steps successful.
- Conditional data collection for relational consultations implemented.
- Tests updated and passing (6/6).

### Completion Notes List

- Redefined `WIZARD_STEPS` and `ConsultationDraft`.
- Implemented `ConsultationFrameStep`, `DataCollectionStep`, `ConsultationSummaryStep`, and `OtherPersonForm`.
- Updated `ConsultationWizardPage` to handle new steps and conditional logic.
- Verified astrologer selection is optional and not blocking.

### File List

- `frontend/src/types/consultation.ts`
- `frontend/src/state/consultationStore.tsx`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/features/consultations/index.ts`
- `frontend/src/features/consultations/components/ConsultationFrameStep.tsx`
- `frontend/src/features/consultations/components/DataCollectionStep.tsx`
- `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
- `frontend/src/features/consultations/components/OtherPersonForm.tsx`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Initial implementation of story 47.3. Conditional wizard refactor.
- 2026-03-13: Alignement du lieu de naissance tiers sur le protocole natal (`birth_city` / `birth_country` -> `search` / `resolve` -> `place_resolved_id` + `birth_lat` / `birth_lon`).
