# Story 46.2: Refondre le wizard et le modèle de données des consultations sans tirage

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want retirer la notion de tirage du wizard, du modèle de données et de la page résultat,
so that `/consultations` devienne un vrai parcours de guidance astrologique ciblée, cohérent pour l'utilisateur et maintenable pour l'équipe.

## Acceptance Criteria

1. Le wizard consultations n'expose plus l'étape `drawing` et suit un parcours `type -> astrologue -> demande`.
2. Le modèle frontend `ConsultationDraft` ne contient plus `drawingOption` et capture à la place les champs nécessaires à une demande ciblée, au minimum `situation`, `objective` et `timeHorizon` optionnel.
3. Le modèle frontend `ConsultationResult` ne contient plus `drawingOption` ni `drawing`; il expose les données nécessaires au rendu d'une guidance contextuelle.
4. La page résultat n'affiche plus de section cartes/runes ni de texte lié au tirage; elle affiche le type, l'astrologue, la demande, le résumé de guidance, les points clés et les conseils actionnables.
5. Les composants du wizard restent réutilisables, accessibles au clavier et cohérents avec les patterns établis dans la story 16.5.
6. Les constantes et helpers centralisés (`WIZARD_STEPS`, `WIZARD_STEP_LABELS`, configs de type, limites de contexte) sont mises à jour sans duplication.
7. Les tests frontend couvrent le nouveau wizard à 3 étapes, la validation du modèle refondu et l'absence de tout rendu `tarot/runes/cards/drawing` sur la page résultat.

## Tasks / Subtasks

- [ ] Task 1: Redéfinir le contrat de données frontend des consultations (AC: 2, 3, 6)
  - [ ] Remplacer `DrawingOption` et les structures associées dans `frontend/src/types/consultation.ts`
  - [ ] Introduire un modèle de draft orienté demande: `situation`, `objective`, `timeHorizon`
  - [ ] Introduire un modèle de résultat centré guidance: résumé, points clés, conseils, disclaimer, métadonnées utiles
  - [ ] Réviser `WIZARD_STEPS`, `WIZARD_LAST_STEP_INDEX` et `WIZARD_STEP_LABELS`

- [ ] Task 2: Refondre le store consultation pour le nouveau modèle (AC: 1, 2, 3, 6)
  - [ ] Supprimer `SET_DRAWING_OPTION` et toute logique liée à `drawingOption`
  - [ ] Ajouter les actions nécessaires pour `objective` et `timeHorizon` si elles n'existent pas encore
  - [ ] Mettre à jour `INITIAL_DRAFT` et `canProceed` selon les nouvelles règles métier
  - [ ] Préparer les points d'extension nécessaires à la migration de localStorage traitée dans 46.3

- [ ] Task 3: Refondre les composants du wizard autour d'une demande ciblée (AC: 1, 5, 6)
  - [ ] Retirer `DrawingOptionStep` du parcours
  - [ ] Soit adapter `ValidationStep`, soit introduire un composant explicite de demande qui collecte `situation`, `objective` et `timeHorizon`
  - [ ] Conserver la progression visuelle, les boutons `Précédent`/`Suivant` et les garde-fous d'accessibilité
  - [ ] Vérifier que la saisie reste concise et alignée avec les types `dating`, `pro`, `event`, `free`

- [ ] Task 4: Refondre le rendu de la page résultat (AC: 3, 4, 5)
  - [ ] Supprimer le rendu conditionnel de `currentResult.drawing`
  - [ ] Afficher les champs de demande au lieu du bloc de tirage
  - [ ] Structurer le résultat autour d'un résumé, de points clés et de conseils
  - [ ] Conserver les actions `Ouvrir dans le chat`, `Sauvegarder`, `Retour aux consultations`

- [ ] Task 5: Nettoyer l'i18n consultations et les labels wizard de premier niveau (AC: 1, 4, 6)
  - [ ] Supprimer ou remplacer les clés `step_drawing`, `select_drawing`, `drawing_none`, `drawing_tarot`, `drawing_runes`, `drawing_completed`
  - [ ] Ajouter les nouveaux libellés de demande ciblée et de résultat guidance
  - [ ] Vérifier la parité FR/EN/ES

- [ ] Task 6: Couvrir la refonte par des tests ciblés (AC: 1, 2, 3, 4, 7)
  - [ ] Ajouter des tests de progression sur 3 étapes
  - [ ] Ajouter des tests store/types pour le nouveau contrat
  - [ ] Ajouter un test garantissant l'absence de rendu cartes/runes dans le résultat
  - [ ] Vérifier les états d'accessibilité déjà couverts par la story 16.5 après refonte

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
  - `frontend/src/tests/`

### Technical Requirements

- Pas de duplication de logique entre composants et store.
- Les types `ConsultationType` existants doivent être conservés.
- Le résultat doit être pensé pour consommer la réponse contextual guidance, pas pour simuler un tirage.
- Les libellés et étapes doivent rester pilotés par des constantes centralisées.

### Architecture Compliance

- Garder la séparation entre types, store, composants et pages.
- Rester compatible avec la route `/consultations`.
- Conserver les actions principales et les patterns d'accessibilité établis.

### Testing Requirements

- Mettre à jour les tests du wizard, du store et de la page résultat.
- S'assurer qu'aucun snapshot ou assertion textuelle ne continue à dépendre de `tirage`, `cartes`, `runes`, `drawing`.
- Vérifier la cohérence des labels d'étapes et l'état `canProceed`.

### References

- [Source: frontend/src/types/consultation.ts]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/i18n/consultations.ts]
- [Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]
- [Source: _bmad-output/implementation-artifacts/46-1-rebrancher-les-consultations-ciblees-sur-la-guidance-contextuelle.md]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

### Completion Notes List

### File List
