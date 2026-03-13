# Story 46.2: Refondre le wizard et le modèle de données des consultations sans tirage

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product designer,
I want simplifier le parcours utilisateur en retirant l'étape de tirage et en adoptant un modèle de données riche,
so that l'expérience soit plus fluide et les conseils plus structurés (points clés, conseils actionnables).

## Acceptance Criteria

- [x] AC1: L'étape "DrawingOptionStep" (choix tarot/runes) est supprimée du Wizard.
- [x] AC2: Le Wizard passe de 4 étapes à 3 étapes (Type -> Astrologer -> Validation).
- [x] AC3: Le modèle de données `ConsultationResult` est mis à jour pour inclure `summary`, `keyPoints`, `actionableAdvice` et `disclaimer`.
- [x] AC4: La page de résultat affiche ces nouveaux champs de manière structurée au lieu d'une simple chaîne de texte.
- [x] AC5: Le rendu des cartes/runes est supprimé de la page de résultat.
- [x] AC6: L'historique des consultations et le deep link supportent le nouveau modèle de données (avec fallback pour les anciens items).
- [x] AC7: Les tests frontend sont mis à jour pour refléter le nouveau parcours en 3 étapes.

## Tasks / Subtasks

- [x] Task 1: Redéfinir le contrat de données frontend (AC: 3)
  - [x] Modifier `frontend/src/types/consultation.ts` pour retirer `DrawingOption` et `DrawingResult`
  - [x] Mettre à jour `ConsultationDraft` et `ConsultationResult` avec les nouveaux champs structurés
  - [x] Mettre à jour `WIZARD_STEPS` et `WIZARD_STEP_LABELS`

- [x] Task 2: Refondre le store consultation pour le nouveau modèle (AC: 1, 2, 3, 6)
  - [x] Supprimer `SET_DRAWING_OPTION` et toute logique liée à `drawingOption`
  - [x] Ajouter les actions nécessaires pour `objective` et `timeHorizon` si elles n'existent pas encore
  - [x] Mettre à jour `INITIAL_DRAFT` et `canProceed` selon les nouvelles règles métier
  - [x] Préparer les points d'extension nécessaires à la migration de localStorage traitée dans 46.3

- [x] Task 3: Refondre les composants du wizard autour d'une demande ciblée (AC: 1, 5, 6)
  - [x] Retirer `DrawingOptionStep` du parcours
  - [x] Soit adapter `ValidationStep`, soit introduire un composant explicite de demande qui collecte `situation`, `objective` et `timeHorizon`
  - [x] Conserver la progression visuelle, les boutons `Précédent`/`Suivant` et les garde-fous d'accessibilité
  - [x] Vérifier que la saisie reste concise et alignée avec les types `dating`, `pro`, `event`, `free`

- [x] Task 4: Refondre le rendu de la page résultat (AC: 3, 4, 5)
  - [x] Supprimer le rendu conditionnel de `currentResult.drawing`
  - [x] Afficher les champs de demande au lieu du bloc de tirage
  - [x] Structurer le résultat autour d'un résumé, de points clés et de conseils
  - [x] Conserver les actions `Ouvrir dans le chat`, `Sauvegarder`, `Retour aux consultations`

- [x] Task 5: Nettoyer l'i18n consultations et les labels wizard de premier niveau (AC: 1, 4, 6)
  - [x] Supprimer ou remplacer les clés `step_drawing`, `select_drawing`, `drawing_none`, `drawing_tarot`, `drawing_runes`, `drawing_completed`
  - [x] Ajouter les nouveaux libellés de demande ciblée et de résultat guidance
  - [x] Vérifier la parité FR/EN/ES

- [x] Task 6: Couvrir la refonte par des tests ciblés (AC: 1, 2, 3, 4, 7)
  - [x] Ajouter des tests de progression sur 3 étapes
  - [x] Ajouter des tests store/types pour le nouveau contrat
  - [x] Ajouter un test garantissant l'absence de rendu cartes/runes dans le résultat
  - [x] Vérifier les états d'accessibilité déjà couverts par la story 16.5 après refonte

## Dev Notes

- Cette story dépend conceptuellement de 46.1: le flux de génération doit déjà être rebranché sur la guidance contextuelle, sinon le nouveau modèle UI n'a pas de source de vérité correcte.
- Le nettoyage doit être structurel. Il ne suffit pas de masquer l'étape `drawing`; il faut retirer les types, l'état, les helpers et les branches de rendu.
- Les abstractions déjà créées dans 16.5 sont utiles et doivent survivre: constantes du wizard, config de type, `AUTO_ASTROLOGER_ID`, `CHAT_PREFILL_KEY`, `classNames`, `generateUniqueId`, `formatDate`.

### Previous Story Intelligence

- Story 16.5 a beaucoup investi dans la centralisation DRY des constantes et helpers. Toute refonte doit s'appuyer sur ce socle et non réintroduire des strings magiques ou des étapes indexées en dur.
- Le store consultation a déjà des validations runtime et une logique `canProceed` stabilisée; il faut l'adapter plutôt que le réécrire.
- Les tests existants sont nombreux. Il faut mettre à jour les invariants sans perdre les protections utiles sur accessibilité, historique et navigation.

### Project Structure Notes

- Fichiers principalement concernés:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationWizardPage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/features/consultations/components/`
  - `frontend/src/i18n/consultations.ts`

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- ValidationStep.tsx cleaned up from drawing references.
- types/consultation.ts refactored to remove DrawingOption.
- ConsultationResultPage.tsx refactored for structured data.
- ConsultationsPage.test.tsx and ConsultationReconnection.test.tsx updated.

### Completion Notes List

- Removed DrawingOptionStep from Wizard and store.
- Updated data model to include summary, keyPoints, and actionableAdvice.
- Refactored result page UI to display structured guidance.
- Fixed existing tests to match 3-step wizard and new data structure.

### File List

- frontend/src/types/consultation.ts
- frontend/src/state/consultationStore.tsx
- frontend/src/pages/ConsultationWizardPage.tsx
- frontend/src/pages/ConsultationResultPage.tsx
- frontend/src/features/consultations/components/ValidationStep.tsx
- frontend/src/features/consultations/index.ts
- frontend/src/i18n/consultations.ts
- frontend/src/tests/ConsultationsPage.test.tsx
- frontend/src/tests/ConsultationReconnection.test.tsx
