# Story 50.6: Créer le composant <Card> avec variants et slots de composition

Status: done

## Story

En tant que développeur frontend,
je veux un composant `<Card>` composable avec des variants de surface,
afin de créer rapidement des conteneurs de contenu cohérents sans recoder la surface glassmorphism ou les ombres.

## Acceptance Criteria

1. Le composant `frontend/src/components/ui/Card/Card.tsx` existe et est exporté via `frontend/src/components/ui/index.ts`.
2. Les variants `glass`, `solid`, `elevated` sont supportés via prop `variant`.
3. La prop `as` permet de changer l'élément HTML rendu (`div`, `article`, `section`, `button`, `a`) — défaut `div`.
4. Les props `padding` (`none | sm | md | lg`) et `className` sont supportées.
5. `<Card.Header>`, `<Card.Body>`, `<Card.Footer>` sont disponibles comme sous-composants pour la composition.
6. La prop `clickable` (boolean) ajoute les styles hover/focus d'une carte cliquable.
7. Les styles utilisent les tokens CSS et la classe `.glass-card` de l'Epic 49 (story 49.4) pour le variant `glass`.
8. Un test couvre le rendu des variants, les sous-composants et le variant clickable.

## Tasks / Subtasks

- [x] Tâche 1 : Créer la structure de fichiers (AC: 1)
  - [x] `frontend/src/components/ui/Card/Card.tsx`
  - [x] `frontend/src/components/ui/Card/Card.css`
  - [x] `frontend/src/components/ui/Card/Card.test.tsx`
  - [x] `frontend/src/components/ui/Card/index.ts`
  - [x] Ajouter `export * from './Card'` dans `frontend/src/components/ui/index.ts`

- [x] Tâche 2 : Implémenter `<Card>` et ses sous-composants (AC: 2, 3, 4, 5, 6)
  - [x] `Card` : composant principal avec polymorphisme `as`
  - [x] `Card.Header` : slot header avec padding et border-bottom optionnel
  - [x] `Card.Body` : slot body avec padding configurable
  - [x] `Card.Footer` : slot footer avec padding et border-top optionnel
  - [x] Pattern composé : `Card.Header = CardHeader` etc. (dot notation)

- [x] Tâche 3 : Créer `Card.css` (AC: 7)
  - [x] `.card` : base reset, overflow hidden, border-radius `--radius-lg`
  - [x] `.card--glass` : délègue à `.glass-card` (Epic 49.4) + import depuis glass.css
  - [x] `.card--solid` : background `--color-bg-surface`, border `--color-glass-border`
  - [x] `.card--elevated` : background `--color-bg-elevated`, shadow `--shadow-card`
  - [x] `.card--clickable` : cursor pointer, hover lift (transform translateY -2px), transition
  - [x] `.card--padding-none`, `.card--padding-sm`, `.card--padding-md`, `.card--padding-lg`
  - [x] `.card__header`, `.card__body`, `.card__footer`

- [x] Tâche 4 : Écrire les tests (AC: 8)
  - [x] Rendu de chaque variant sans crash
  - [x] `as="article"` rend un `<article>`
  - [x] `clickable` ajoute le cursor pointer
  - [x] Sous-composants Card.Header et Card.Body rendus

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 stories 49.1-49.4 doivent être `done` (tokens + glass.css).

### Pattern Compound Component (dot notation)

```typescript
function Card({ as: Tag = 'div', variant = 'glass', padding = 'md', clickable, className, children, ...props }: CardProps) {
  const classes = [
    'card',
    `card--${variant}`,
    variant === 'glass' ? 'glass-card' : '',
    `card--padding-${padding}`,
    clickable ? 'card--clickable' : '',
    className
  ].filter(Boolean).join(' ')

  return <Tag className={classes} {...props}>{children}</Tag>
}

function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={`card__header ${className ?? ''}`}>{children}</div>
}

Card.Header = CardHeader
Card.Body = CardBody
Card.Footer = CardFooter

export { Card }
```

### Polymorphisme `as`

```typescript
interface CardProps<T extends React.ElementType = 'div'> {
  as?: T
  variant?: 'glass' | 'solid' | 'elevated'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  clickable?: boolean
  className?: string
  children?: React.ReactNode
}
```

Pour un typage complet du polymorphisme avec les props de l'élément cible, utiliser le pattern standard React `ComponentPropsWithRef`. Si le typage devient trop complexe, simplifier en acceptant `as` sans le typage polymorphique avancé — la fonctionnalité prime sur le typage parfait.

### Lien avec `.glass-card` (Epic 49.4)

Le variant `glass` ajoute la classe `.glass-card` qui est définie dans `frontend/src/styles/glass.css` (créé en 49.4). Le composant `Card` ne redéfinit pas le glassmorphism — il délègue à `.glass-card`.

```css
/* Card.css */
.card--glass {
  /* Les styles glass viennent de .glass-card via la classe CSS */
  /* Ce selector ne rajoute que les surcharges spécifiques à Card */
}
```

### Usages futurs dans le codebase

Le composant `<Card>` sera utilisé lors de la migration des pages (Epic 51+) pour remplacer :
- Les `<div className="panel">` dans les pages
- Les wrappers de sections dans Dashboard, Settings, etc.
- **Pas** HeroHoroscopeCard, MiniInsightCard, ShortcutCard — ces composants sont spécifiques et gardent leur CSS

### Tokens CSS

```css
.card--solid {
  background: var(--color-bg-surface);
  border: 1px solid var(--color-glass-border);
}
.card--elevated {
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-card);
}
.card--clickable:hover {
  transform: translateY(-2px);
  transition: transform var(--duration-fast) var(--easing-default);
}
.card--padding-sm { padding: var(--space-4); }
.card--padding-md { padding: var(--space-6); }
.card--padding-lg { padding: var(--space-8); }
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/components/ui/Card/Card.tsx` |
| Créer | `frontend/src/components/ui/Card/Card.css` |
| Créer | `frontend/src/components/ui/Card/Card.test.tsx` |
| Créer | `frontend/src/components/ui/Card/index.ts` |
| Modifier | `frontend/src/components/ui/index.ts` |

### References

- [Source: frontend/src/styles/glass.css] (Epic 49.4)
- [Source: frontend/src/styles/design-tokens.css] (Epic 49)
- [Source: frontend/src/App.css] (`.panel` existant — futur remplacé par Card)
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Composant `<Card>` implémenté avec support du polymorphisme (`as`).
- Support des variants `glass`, `solid` et `elevated`.
- Architecture en "Compound Components" avec `Card.Header`, `Card.Body` et `Card.Footer`.
- Intégration native avec `glass.css` pour le variant `glass`.
- Gestion des paddings (`none` à `lg`) et de l'état cliquable (hover lift).
- 6 tests unitaires validant les variants, le polymorphisme et la composition.

### Change Log

- 2026-03-14 : Création du composant Card et de ses sous-composants.

### File List

| Action | Fichier |
|--------|---------|
| Créé | `frontend/src/components/ui/Card/Card.tsx` |
| Créé | `frontend/src/components/ui/Card/Card.css` |
| Créé | `frontend/src/components/ui/Card/Card.test.tsx` |
| Créé | `frontend/src/components/ui/Card/index.ts` |
| Modifié | `frontend/src/components/ui/index.ts` |
