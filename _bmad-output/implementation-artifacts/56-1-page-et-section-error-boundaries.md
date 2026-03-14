# Story 56.1: Créer PageErrorBoundary et SectionErrorBoundary à partir du ErrorBoundary existant

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que le composant `ErrorBoundary` existant soit étendu en deux variantes spécialisées `PageErrorBoundary` et `SectionErrorBoundary`,
afin d'avoir des fallbacks visuellement adaptés selon la portée de l'erreur (page entière vs section).

## Acceptance Criteria

1. `PageErrorBoundary` affiche un fallback pleine page avec titre "Une erreur est survenue" et bouton "Recharger la page".
2. `SectionErrorBoundary` affiche un fallback compact inline avec message d'erreur et bouton "Réessayer".
3. Les deux composants sont basés sur `ErrorBoundary.tsx` existant (pas de duplication de logique de boundary).
4. Les deux composants sont exportés depuis `frontend/src/components/ErrorBoundary/index.ts`.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Analyser `ErrorBoundary.tsx` existant (AC: 3)
  - [ ] Lire `frontend/src/components/ErrorBoundary.tsx`
  - [ ] Identifier l'API actuelle : props, méthodes, fallback par défaut
  - [ ] Décider si créer des variantes via props ou via sous-classes/wrappers

- [ ] Tâche 2 : Créer `PageErrorBoundary` (AC: 1)
  - [ ] Composant wrapper autour de `ErrorBoundary` avec fallback pleine page
  - [ ] Fallback : fond centré, titre, message, bouton `onClick={() => window.location.reload()`
  - [ ] Utiliser les tokens CSS : `var(--color-text-primary)`, `var(--bg-base)` etc.

- [ ] Tâche 3 : Créer `SectionErrorBoundary` (AC: 2)
  - [ ] Composant wrapper avec fallback compact inline
  - [ ] Fallback : card avec icône erreur, message, bouton "Réessayer" qui appelle `this.setState({ hasError: false })`
  - [ ] Utiliser le composant `EmptyState` de l'Epic 50 comme base visuelle si disponible

- [ ] Tâche 4 : Créer `frontend/src/components/ErrorBoundary/index.ts` (AC: 4)
  - [ ] Exporter `ErrorBoundary`, `PageErrorBoundary`, `SectionErrorBoundary`
  - [ ] Déplacer `ErrorBoundary.tsx` dans le dossier si nécessaire

- [ ] Tâche 5 : Validation (AC: 5)
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**ErrorBoundary React** : Les class components sont requis pour implémenter `componentDidCatch` / `getDerivedStateFromError`. On ne peut pas utiliser des hooks pour ça.

**Pattern recommandé** :
```tsx
// ErrorBoundary.tsx — existant (base)
class ErrorBoundary extends React.Component<ErrorBoundaryProps, State> {
  // logique existante
}

// PageErrorBoundary.tsx — nouveau wrapper
export function PageErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary fallback={<PageErrorFallback />}>
      {children}
    </ErrorBoundary>
  )
}

// SectionErrorBoundary.tsx — nouveau wrapper
export function SectionErrorBoundary({ children, onRetry }: Props) {
  return (
    <ErrorBoundary fallback={<SectionErrorFallback onRetry={onRetry} />}>
      {children}
    </ErrorBoundary>
  )
}
```

**Attention** : Le bouton "Réessayer" d'une SectionErrorBoundary doit réinitialiser l'état du boundary (`hasError: false`). Si `ErrorBoundary` existant ne fournit pas ce mécanisme, il faut l'ajouter via une prop `onReset` ou un `key` sur le boundary.

**Pattern key pour reset** :
```tsx
const [errorKey, setErrorKey] = useState(0)
return (
  <SectionErrorBoundary key={errorKey} onRetry={() => setErrorKey(k => k + 1)}>
    ...
  </SectionErrorBoundary>
)
```

**Composant `EmptyState`** : Si Epic 50 story 50.7 est `done`, `EmptyState` est disponible et peut servir de base pour le fallback compact.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire/modifier | `frontend/src/components/ErrorBoundary.tsx` |
| Créer | `frontend/src/components/ErrorBoundary/PageErrorBoundary.tsx` |
| Créer | `frontend/src/components/ErrorBoundary/SectionErrorBoundary.tsx` |
| Créer | `frontend/src/components/ErrorBoundary/index.ts` |

### References

- [Source: frontend/src/components/ErrorBoundary.tsx]
- [Source: frontend/src/components/ui/EmptyState/EmptyState.tsx]
- [Source: _bmad-output/planning-artifacts/epic-56-error-boundaries-standardises.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
