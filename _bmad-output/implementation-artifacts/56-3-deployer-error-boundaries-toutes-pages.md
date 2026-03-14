# Story 56.3: Déployer les error boundaries sur toutes les pages et sections critiques

Status: done

## Story

En tant que développeur frontend,
je veux que les `PageErrorBoundary` et `SectionErrorBoundary` soient déployés sur toutes les pages et sections critiques,
afin qu'une erreur JavaScript dans un composant affiche une UI de fallback utile plutôt que de faire planter l'app entière.

## Acceptance Criteria

1. Toutes les pages dans `AppShell` sont enveloppées dans un `PageErrorBoundary` au niveau du router ou du layout.
2. Les sections critiques (dashboard, chat, prediction) sont enveloppées dans des `SectionErrorBoundary`.
3. Les erreurs API visibles à l'utilisateur utilisent `<ErrorState>` au lieu de spans inline ou de rien.
4. L'app ne crashe plus entièrement si un composant lève une exception JavaScript.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Déployer `PageErrorBoundary` au niveau router/layout (AC: 1)
  - [x] Enveloppement de `<Outlet />` dans `AppLayout.tsx` avec `PageErrorBoundary`. Couvre toutes les pages protégées.

- [x] Tâche 2 : Identifier les sections critiques (AC: 2)
  - [x] Sections identifiées : Dashboard (Summary Card), Chat (Main window), Prédiction (Day card).

- [x] Tâche 3 : Déployer `SectionErrorBoundary` sur les sections critiques (AC: 2)
  - [x] `DashboardPage.tsx` : Enveloppement de `DashboardHoroscopeSummaryCardContainer`.
  - [x] `ChatPage.tsx` : Enveloppement de `ChatLayout`.
  - [x] `DailyHoroscopePage.tsx` : Enveloppement de `DayPredictionCard`.

- [x] Tâche 4 : Remplacer les affichages d'erreur hétérogènes (AC: 3)
  - [x] `NatalChartPage.tsx` : Remplacement du rendu d'erreur générique par `<ErrorState>`.

- [x] Tâche 5 : Validation (AC: 4, 5)
  - [x] `npm run test` — 1079 tests réussis.
  - [x] Correction d'un import erroné de `ErrorState` dans `NatalChartPage.tsx` détecté lors des tests.

## Dev Notes

### Stratégie de déploiement des Error Boundaries

Le déploiement a été fait de manière hiérarchique :
1. **Global** : `PageErrorBoundary` dans `AppLayout` pour empêcher le crash de toute l'interface de navigation si une page échoue.
2. **Local** : `SectionErrorBoundary` sur les composants faisant du fetching asynchrone complexe (`SummaryCard`, `DayPredictionCard`, `ChatWindow`).

L'utilisation systématique de l'alias `@ui` a été privilégiée pour l'import de `ErrorState`.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Déploiement de `PageErrorBoundary` dans le layout principal.
- Isolation des sections critiques du dashboard, du chat et des prédictions via `SectionErrorBoundary`.
- Utilisation de `ErrorState` pour les retours d'erreurs dans `NatalChartPage`.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
