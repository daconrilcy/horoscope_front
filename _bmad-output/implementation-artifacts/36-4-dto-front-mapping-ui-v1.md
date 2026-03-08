# Story 36.4 : DTO front et mapping UI V1

Status: done

## Story

As a développeur front-end de l'application horoscope,
I want un contrat TypeScript stable (types, client API, hooks, utilitaires de mapping) et des composants UI de base pour afficher la prédiction quotidienne,
so that la `TodayPage` peut remplacer ses données statiques par la vraie réponse API sans duplication de logique de présentation.

## Acceptance Criteria

### AC1 — Catégories dynamiques depuis l'API

Les catégories affichées correspondent exactement au tableau `categories[]` renvoyé par l'API (code, note_20, summary). Aucun hardcoding de liste de catégories côté front.

### AC2 — Mapping notes 1-20 stable

Les mêmes valeurs numériques `note_20` donnent toujours les mêmes labels et couleurs CSS, selon la table :
- 1–5 : "fragile" → `var(--danger)`
- 6–9 : "tendu" → `var(--warning)`
- 10–12 : "neutre" → `var(--text-2)`
- 13–16 : "porteur" → `var(--success)`
- 17–20 : "très favorable" → `var(--primary)`

### AC3 — Pivots visuellement distingués

Les blocs `turning_point: true` dans la timeline sont visuellement distincts des blocs ordinaires. Les entrées `turning_points[]` sont listées séparément dans `TurningPointsList`.

### AC4 — Affichage brut sans réinterprétation

Le front n'effectue aucun calcul sur les scores. Il affiche uniquement ce que l'API renvoie (`note_20`, `summary`, `overall_tone`, etc.).

### AC5 — Fallback loading/erreur

La `TodayPage` affiche un indicateur visuel pendant le chargement et un message d'erreur explicite si le hook React Query retourne `isError`. Aucun crash sur réponse vide.

### AC6 — Heures au format HH:mm locale

Toutes les heures issues de `start_local` / `end_local` / `occurred_at_local` sont affichées au format HH:mm en locale `fr-FR`.

## Tasks / Subtasks

### T1 — Créer `frontend/src/types/dailyPrediction.ts` (AC1, AC4)

- [x] Déclarer `DailyPredictionMeta`
- [x] Déclarer `DailyPredictionCategory`
- [x] Déclarer `DailyPredictionTimeBlock`
- [x] Déclarer `DailyPredictionTurningPoint`
- [x] Déclarer `DailyPredictionSummary`
- [x] Déclarer `DailyPredictionResponse`

### T2 — Créer `frontend/src/api/dailyPrediction.ts` (AC5)

- [x] Fonction `getDailyPrediction(token: string, date?: string): Promise<DailyPredictionResponse>`
- [x] Fonction `getDailyHistory(token: string, from: string, to: string): Promise<DailyHistoryResponse>`

### T3 — Créer `frontend/src/api/useDailyPrediction.ts` (AC5)

- [x] Hook `useDailyPrediction(token: string | null, date?: string)` via `useQuery`
- [x] Hook `useDailyHistory(token: string | null, from: string, to: string)` via `useQuery`

### T4 — Créer `frontend/src/utils/predictionBands.ts` (AC2)

- [x] Fonction `getNoteBand(note: number): { label: string; colorVar: string }`
- [x] Mapping `TONE_LABELS`
- [x] Mapping `TONE_COLORS`
- [x] Mapping `CATEGORY_META`

### T5 — Créer les composants dans `frontend/src/components/prediction/` (AC1, AC2, AC3, AC4, AC6)

- [x] `DayPredictionCard.tsx`
- [x] `CategoryGrid.tsx`
- [x] `DayTimeline.tsx`
- [x] `TurningPointsList.tsx`

### T6 — Mettre à jour `frontend/src/pages/TodayPage.tsx` (AC1, AC5)

- [x] Importer `useDailyPrediction`
- [x] Remplacer `STATIC_HOROSCOPE` par la donnée issue du hook
- [x] Afficher un spinner pendant `isLoading`
- [x] Afficher un message d'erreur pendant `isError`
- [x] Intégrer les nouveaux composants

### T7 — Corriger les écarts remontés en code review (AC1, AC4, AC5)

- [x] Scoper les clés React Query par utilisateur pour éviter la réutilisation cross-session
- [x] Supprimer l'arrondi de `note_20` dans `CategoryGrid`
- [x] Ajouter un fallback lisible pour les codes catégories inconnus sans écraser le code API
- [x] Remplacer les `any` résiduels du DTO par des types explicites pour `drivers`
- [x] Réaligner les tests `TodayPage` et routeurs avec le nouveau flux API
- [x] Ajouter des tests ciblés pour `dailyPrediction`, `useDailyPrediction` et `predictionBands`

## Dev Notes

### Architecture

L'intégration suit le pattern établi : Types -> Client API -> Hook React Query -> UI Components.

### Project Structure Notes

- Création du dossier `frontend/src/components/prediction/`
- Suppression des données statiques dans `TodayPage.tsx`
- Ajout de tests ciblés pour le contrat daily prediction et la navigation liée à `TodayPage`

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Fixed linting errors (unused imports, verbatimModuleSyntax for types).
- Confirmed `npm run lint` passes in `frontend`.
- Fixed review findings on cache scoping, raw score rendering, DTO typing, and regression coverage.
- Confirmed targeted Vitest suite passes for `TodayPage`, router, hooks, API client and mapping utilities.

### Completion Notes List

- TypeScript interfaces for Daily Prediction and History implemented.
- API client functions with robust error handling (FastAPI 422 support).
- React Query hooks for fetching data with 5min/15min staleTime and user-scoped query keys.
- Utility for note-to-band mapping according to AC2, with readable fallback labels for unknown category codes.
- 4 specialized UI components using project CSS variables.
- `TodayPage.tsx` refactored to use real-time API data instead of static content.
- `CategoryGrid` now displays the raw `note_20` value returned by the API without re-interpretation.
- DTO typing was tightened for `turning_points[].drivers` and `severity`.
- Regression tests were updated and new tests were added for the daily prediction contract.

### File List

- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/api/dailyPrediction.ts`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/utils/predictionBands.ts`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayTimeline.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/tests/TodayPage.test.tsx`
- `frontend/src/tests/useDailyPrediction.test.tsx`
- `frontend/src/tests/dailyPredictionApi.test.ts`
- `frontend/src/tests/predictionBands.test.ts`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/router.test.tsx`

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
- 2026-03-08: Implémentation complète du contrat front et intégration UI.
- 2026-03-08: Corrections post-review appliquées sur le cache utilisateur, l'affichage brut des scores, le typage DTO et la couverture de tests.
