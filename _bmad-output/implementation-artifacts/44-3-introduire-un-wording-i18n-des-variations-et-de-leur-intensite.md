# Story 44.3: Introduire un wording i18n des variations et de leur intensité

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want traduire les variations de mouvement via i18n à partir des valeurs structurées,
so that les moments clés restent compréhensibles en plusieurs langues sans figer des phrases quantitatives dans le backend.

## Acceptance Criteria

1. Le frontend introduit des clés i18n dédiées pour `direction`, `strength`, `delta` et les formulations de montée, recul, stabilité ou redistribution.
2. Le wording sait produire une version qualitative sobre (`léger`, `net`, `marqué`) sans exposer obligatoirement les chiffres bruts.
3. Les helpers i18n gèrent FR et EN à partir du même payload structuré.
4. Les valeurs numériques éventuelles sont formatées côté frontend selon la locale et jamais concaténées en dur.
5. Les règles de formulation évitent les contradictions du type “ça change” alors que les catégories visibles restent identiques faute de contexte.

## Tasks / Subtasks

- [ ] Task 1: Définir les nouvelles clés i18n des variations (AC: 1, 2)
  - [ ] Ajouter les libellés de direction `upshift`, `downshift`, `redistribution`
  - [ ] Ajouter les niveaux d'intensité qualitative
  - [ ] Ajouter les labels des variations locales par catégorie

- [ ] Task 2: Étendre les helpers de composition linguistique (AC: 2, 3, 4, 5)
  - [ ] Introduire des helpers purs pour humaniser `movement` et `category_deltas`
  - [ ] Supporter un rendu qualitatif sans chiffres et un rendu enrichi si des valeurs sont affichées
  - [ ] Centraliser le formatage localisé des nombres

- [ ] Task 3: Prévoir des fallbacks cohérents (AC: 3, 5)
  - [ ] Gérer les payloads sans `movement`
  - [ ] Gérer les payloads avec mouvement global mais sans `category_deltas`
  - [ ] Éviter les formulations contradictoires ou redondantes avec la transition existante

## Dev Notes

- Cette story étend l'approche i18n de 43.2.
- Le backend fournit les valeurs structurées; le frontend produit toutes les phrases finales.
- Les helpers doivent rester petits, testables et sans duplication FR/EN hors dictionnaires.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/i18n/predictions.ts`
  - `frontend/src/types/dailyPrediction.ts`

### Technical Requirements

- Aucune chaîne de variation ne doit être assemblée en dur dans les composants.
- Le formatage des nombres doit passer par les utilitaires localisés existants si le projet en dispose.
- Les niveaux qualitatifs doivent être stables pour la QA.

### Architecture Compliance

- La localisation reste côté frontend.
- Les composants consomment des helpers de présentation, pas des règles métier inline.

### Testing Requirements

- Ajouter des tests FR et EN sur les nouvelles compositions.
- Vérifier les fallbacks sans valeurs.
- Vérifier la cohérence entre rendu qualitatif et rendu enrichi.

### Previous Story Intelligence

- Epic 43 a déjà centralisé la sémantique `Pourquoi / Transition / Implication`.
- Les régressions passées montrent qu'un wording trop pauvre masque les vrais changements, tandis qu'un wording trop direct crée des incohérences si le contexte manque.

### Git Intelligence Summary

- Les helpers i18n existants sont déjà le point de centralisation des moments clés enrichis.
- Il faut prolonger cette approche, pas réintroduire de la logique textuelle dans les composants.

### References

- [Source: frontend/src/utils/predictionI18n.ts]
- [Source: frontend/src/i18n/predictions.ts]
- [Source: frontend/src/types/dailyPrediction.ts]
- [Source: _bmad-output/implementation-artifacts/43-2-introduire-un-wording-i18n-pour-les-moments-cles.md]
- [Source: user request 2026-03-12 — “le wording doit etre gerer avec i18n pour les differentes langues”]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
