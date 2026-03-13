# Story 46.3: Migrer l'historique local et préserver l'ouverture dans le chat

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend maintainer,
I want migrer proprement l'historique local des consultations vers le nouveau schéma sans tirage,
so that les utilisateurs conservent leurs consultations passées et peuvent toujours ouvrir une guidance dans le chat sans régression.

## Acceptance Criteria

1. Le store consultation accepte encore en lecture les anciennes entrées localStorage contenant `drawingOption` et/ou `drawing`, sans planter ni les rejeter silencieusement si elles sont autrement valides.
2. Une migration de lecture normalise ces anciennes entrées vers le schéma cible de l'epic 46 et supprime les notions de tirage du modèle runtime.
3. Les nouvelles écritures dans le localStorage utilisent uniquement le schéma de consultation sans tirage.
4. L'historique affiché dans `/consultations` reste lisible après migration et les entrées préexistantes restent consultables via `?id=...`.
5. Le bouton `Ouvrir dans le chat` continue de préremplir le message via `CHAT_PREFILL_KEY`, avec un contenu fondé sur la guidance contextuelle et non sur un tirage.
6. Les tests frontend couvrent:
   - lecture d'un ancien historique
   - écriture du nouveau schéma
   - ouverture dans le chat depuis une consultation migrée
   - absence de casse sur les cas de données invalides ou partielles

## Tasks / Subtasks

- [ ] Task 1: Définir la stratégie de compatibilité de schéma (AC: 1, 2, 3)
  - [ ] Documenter le schéma legacy actuellement produit par `consultationStore`
  - [ ] Définir un schéma runtime cible sans `drawingOption` ni `drawing`
  - [ ] Choisir si une clé de version explicite est ajoutée ou si la migration repose sur détection de forme
  - [ ] Définir les règles de normalisation minimales pour les anciennes entrées

- [ ] Task 2: Mettre à jour le chargement et la validation du localStorage (AC: 1, 2, 3, 4)
  - [ ] Adapter `isValidConsultationResult` ou introduire un validateur legacy + normaliseur
  - [ ] Conserver les garde-fous contre JSON invalide, pollution prototype et dates invalides
  - [ ] Garantir qu'une entrée legacy valide soit relue, convertie et conservée dans l'historique runtime
  - [ ] Garantir que les nouvelles sauvegardes sérialisent uniquement le schéma v2

- [ ] Task 3: Préserver le rendu d'historique et les deep links résultat (AC: 2, 4)
  - [ ] Vérifier que `ConsultationsPage` et `ConsultationResultPage` tolèrent les entrées migrées
  - [ ] Vérifier que `historyId` continue à retrouver une entrée migrée
  - [ ] Prévoir un fallback lisible si certaines anciennes métadonnées sont absentes

- [ ] Task 4: Mettre à jour le préremplissage chat sans sémantique tirage (AC: 5)
  - [ ] Revoir la composition du message `CHAT_PREFILL_KEY`
  - [ ] Inclure la demande, le résumé ou les éléments actionnables utiles
  - [ ] Exclure toute mention `tirage`, `carte`, `rune` du message généré
  - [ ] Conserver le paramètre astrologerId quand il est pertinent

- [ ] Task 5: Tester explicitement la migration et le chat prefill (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Ajouter des fixtures localStorage legacy
  - [ ] Ajouter des assertions sur la forme écrite du nouveau schéma
  - [ ] Ajouter un test d'ouverture chat depuis une entrée legacy migrée
  - [ ] Garder les tests de robustesse sur JSON corrompu et dates invalides

## Dev Notes

- Story 16.5 a déjà beaucoup renforcé la robustesse localStorage. Cette story doit préserver ces garanties et les étendre à une migration de forme.
- La migration doit être tolérante en lecture, stricte en écriture.
- Ne pas supprimer brutalement l'ancien historique: l'utilisateur ne doit pas perdre la consultation sauvegardée avant l'epic 46.
- L'ouverture dans le chat doit rester un bénéfice produit visible après la refonte; c'est un point de non-régression majeur.

### Previous Story Intelligence

- Story 16.5 a introduit `STORAGE_KEY`, `CHAT_PREFILL_KEY`, `isValidISODate`, `isValidDrawing`, `HISTORY_MAX_LENGTH` et une série de tests de sécurité localStorage. Réutiliser ce socle.
- Story 16.5 a aussi corrigé plusieurs bugs liés au `historyId` et à `isSaved`; la migration doit maintenir ce comportement.
- Story 46.2 redéfinit le modèle consultation. Cette story doit l'utiliser comme schéma cible et non inventer un deuxième modèle parallèle.

### Project Structure Notes

- Fichiers à inspecter et probablement modifier:
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/pages/ConsultationsPage.tsx`
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/tests/`

### Technical Requirements

- La migration doit être pure et testable.
- Le normaliseur legacy ne doit pas dépendre d'un composant React.
- Les nouvelles écritures doivent converger vers un seul format sérialisé.
- Le message stocké dans `CHAT_PREFILL_KEY` doit rester textuel, lisible et stable.

### Architecture Compliance

- La source de vérité historique reste `consultationStore`.
- Ne pas introduire une seconde clé localStorage ni un mécanisme de persistance concurrent.
- Maintenir la compatibilité avec les routes existantes et le shell chat.

### Testing Requirements

- Tests unitaires du store sur migration legacy -> v2.
- Tests d'intégration UI sur historique et `Ouvrir dans le chat`.
- Vérifier qu'une donnée invalide reste filtrée proprement au lieu de polluer l'historique.

### References

- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/pages/ConsultationsPage.tsx]
- [Source: frontend/src/types/consultation.ts]
- [Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]
- [Source: _bmad-output/implementation-artifacts/46-2-refondre-le-wizard-et-le-modele-de-donnees-des-consultations-sans-tirage.md]

## Dev Agent Record

### Agent Model Used

TBD

### Debug Log References

### Completion Notes List

### File List
