# Story 53.2: Variables CSS contextuelles pour les surfaces AstroTheme

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les surfaces de fond astrologique (clair/sombre) soient gérées par des variables CSS contextuelles,
afin que les composants enfants d'AstroMoodBackground s'adaptent automatiquement sans vérifier `theme === 'dark'`.

## Acceptance Criteria

1. Les variables `--color-surface-astro-light`, `--color-surface-astro-dark` sont définies dans `design-tokens.css`.
2. La classe `.astro-context` dans `AstroMoodBackground.css` expose `--color-surface-astro` qui bascule selon le thème global via la cascade CSS.
3. Les composants enfants de `AstroMoodBackground` qui lisent une couleur de surface n'utilisent plus `theme === 'dark'` pour leurs backgrounds.
4. Le rendu visuel est identique en light, dark, et mode astrologique à l'état précédent.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Identifier tous les composants qui vérifient `theme === 'dark'` pour des couleurs de surface dans un contexte astro (AC: 1)
  - [ ] Grep `theme === 'dark'` dans `frontend/src/components/`
  - [ ] Lister les composants concernés et les variables CSS manquantes

- [ ] Tâche 2 : Ajouter les variables de surface astro dans `design-tokens.css` (AC: 1)
  - [ ] `--color-surface-astro: rgba(10, 5, 30, 0.85)` en mode light (fond astro foncé par défaut)
  - [ ] `.dark { --color-surface-astro: rgba(5, 2, 20, 0.92); }` — légèrement plus sombre en dark

- [ ] Tâche 3 : Étendre `.astro-context` dans `AstroMoodBackground.css` (AC: 2)
  - [ ] Ajouter `--color-surface-current: var(--color-surface-astro)` dans `.astro-context`
  - [ ] Vérifier que les composants lisant `--color-surface-current` héritent bien

- [ ] Tâche 4 : Migrer les composants identifiés (AC: 3)
  - [ ] Remplacer les styles inline `background: theme === 'dark' ? ... : ...` par `var(--color-surface-astro)`
  - [ ] Supprimer les imports `useTheme()` devenus inutiles dans ces composants

- [ ] Tâche 5 : Validation (AC: 4, 5)
  - [ ] Vérifier visuellement en light, dark, et astrologique
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Story 53.1 `done` (`.astro-context` est déjà en place sur `AstroMoodBackground`).

**Mécanisme** : La classe `.astro-context` est déjà appliquée sur le conteneur racine de `AstroMoodBackground`. On l'étend avec des variables de surface supplémentaires. Les enfants héritent automatiquement.

```css
/* AstroMoodBackground.css */
.astro-context {
  --color-text-primary: white;
  --color-text-secondary: rgba(255, 255, 255, 0.7);
  /* Nouveau : */
  --color-surface-astro: rgba(10, 5, 30, 0.85);
}
```

**Ne pas modifier** : `AstroMoodBackground.tsx` — la classe est déjà appliquée depuis 53.1.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/styles/design-tokens.css` |
| Modifier | `frontend/src/components/astro/AstroMoodBackground.css` |
| Modifier | Composants identifiés au step 1 |

### References

- [Source: frontend/src/components/astro/AstroMoodBackground.css]
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/implementation-artifacts/53-1-variables-css-adaptatives-dark-mode.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
