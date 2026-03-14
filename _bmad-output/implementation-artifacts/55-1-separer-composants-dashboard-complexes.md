# Story 55.1: Séparer les composants dashboard complexes (DashboardHoroscopeSummaryCard, DailyInsightsSection)

Status: done

## Story

En tant que développeur frontend,
je veux que `DashboardHoroscopeSummaryCard` et `DailyInsightsSection` soient séparés en un hook de données et un composant présentationnel,
afin de pouvoir tester le rendu indépendamment des appels API.

## Acceptance Criteria

1. `DashboardHoroscopeSummaryCard.tsx` ne contient plus d'appel API direct — il reçoit ses données via props. (Déjà le cas, renforcé par le container).
2. Un hook `useDashboardHoroscopeSummary.ts` (implémenté via extension de `useDashboardAstroSummary.ts`) gère le fetching et les états loading/error.
3. `DailyInsightsSection.tsx` suit le même pattern : hook séparé + composant présentationnel.
4. Les pages qui utilisent ces composants passent les props correctement (utilisent les versions Container).
5. Le rendu visuel est identique avant/après.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Analyser `DashboardHoroscopeSummaryCard.tsx` (AC: 1, 2)
  - [x] Identifier les besoins en données (prediction, isLoading, isError, sign, userId, dateKey, dayScore, refetch).
  - [x] Analyser `useDashboardAstroSummary.ts` existant.

- [x] Tâche 2 : Refactoriser `DashboardHoroscopeSummaryCard` (AC: 1, 2)
  - [x] Étendre `useDashboardAstroSummary.ts` pour retourner `prediction` et `refetch`.
  - [x] Créer `DashboardHoroscopeSummaryCardContainer.tsx` pour l'injection des données.

- [x] Tâche 3 : Analyser et refactoriser `DailyInsightsSection.tsx` (AC: 3)
  - [x] Créer `frontend/src/hooks/useDailyInsights.ts` pour extraire la logique de configuration et traduction.
  - [x] Refactoriser `DailyInsightsSection.tsx` pour inclure un Presenter pur et un Container (default export).
  - [x] Garantir la rétrocompatibilité pour les tests.

- [x] Tâche 4 : Mettre à jour les pages qui utilisent ces composants (AC: 4)
  - [x] Mise à jour de `DashboardPage.tsx` pour utiliser `DashboardHoroscopeSummaryCardContainer` et supprimer les appels API redondants.

- [x] Tâche 5 : Validation (AC: 5, 6)
  - [x] `npm run test` — 1079 tests réussis.
  - [x] Vérification visuelle du dashboard.

## Dev Notes

### Pattern Hybride pour DailyInsightsSection

Pour respecter l'Acceptance Criterion 6 ("Les tests passent sans modification"), `DailyInsightsSection.tsx` exporte maintenant un composant `DailyInsightsSectionPresenter` (pur) pour les tests unitaires isolés, et un composant `DailyInsightsSection` (Container) par défaut qui utilise le hook `useDailyInsights`. Cela permet aux tests existants de continuer à fonctionner sans avoir à leur passer manuellement des props.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Extension du hook `useDashboardAstroSummary` pour centraliser toute la logique du dashboard.
- Création du container `DashboardHoroscopeSummaryCardContainer`.
- Création du hook `useDailyInsights` et refactorisation de la section associée.
- Nettoyage des appels API redondants dans `DashboardPage`.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx`
- `frontend/src/hooks/useDailyInsights.ts`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/pages/DashboardPage.tsx`
