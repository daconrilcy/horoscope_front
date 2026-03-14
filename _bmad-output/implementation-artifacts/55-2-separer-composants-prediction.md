# Story 55.2: Séparer les composants de prédiction (DayPredictionCard, CategoryGrid)

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que `DayPredictionCard` et `CategoryGrid` soient séparés en hook de données et composant présentationnel,
afin de pouvoir tester leur rendu avec des données mockées sans appel API.

## Acceptance Criteria

1. `DayPredictionCard.tsx` ne contient plus de logique de fetching — il reçoit `prediction`, `isLoading`, `error` en props.
2. Un hook `useDayPrediction.ts` gère le fetching et les états.
3. `CategoryGrid` suit le même pattern si elle contient de la logique de données.
4. Un composant `DayPredictionCardContainer` (ou équivalent) assemble hook + composant.
5. Le rendu visuel est identique avant/après.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Analyser `DayPredictionCard.tsx` (AC: 1, 2)
  - [ ] Lire le fichier complet
  - [ ] Identifier les appels API, hooks de données, et la logique métier
  - [ ] Déterminer l'interface de props du composant présentationnel

- [ ] Tâche 2 : Créer `useDayPrediction.ts` (AC: 2)
  - [ ] Extraire toute la logique de fetching depuis `DayPredictionCard.tsx`
  - [ ] Retourner `{ prediction, isLoading, error }`

- [ ] Tâche 3 : Refactoriser `DayPredictionCard.tsx` (AC: 1, 4)
  - [ ] Modifier le composant pour être purement présentationnel
  - [ ] Créer `DayPredictionCardContainer.tsx` qui utilise le hook

- [ ] Tâche 4 : Analyser et refactoriser `CategoryGrid` (AC: 3)
  - [ ] Lire `CategoryGrid.tsx` s'il contient de la logique de données
  - [ ] Si oui, extraire un hook `useCategoryGrid.ts`
  - [ ] Si non (déjà présentationnel), documenter dans Completion Notes

- [ ] Tâche 5 : Mettre à jour les consommateurs (AC: 4)
  - [ ] Identifier les pages/composants qui utilisent `DayPredictionCard`
  - [ ] Remplacer par `DayPredictionCardContainer` ou passer les props

- [ ] Tâche 6 : Validation (AC: 5, 6)
  - [ ] Vérifier le rendu de la page de prédiction
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Story 53.1 `done` — `DayPredictionCard` n'a plus de `useTheme()` pour les couleurs.

**Attention** : `DayPredictionCard` a une prop `isAstro` qui détermine si le fond astrologique est actif. Cette prop reste — c'est une prop de présentation, pas de logique métier.

**Pattern** :
```tsx
// Hook
export function useDayPrediction(date: string) {
  return useQuery(['dayPrediction', date], () => fetchDayPrediction(date))
}

// Composant présentationnel
interface DayPredictionCardProps {
  prediction: DayPrediction | null
  isLoading: boolean
  error: Error | null
  isAstro?: boolean  // prop de présentation — reste ici
}
export function DayPredictionCard({ prediction, isLoading, error, isAstro }: DayPredictionCardProps) {
  // JSX pur
}

// Container
export function DayPredictionCardContainer({ date, isAstro }: { date: string; isAstro?: boolean }) {
  const { data: prediction, isLoading, error } = useDayPrediction(date)
  return <DayPredictionCard prediction={prediction} isLoading={isLoading} error={error} isAstro={isAstro} />
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire/modifier | `frontend/src/components/prediction/DayPredictionCard.tsx` |
| Créer | `frontend/src/hooks/useDayPrediction.ts` |
| Créer | `frontend/src/components/prediction/DayPredictionCardContainer.tsx` |
| Vérifier | `frontend/src/components/prediction/CategoryGrid.tsx` |

### References

- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: _bmad-output/planning-artifacts/epic-55-separation-logique-presentation.md]
- [Source: _bmad-output/implementation-artifacts/55-1-separer-composants-dashboard-complexes.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
