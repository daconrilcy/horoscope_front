# Story 50.8: Créer les composants <Badge> et <IconBadge>

Status: done

## Story

En tant que développeur frontend,
je veux des composants `<Badge>` et `<IconBadge>` partagés,
afin de ne plus recoder le pattern icône-dans-un-badge-coloré dans chaque composant qui l'utilise.

## Acceptance Criteria

1. Le composant `<Badge>` existe dans `frontend/src/components/ui/Badge/Badge.tsx` avec les props `color`, `size` (`'sm' | 'md' | 'lg'`) et `children`.
2. Le composant `<IconBadge>` existe dans le même fichier avec les props `icon` (ReactNode), `color`, `size`.
3. Les couleurs des badges du produit (`--color-badge-chat`, `--color-badge-amour`, etc.) sont accessibles via un mapping TypeScript exporté `BADGE_COLORS`.
4. Les composants `ShortcutCard.tsx` et `MiniInsightCard.tsx` sont refactorisés pour utiliser `<IconBadge>` en interne.
5. Le rendu visuel de `ShortcutCard` et `MiniInsightCard` est pixel-perfect identique avant/après.
6. Les deux composants sont exportés via `frontend/src/components/ui/index.ts`.
7. Un test couvre le rendu des tailles, la prop color et l'usage de BADGE_COLORS.

## Tasks / Subtasks

- [x] Tâche 1 : Lire `ShortcutCard.tsx` et `MiniInsightCard.tsx` (AC: 4)
  - [x] Identifier le pattern badge actuel dans chaque composant
  - [x] Noter la taille et les styles du badge (44px dans ShortcutCard)
  - [x] Identifier comment `badgeColor` est passé en prop

- [x] Tâche 2 : Créer `<Badge>` et `<IconBadge>` (AC: 1, 2, 3)
  - [x] `frontend/src/components/ui/Badge/Badge.tsx`
  - [x] `frontend/src/components/ui/Badge/Badge.css`
  - [x] `frontend/src/components/ui/Badge/Badge.test.tsx`
  - [x] `frontend/src/components/ui/Badge/index.ts`
  - [x] `BADGE_COLORS` mapping TypeScript exporté
  - [x] Ajouter `export * from './Badge'` dans `frontend/src/components/ui/index.ts`

- [x] Tâche 3 : Refactoriser `ShortcutCard.tsx` (AC: 4)
  - [x] Remplacer le badge inline par `<IconBadge>`
  - [x] Utiliser `BADGE_COLORS` si la couleur vient d'une constante

- [x] Tâche 4 : Refactoriser `MiniInsightCard.tsx` (AC: 4)
  - [x] Remplacer le badge inline par `<IconBadge>`
  - [x] Utiliser `BADGE_COLORS` si applicable

- [x] Tâche 5 : Validation visuelle (AC: 5)
  - [x] Dashboard : ShortcutCard et MiniInsightCard visuellement identiques

- [x] Tâche 6 : Écrire les tests (AC: 7)
  - [x] Rendu Badge sm/md/lg
  - [x] IconBadge avec icône Lucide
  - [x] BADGE_COLORS contient les clés attendues

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 story 49.1 `done` (tokens couleurs badges).

### Pattern actuel à remplacer

**Dans `ShortcutCard.tsx`** (approximatif) :
```tsx
<div style={{ background: badgeColor, borderRadius: 16, width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
  <Icon size={20} strokeWidth={1.75} />
</div>
```

**Dans `MiniInsightCard.tsx`** (approximatif) :
```tsx
<div className="mini-card__badge" style={{ background: badgeColor }}>
  <Icon size={18} />
</div>
```

### Interface TypeScript

```typescript
// Badge.tsx
export interface BadgeProps {
  color?: string          // valeur CSS directe ou depuis BADGE_COLORS
  size?: 'sm' | 'md' | 'lg'
  className?: string
  children?: React.ReactNode
}

export interface IconBadgeProps {
  icon: React.ReactNode
  color?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

// Mapping des couleurs de badges du produit
export const BADGE_COLORS = {
  chat:         'var(--color-badge-chat)',
  consultation: 'var(--color-badge-consultation)',
  amour:        'var(--color-badge-amour)',
  travail:      'var(--color-badge-travail)',
  energie:      'var(--color-badge-energie)',
} as const

export type BadgeColorKey = keyof typeof BADGE_COLORS
```

### CSS

```css
.badge {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);  /* 14px — ou --radius-lg selon la taille */
  flex-shrink: 0;
}
/* Tailles */
.badge--sm { width: 32px;  height: 32px; border-radius: var(--radius-sm); }
.badge--md { width: 40px;  height: 40px; border-radius: var(--radius-md); }
.badge--lg { width: 48px;  height: 48px; border-radius: var(--radius-lg); }
```

La couleur de fond est appliquée via `style={{ background: color }}` sur l'élément — c'est une prop dynamique et non une classe CSS statique.

### Taille des icônes par taille de badge

| Badge size | Icon size Lucide |
|-----------|-----------------|
| sm | 16px |
| md | 20px |
| lg | 24px |

Passer la taille d'icône via prop dans `<IconBadge>` ou calculer automatiquement selon `size`.

### Attention : `ShortcutCard` et `MiniInsightCard` utilisent des classes CSS spécifiques

`MiniInsightCard.css` a `.mini-card__badge`. Après refacto :
- Si le rendu est identique avec `<IconBadge>`, supprimer `.mini-card__badge` du CSS
- Sinon, conserver `.mini-card__badge` et appliquer `className="mini-card__badge"` sur `<Badge>`

Ne pas casser le rendu pixel-perfect.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Badge/Badge.tsx` |
| Créer | `frontend/src/components/ui/Badge/Badge.css` |
| Créer | `frontend/src/components/ui/Badge/Badge.test.tsx` |
| Créer | `frontend/src/components/ui/Badge/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |
| Modifier | `frontend/src/components/ShortcutCard.tsx` |
| Modifier | `frontend/src/components/MiniInsightCard.tsx` |

### References

- [Source: frontend/src/components/ShortcutCard.tsx]
- [Source: frontend/src/components/ShortcutCard.css]
- [Source: frontend/src/components/MiniInsightCard.tsx]
- [Source: frontend/src/components/MiniInsightCard.css]
- [Source: frontend/src/styles/design-tokens.css] (tokens --color-badge-*)
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Badge>` implémenté avec support des tailles `sm` (36px), `md` (40px) et `lg` (44px).
- Composant `<IconBadge>` pour simplifier l'usage des icônes dans les badges.
- Mapping `BADGE_COLORS` exporté pour centraliser les variables CSS des badges.
- Refactorisation de `ShortcutCard` pour utiliser `<IconBadge size="lg">`.
- Refactorisation de `MiniInsightCard` pour utiliser `<IconBadge size="sm">`.
- Nettoyage des styles CSS redondants dans les composants refactorisés.
- 6 tests unitaires validant les tailles, les couleurs et le rendu des icônes.

### Change Log

- 2026-03-14 : Création des composants Badge et IconBadge et refactorisation des cartes.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Badge/Badge.tsx` |
| Créé | `frontend/src/components/ui/Badge/Badge.css` |
| Créé | `frontend/src/components/ui/Badge/Badge.test.tsx` |
| Créé | `frontend/src/components/ui/Badge/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
| Modifié | `frontend/src/components/ShortcutCard.tsx` |
| Modifié | `frontend/src/components/ShortcutCard.css` |
| Modifié | `frontend/src/components/MiniInsightCard.tsx` |
| Modifié | `frontend/src/components/MiniInsightCard.css` |
