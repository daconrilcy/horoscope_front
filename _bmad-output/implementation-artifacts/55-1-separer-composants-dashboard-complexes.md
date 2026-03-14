# Story 55.1: Séparer les composants dashboard complexes (DashboardHoroscopeSummaryCard, DailyInsightsSection)

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que `DashboardHoroscopeSummaryCard` et `DailyInsightsSection` soient séparés en un hook de données et un composant présentationnel,
afin de pouvoir tester le rendu indépendamment des appels API.

## Acceptance Criteria

1. `DashboardHoroscopeSummaryCard.tsx` ne contient plus d'appel API direct — il reçoit ses données via props.
2. Un hook `useDashboardHoroscopeSummary.ts` (ou le hook existant `useDashboardAstroSummary.ts` si déjà présent) gère le fetching et les états loading/error.
3. `DailyInsightsSection.tsx` suit le même pattern : hook séparé + composant présentationnel.
4. Les pages qui utilisent ces composants passent les props correctement.
5. Le rendu visuel est identique avant/après.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Analyser `DashboardHoroscopeSummaryCard.tsx` (AC: 1, 2)
  - [ ] Lire le fichier et identifier tous les appels API, hooks de données
  - [ ] Vérifier si `useDashboardAstroSummary.ts` existe déjà et couvre les besoins
  - [ ] Lister les props à passer au composant présentationnel

- [ ] Tâche 2 : Refactoriser `DashboardHoroscopeSummaryCard` (AC: 1, 2)
  - [ ] Créer/compléter `useDashboardHoroscopeSummary.ts` si besoin
  - [ ] Modifier le composant pour recevoir `data`, `isLoading`, `error` en props
  - [ ] Créer un composant container `DashboardHoroscopeSummaryCardContainer.tsx` qui appelle le hook et passe les props

- [ ] Tâche 3 : Analyser et refactoriser `DailyInsightsSection.tsx` (AC: 3)
  - [ ] Lire le fichier
  - [ ] Identifier le hook de données associé ou à créer
  - [ ] Appliquer le même pattern container/presenter

- [ ] Tâche 4 : Mettre à jour les pages qui utilisent ces composants (AC: 4)
  - [ ] Identifier quelles pages importent ces composants
  - [ ] Remplacer par les versions Container si applicable

- [ ] Tâche 5 : Validation (AC: 5, 6)
  - [ ] Vérifier le rendu visuel du dashboard
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Pattern container/presenter** :
```tsx
// Hook (logique)
export function useDashboardHoroscopeSummary() {
  const { data, isLoading, error } = useQuery(...)
  return { summary: data, isLoading, error }
}

// Composant présentationnel (pur)
interface Props {
  summary: SummaryData | null
  isLoading: boolean
  error: Error | null
}
export function DashboardHoroscopeSummaryCard({ summary, isLoading, error }: Props) {
  // Aucun appel API, aucun useQuery — juste du JSX
}

// Container (colle les deux)
export function DashboardHoroscopeSummaryCardContainer() {
  const { summary, isLoading, error } = useDashboardHoroscopeSummary()
  return <DashboardHoroscopeSummaryCard summary={summary} isLoading={isLoading} error={error} />
}
```

**Hook existant** : `useDashboardAstroSummary.ts` existe déjà selon la documentation — vérifier s'il couvre tous les besoins avant d'en créer un nouveau.

**Backward compatibility** : Si des pages importent directement `DashboardHoroscopeSummaryCard`, deux options :
1. Exporter le Container sous le nom original (transparent pour les consommateurs)
2. Mettre à jour les imports dans les pages (propre)

Préférer l'option 1 si les pages sont nombreuses.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire/modifier | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` |
| Vérifier/créer | `frontend/src/components/dashboard/useDashboardAstroSummary.ts` |
| Lire/modifier | `frontend/src/components/DailyInsightsSection.tsx` |
| Créer si besoin | `frontend/src/hooks/useDailyInsights.ts` |

### References

- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/components/dashboard/useDashboardAstroSummary.ts]
- [Source: frontend/src/components/DailyInsightsSection.tsx]
- [Source: _bmad-output/planning-artifacts/epic-55-separation-logique-presentation.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
