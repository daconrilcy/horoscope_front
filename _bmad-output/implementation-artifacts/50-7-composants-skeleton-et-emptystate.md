# Story 50.7: Créer les composants <Skeleton> et <EmptyState>

Status: done

## Story

En tant que développeur frontend,
je veux des composants `<Skeleton>` et `<EmptyState>` partagés,
afin de standardiser les états de chargement et de contenu vide à travers tout le produit.

## Acceptance Criteria

1. Le composant `<Skeleton>` existe dans `frontend/src/components/ui/Skeleton/Skeleton.tsx` et accepte les props `width`, `height`, `variant` (`'text' | 'rect' | 'circle'`) et `className`.
2. `<Skeleton>` utilise une animation de shimmer (gradient animé) définie via les tokens CSS.
3. Un composant utilitaire `<SkeletonGroup>` permet de définir un nombre de lignes Skeleton en une seule déclaration (`count` prop).
4. Le composant `<EmptyState>` existe dans `frontend/src/components/ui/EmptyState/EmptyState.tsx` et accepte les props `icon`, `title`, `description`, `action` (ReactNode optionnel).
5. `<EmptyState>` est centré visuellement et utilise les tokens de couleur et d'espacement.
6. Les deux composants sont exportés via `frontend/src/components/ui/index.ts`.
7. Les inline `<div style={{ width: "80%", marginBottom: "0.5rem" }}/>` dans `DashboardHoroscopeSummaryCard.tsx` sont remplacés par `<Skeleton>`.
8. Un test couvre le rendu de Skeleton avec différents variants et EmptyState avec et sans action.

## Tasks / Subtasks

- [x] Tâche 1 : Créer `<Skeleton>` (AC: 1, 2, 3)
  - [x] `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - [x] `frontend/src/components/ui/Skeleton/Skeleton.css`
  - [x] `frontend/src/components/ui/Skeleton/Skeleton.test.tsx`
  - [x] Animation shimmer CSS (gradient animé de gauche à droite)
  - [x] `SkeletonGroup` : rendu de `count` lignes Skeleton avec largeurs décroissantes par défaut
  - [x] `frontend/src/components/ui/Skeleton/index.ts`

- [x] Tâche 2 : Créer `<EmptyState>` (AC: 4, 5)
  - [x] `frontend/src/components/ui/EmptyState/EmptyState.tsx`
  - [x] `frontend/src/components/ui/EmptyState/EmptyState.css`
  - [x] `frontend/src/components/ui/EmptyState/EmptyState.test.tsx`
  - [x] `frontend/src/components/ui/EmptyState/index.ts`

- [x] Tâche 3 : Mettre à jour `frontend/src/components/ui/index.ts` (AC: 6)
  - [x] Ajouter les exports Skeleton et EmptyState

- [x] Tâche 4 : Remplacer les inline skeletons dans `DashboardHoroscopeSummaryCard.tsx` (AC: 7)
  - [x] Lire le composant pour localiser les `<div style={{ width: "..." }}>` de chargement
  - [x] Remplacer par `<Skeleton width="80%" height="1rem" />` etc.

- [x] Tâche 5 : Écrire les tests (AC: 8)
  - [x] Skeleton : rendu text, rect, circle ; SkeletonGroup avec count=3
  - [x] EmptyState : titre visible, action rendue si fournie, pas d'action si non fournie

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 stories 49.1-49.2 doivent être `done` pour les tokens d'animation.

### Animation shimmer

```css
@keyframes skeleton-shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-surface) 25%,
    var(--color-glass-bg) 50%,
    var(--color-bg-surface) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

.skeleton--text { height: 1em; border-radius: var(--radius-sm); }
.skeleton--rect { border-radius: var(--radius-md); }
.skeleton--circle { border-radius: var(--radius-full); }
```

### Interface TypeScript

```typescript
// Skeleton
interface SkeletonProps {
  width?: string | number
  height?: string | number
  variant?: 'text' | 'rect' | 'circle'
  className?: string
}

// SkeletonGroup
interface SkeletonGroupProps {
  count?: number
  // Chaque ligne a une largeur légèrement différente pour un rendu naturel
  widths?: string[]  // ex: ["80%", "60%", "70%"]
  height?: string
}

// EmptyState
interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}
```

### `SkeletonGroup` pour le chargement par défaut

```typescript
function SkeletonGroup({ count = 3, widths, height = '1rem' }: SkeletonGroupProps) {
  const defaultWidths = ['80%', '60%', '70%', '50%', '75%']
  return (
    <div className="skeleton-group">
      {Array.from({ length: count }, (_, i) => (
        <Skeleton key={i} width={widths?.[i] ?? defaultWidths[i % defaultWidths.length]} height={height} />
      ))}
    </div>
  )
}
```

### Usage dans `DashboardHoroscopeSummaryCard.tsx`

**Avant** (inline hardcodé) :
```tsx
<div style={{ width: "80%", marginBottom: "0.5rem" }} />
<div style={{ width: "60%" }} />
```

**Après** (composant Skeleton) :
```tsx
import { SkeletonGroup } from '../ui'

<SkeletonGroup count={2} widths={["80%", "60%"]} height="1rem" />
```

### EmptyState — usages identifiés dans le codebase

Les textes "Aucun contenu disponible..." dans les panneaux B2B et Admin seront migrés vers `<EmptyState>` dans l'Epic 52. Dans cette story, créer uniquement le composant — ne pas migrer les panneaux.

### Accessibilité

`<Skeleton>` : ajouter `aria-hidden="true"` pour masquer aux screen readers (c'est un état visuel de chargement, pas du contenu).

`<EmptyState>` : le titre est dans un `<h3>`, accessible normalement.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Skeleton/Skeleton.tsx` |
| Créer | `frontend/src/components/ui/Skeleton/Skeleton.css` |
| Créer | `frontend/src/components/ui/Skeleton/Skeleton.test.tsx` |
| Créer | `frontend/src/components/ui/Skeleton/index.ts` |
| Créer | `frontend/src/components/ui/EmptyState/EmptyState.tsx` |
| Créer | `frontend/src/components/ui/EmptyState/EmptyState.css` |
| Créer | `frontend/src/components/ui/EmptyState/EmptyState.test.tsx` |
| Créer | `frontend/src/components/ui/EmptyState/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |
| Modifier | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` |

### References

- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/styles/design-tokens.css] (tokens animation)
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Skeleton>` implémenté avec animation shimmer et variants (`text`, `rect`, `circle`).
- Composant utilitaire `<SkeletonGroup>` pour gérer facilement plusieurs lignes de chargement.
- Composant `<EmptyState>` pour standardiser les messages d'absence de contenu.
- Migration de `DashboardHoroscopeSummaryCard` pour utiliser les nouveaux Skeletons.
- Accessibilité : `aria-hidden="true"` sur les Skeletons.
- 8 tests unitaires validant les différents états et configurations.

### Change Log

- 2026-03-14 : Création des composants Skeleton et EmptyState.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Skeleton/Skeleton.tsx` |
| Créé | `frontend/src/components/ui/Skeleton/Skeleton.css` |
| Créé | `frontend/src/components/ui/Skeleton/Skeleton.test.tsx` |
| Créé | `frontend/src/components/ui/Skeleton/index.ts` |
| Créé | `frontend/src/components/ui/EmptyState/EmptyState.tsx` |
| Créé | `frontend/src/components/ui/EmptyState/EmptyState.css` |
| Créé | `frontend/src/components/ui/EmptyState/EmptyState.test.tsx` |
| Créé | `frontend/src/components/ui/EmptyState/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
| Modifié | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` |
