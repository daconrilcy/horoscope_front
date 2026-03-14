# Story 55.2: Séparer les composants de prédiction (DayPredictionCard, CategoryGrid)

Status: done

## Story

En tant que développeur frontend,
je veux que `DayPredictionCard` et `CategoryGrid` soient séparés en hook de données et composant présentationnel,
afin de pouvoir tester leur rendu avec des données mockées sans appel API.

## Acceptance Criteria

1. `DayPredictionCard.tsx` ne contient plus de logique de fetching — il reçoit `prediction`, `isLoading`, `error` en props.
2. Un hook `useDayPrediction.ts` gère le fetching et les états.
3. `CategoryGrid` suit le même pattern si elle contient de la logique de données (déjà purement présentationnel).
4. Un composant `DayPredictionCardContainer` assemble hook + composant.
5. Le rendu visuel est identique avant/après.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `DayPredictionCard.tsx` (AC: 1, 2)
  - [x] Identifier les props nécessaires : prediction, lang, isLoading, isError, onRetry, astroBackgroundProps.

- [x] Tâche 2 : Créer `useDayPrediction.ts` (AC: 2)
  - [x] Créer `frontend/src/hooks/useDayPrediction.ts` comme wrapper simplifié de `useDailyPrediction`.

- [x] Tâche 3 : Refactoriser `DayPredictionCard.tsx` (AC: 1, 4)
  - [x] Étendre l'interface des props pour inclure les états de chargement et d'erreur.
  - [x] Ajouter le rendu des Skeletons en mode loading.
  - [x] Ajouter le rendu du message d'erreur et bouton retry.
  - [x] Créer `DayPredictionCardContainer.tsx`.

- [x] Tâche 4 : Analyser et refactoriser `CategoryGrid` (AC: 3)
  - [x] Analyse : `CategoryGrid` est déjà un composant de présentation pur recevant ses données en props. Aucune refactorisation nécessaire.

- [x] Tâche 5 : Mettre à jour les consommateurs (AC: 4)
  - [x] Les pages existantes comme `DailyHoroscopePage` continuent d'utiliser le Presenter en lui passant les props, ce qui respecte le pattern sans introduire de fetching redondant.

- [x] Tâche 6 : Validation (AC: 5, 6)
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Gestion de la granularité

Bien qu'un `DayPredictionCardContainer` ait été créé pour formaliser le pattern, la page `DailyHoroscopePage` continue d'injecter directement les données dans le `DayPredictionCard` (Presenter). Cela évite des appels API multiples sur une même page qui a besoin des données de prédiction pour plusieurs sections (Agenda, Turning Points, etc.). Le pattern Presenter est ainsi respecté tout en optimisant les performances.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création du hook `useDayPrediction`.
- Création du container `DayPredictionCardContainer`.
- Enrichissement de `DayPredictionCard` pour gérer ses propres états de loading (skeletons) et d'erreur.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/hooks/useDayPrediction.ts`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/DayPredictionCardContainer.tsx`
