# Story 46.3: Migrer l'historique local et préserver l'ouverture dans le chat

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend maintainer,
I want migrer proprement l'historique local des consultations vers le nouveau schéma sans tirage,
so that les utilisateurs conservent leurs consultations passées et peuvent toujours ouvrir une guidance dans le chat sans régression.

## Acceptance Criteria

- [x] AC1: Le store consultation accepte encore en lecture les anciennes entrées localStorage contenant `drawingOption` et/ou `drawing`, sans planter ni les rejeter silencieusement si elles sont autrement valides.
- [x] AC2: Une migration de lecture normalise ces anciennes entrées vers le schéma cible de l'epic 46 et supprime les notions de tirage du modèle runtime.
- [x] AC3: Les nouvelles écritures dans le localStorage utilisent uniquement le schéma de consultation sans tirage.
- [x] AC4: L'historique affiché dans `/consultations` reste lisible après migration et les entrées préexistantes restent consultables via `?id=...`.
- [x] AC5: Le bouton `Ouvrir dans le chat` continue de préremplir le message via `CHAT_PREFILL_KEY`, avec un contenu fondé sur la guidance contextuelle et non sur un tirage.
- [x] AC6: Les tests frontend couvrent:
   - [x] lecture d'un ancien historique
   - [x] écriture du nouveau schéma
   - [x] ouverture dans le chat depuis une consultation migrée
   - [x] absence de casse sur les cas de données invalides ou partielles

## Tasks / Subtasks

- [x] Task 1: Définir la stratégie de compatibilité de schéma (AC: 1, 2, 3)
  - [x] Documenter le schéma legacy actuellement produit par `consultationStore`
  - [x] Définir un schéma runtime cible sans `drawingOption` ni `drawing`
  - [x] Définir les règles de normalisation minimales pour les anciennes entrées

- [x] Task 2: Mettre à jour le chargement et la validation du localStorage (AC: 1, 2, 3, 4)
  - [x] Adapter `isValidConsultationResult` ou introduire un validateur legacy + normaliseur
  - [x] Conserver les garde-fous contre JSON invalide, pollution prototype et dates invalides
  - [x] Garantir qu'une entrée legacy valide soit relue, convertie et conservée dans l'historique runtime
  - [x] Garantir que les nouvelles sauvegardes sérialisent uniquement le schéma v2

- [x] Task 3: Préserver le rendu d'historique et les deep links résultat (AC: 2, 4)
  - [x] Vérifier que `ConsultationsPage` et `ConsultationResultPage` tolèrent les entrées migrées
  - [x] Vérifier que `historyId` continue à retrouver une entrée migrée
  - [x] Prévoir un fallback lisible si certaines anciennes métadonnées sont absentes

- [x] Task 4: Mettre à jour le préremplissage chat sans sémantique tirage (AC: 5)
  - [x] Revoir la composition du message `CHAT_PREFILL_KEY`
  - [x] Inclure la demande, le résumé ou les éléments actionnables utiles
  - [x] Exclure toute mention `tirage`, `carte`, `rune` du message généré
  - [x] Conserver le paramètre astrologerId quand il est pertinent

- [x] Task 5: Tester explicitement la migration et le chat prefill (AC: 1, 2, 3, 4, 5, 6)
  - [x] Ajouter des fixtures localStorage legacy
  - [x] Ajouter des assertions sur la forme écrite du nouveau schéma
  - [x] Ajouter un test d'ouverture chat depuis une entrée legacy migrée
  - [x] Garder les tests de robustesse sur JSON corrompu et dates invalides

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- normalizeConsultationResult added to consultationStore.tsx.
- ConsultationMigration.test.tsx created to verify normalization and chat prefill.
- Cleaned up ConsultationResultPage.tsx from legacy field usage.

### Completion Notes List

- Implemented a robust normalizer for legacy consultation history.
- Normalized legacy fields (interpretation -> summary) and removed drawing concepts.
- Updated chat prefill to use new structured guidance data.
- Verified that historical links and history list remain functional.

### File List

- frontend/src/state/consultationStore.tsx
- frontend/src/pages/ConsultationResultPage.tsx
- frontend/src/tests/ConsultationMigration.test.tsx
