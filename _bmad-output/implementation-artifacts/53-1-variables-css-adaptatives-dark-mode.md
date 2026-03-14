# Story 53.1: Variables CSS adaptatives pour le mode dark dans les composants de texte

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les couleurs de texte qui changent selon le thème dark soient gérées par des variables CSS auto-adaptatives,
afin de supprimer tout calcul de couleur conditionnel `theme === 'dark'` dans les composants de présentation.

## Acceptance Criteria

1. Les variables `--color-text-on-dark`, `--color-text-muted-on-dark` sont définies dans `design-tokens.css` pour les contextes où le fond est sombre indépendamment du thème global.
2. La classe `.astro-context` définie sur le conteneur `AstroMoodBackground` surcharge les variables de texte pour forcer des couleurs claires sur fond sombre.
3. `DayPredictionCard.tsx` ne contient plus `const textColor = isAstro && theme === 'dark' ? "white" : "var(--text-1)"` — le composant n'importe plus `useTheme()` pour cette raison.
4. `DashboardHoroscopeSummaryCard.tsx` ne contient plus `theme === 'dark' ? 'white' : undefined` dans les styles inline.
5. Le rendu visuel des deux composants est identique en light, dark, et mode astrologique.
6. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Ajouter les variables contextuelles dans `design-tokens.css` (AC: 1)
  - [ ] `--color-text-on-astro: white` — texte sur fond astrologique sombre
  - [ ] `--color-text-muted-on-astro: rgba(255, 255, 255, 0.7)` — texte secondaire sur astro
  - [ ] Ces variables sont indépendantes du thème global (pas dans `.dark`) — elles s'appliquent par contexte de conteneur

- [ ] Tâche 2 : Ajouter la classe `.astro-context` dans `AstroMoodBackground.css` (AC: 2)
  - [ ] `.astro-context { --color-text-primary: var(--color-text-on-astro); --color-text-secondary: var(--color-text-muted-on-astro); }`
  - [ ] Appliquer cette classe sur l'élément racine de `AstroMoodBackground` (ou son enfant `.astro-mood-background__content`)

- [ ] Tâche 3 : Lire `DayPredictionCard.tsx` et identifier tous les usages de `theme` et `textColor` (AC: 3)
  - [ ] Lister chaque ligne avec `useTheme()`, `textColor`, `textMuted`
  - [ ] Créer les classes CSS correspondantes dans `DayPredictionCard.css` (nouveau ou existant)
  - [ ] Supprimer les variables `textColor`/`textMuted` et leur usage inline
  - [ ] Vérifier si `useTheme()` est encore nécessaire dans ce composant — supprimer l'import si non

- [ ] Tâche 4 : Migrer `DashboardHoroscopeSummaryCard.tsx` (AC: 4)
  - [ ] Supprimer `style={{ color: theme === 'dark' ? 'white' : undefined }}`
  - [ ] Le composant est dans un contexte `AstroMoodBackground` → `.astro-context` gère la couleur
  - [ ] Supprimer l'import `useTheme()` si plus nécessaire

- [ ] Tâche 5 : Validation (AC: 5, 6)
  - [ ] Tester DayPredictionCard en light mode, dark mode, et dans AstroMoodBackground
  - [ ] Tester DashboardHoroscopeSummaryCard idem
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Epic 49 story 49.1 `done` (tokens couleurs).

**Mécanisme CSS contextuel** : CSS custom properties héritent dans l'arbre DOM. Si un parent déclare `--color-text-primary: white`, tous ses enfants voient cette valeur sauf s'ils la redéfinissent eux-mêmes. C'est le mécanisme que `.astro-context` exploite.

```css
/* design-tokens.css */
:root {
  --color-text-primary: /* valeur normale */;
}
/* PAS dans .dark — indépendant du thème global */

/* AstroMoodBackground.css */
.astro-context {
  --color-text-primary: white;
  --color-text-secondary: rgba(255, 255, 255, 0.7);
}
```

### Cas particulier de DayPredictionCard

`DayPredictionCard` peut être rendu **avec ou sans** `AstroMoodBackground` selon le contexte. La prop `isAstro` détermine le contexte actuel. Si `isAstro`, le composant est enveloppé dans `AstroMoodBackground` (qui aura la classe `.astro-context`) — les variables CSS sont donc automatiquement surpassées. Si `!isAstro`, les couleurs normales s'appliquent.

→ La logique `isAstro && theme === 'dark' ? "white"` peut être **entièrement supprimée** si `AstroMoodBackground` porte la classe `.astro-context`.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/styles/design-tokens.css` |
| Modifier | `frontend/src/components/astro/AstroMoodBackground.css` |
| Modifier | `frontend/src/components/astro/AstroMoodBackground.tsx` (ajouter classe astro-context) |
| Modifier | `frontend/src/components/prediction/DayPredictionCard.tsx` |
| Modifier | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` |
| Créer/modifier | `frontend/src/components/prediction/DayPredictionCard.css` |

### References

- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/components/astro/AstroMoodBackground.css]
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-53-theme-dynamique-css.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
