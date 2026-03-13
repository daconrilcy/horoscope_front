# Story 47.1: Redéfinir le catalogue produit et la taxonomie des consultations complètes

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product-facing frontend architect,
I want réaligner `/consultations` sur la taxonomie MVP de la consultation complète,
so that le parcours expose les bons types de consultation sans casser la route, l'historique existant ni les deep links hérités de l'epic 46.

## Acceptance Criteria

1. Le catalogue visible de `/consultations` expose des types MVP alignés avec `docs/backlog_epics_consultation_complete.md`, au minimum `period`, `work`, `orientation`, `relation`, `timing`.
2. Les identifiants de types de consultation sont stabilisés dans un contrat consultation dédié, et les anciens types `dating`, `pro`, `event`, `free` restent lisibles en historique mais ne sont plus créables.
3. Chaque type visible déclare explicitement son `label`, sa promesse UX courte, ses besoins de données minimaux et son mode nominal / dégradé attendu.
4. La route `/consultations` ainsi que les deep links `/consultations/new` et `/consultations/result?id=...` restent stables.
5. Le catalogue ne réintroduit pas de sémantique obsolète du parcours 46 et n'implique pas de changement hors du code consultations courant.
6. Les tests frontend couvrent le nouveau catalogue, la compatibilité d'affichage des historiques legacy et l'absence de régression sur la navigation consultations.

## Tasks / Subtasks

- [x] Task 1: Définir le référentiel consultation MVP dans le module consultations (AC: 1, 2, 3)
  - [x] Remplacer la taxonomie `dating/pro/event/free` dans le flux de création par des IDs stables consultation complète
  - [x] Introduire une structure de config capable de porter `labelKey`, promesse UX, exigences de données et drapeaux de fallback
  - [x] Prévoir un statut explicite pour les types legacy afin de les garder lisibles en historique sans les proposer à la création

- [x] Task 2: Réaligner la landing `/consultations` et les labels history/result (AC: 1, 3, 4)
  - [x] Mettre à jour `ConsultationsPage` et `i18n/consultations.ts`
  - [x] Vérifier que la liste de preview et les CTA reflètent le nouveau périmètre
  - [x] Conserver la lecture des anciens items via leur mapping de label legacy

- [x] Task 3: Préparer le contrat pour les stories suivantes sans dupliquer la logique métier (AC: 2, 3, 5)
  - [x] Centraliser le mapping type -> besoin minimal dans `frontend/src/types/consultation.ts` ou un module voisin consultation-centric
  - [x] Éviter de disperser des conditions métier dans les composants UI
  - [x] Laisser le calcul effectif de qualité / fallback à la future couche backend consultation

- [x] Task 4: Verrouiller la compatibilité legacy et les tests (AC: 2, 4, 6)
  - [x] Mettre à jour les tests de page consultations pour les nouveaux types
  - [x] Ajouter un test qui vérifie qu'un historique legacy reste lisible même si son type n'est plus créable
  - [x] Vérifier que les liens existants `/consultations/new` et `/consultations/result` restent inchangés

## Dev Notes

- Le backlog de référence ne parle plus du découpage `dating/pro/event/free`; cette taxonomie doit devenir un héritage de lecture, pas un pivot produit.
- Le code actuel centralise déjà les types et labels dans `frontend/src/types/consultation.ts` et `frontend/src/i18n/consultations.ts`. Il faut étendre ce socle plutôt que recréer un second catalogue ailleurs.
- La story ne doit pas encore implémenter le précheck ni les fallbacks métier; elle prépare leur point d'ancrage sans inventer la logique côté frontend.

### Previous Story Intelligence

- L'epic 46 a stabilisé la route `/consultations` et l'historique local; ces invariants doivent rester intacts.
- `normalizeConsultationResult` gère déjà le legacy 16.5 -> 46.x. La nouvelle taxonomie doit s'y brancher sans casser les anciens objets.
- Le wizard actuel reste trop centré sur l'ancien flux. Cette story ne doit pas le réécrire entièrement; elle fige d'abord le vocabulaire produit.

### Project Structure Notes

- Fichiers principalement concernés:
  - `frontend/src/types/consultation.ts`
  - `frontend/src/i18n/consultations.ts`
  - `frontend/src/pages/ConsultationsPage.tsx`
  - `frontend/src/state/consultationStore.tsx`
  - `frontend/src/tests/ConsultationsPage.test.tsx`
  - `frontend/src/tests/consultationStore.test.ts`

### Technical Requirements

- Le catalogue doit distinguer clairement les types créables des types legacy de lecture.
- Aucun composant hors consultations ne doit dépendre directement de la nouvelle taxonomie.
- Les labels et règles de type doivent rester centralisés et testables.

### Architecture Compliance

- Respecter la structure frontend existante: types / store / pages / tests.
- Ne pas déplacer la source de vérité consultation vers `dashboard`, `chat` ou `astrologers`.
- Préserver le contrat de route existant et la persistance locale déjà en place.

### Testing Requirements

- Mettre à jour les tests du catalogue `/consultations`.
- Ajouter un test de lecture d'un ancien item `dating/pro/event/free`.
- Vérifier l'absence de casse sur les raccourcis et deep links consultations.

### References

- [Source: docs/backlog_epics_consultation_complete.md#5-epic-cc-01-catalogue-produit-et-taxonomie-de-consultation]
- [Source: docs/backlog_epics_consultation_complete.md#13-epic-cc-09-integration-ux-front-de-lexperience-end-to-end]
- [Source: _bmad-output/planning-artifacts/epic-47-consultation-complete-depuis-consultations.md]
- [Source: _bmad-output/implementation-artifacts/46-2-refondre-le-wizard-et-le-modele-de-donnees-des-consultations-sans-tirage.md]
- [Source: _bmad-output/implementation-artifacts/46-3-migrer-l-historique-local-et-preserver-l-ouverture-dans-le-chat.md]
- [Source: frontend/src/types/consultation.ts]
- [Source: frontend/src/pages/ConsultationsPage.tsx]
- [Source: frontend/src/state/consultationStore.tsx]

## Dev Agent Record

### Agent Model Used

Gemini CLI

### Debug Log References

- Story implémentée avec succès.
- Taxonomie mise à jour: period, work, orientation, relation, timing.
- Support legacy préservé pour dating, pro, event, free.
- Tests mis à jour et passants (33/33).

### Completion Notes List

- Redéfinition de la taxonomie dans `types/consultation.ts`.
- Mise à jour des traductions et promesses UX dans `i18n/consultations.ts`.
- Filtrage des types legacy dans la page de garde et le wizard.
- Mise à jour exhaustive des tests pour couvrir les nouveaux types et la compatibilité legacy.

### File List

- `frontend/src/types/consultation.ts`
- `frontend/src/i18n/consultations.ts`
- `frontend/src/pages/ConsultationsPage.tsx`
- `frontend/src/features/consultations/components/ConsultationTypeStep.tsx`
- `frontend/src/tests/ConsultationsPage.test.tsx`

## Change Log

- 2026-03-13: Initial implementation of story 47.1. New taxonomy and legacy support.
