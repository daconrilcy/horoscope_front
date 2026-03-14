# Story 49.3: Créer les classes CSS utilitaires dérivées des tokens

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux disposer d'un ensemble de classes CSS utilitaires (`.text-primary`, `.surface-glass`, `.rounded-xl`, etc.) dérivées des design tokens,
afin d'appliquer les styles courants dans les composants sans dupliquer de valeurs CSS inline ou de redéclarer des styles identiques dans plusieurs fichiers.

## Acceptance Criteria

1. Le fichier `frontend/src/styles/utilities.css` existe et contient les classes utilitaires organisées par catégorie.
2. Les classes de couleur de texte `.text-primary`, `.text-secondary`, `.text-muted` sont disponibles et utilisent les variables de couleur de `design-tokens.css`.
3. Les classes de surface `.surface-glass`, `.surface-card`, `.surface-elevated` sont disponibles pour appliquer les fonds et bordures des tokens.
4. Les classes de rayon `.rounded-sm`, `.rounded-md`, `.rounded-lg`, `.rounded-xl`, `.rounded-full` sont disponibles.
5. Les classes d'ombre `.shadow-card`, `.shadow-hero`, `.shadow-nav` sont disponibles.
6. Les classes d'espacement utilitaires les plus courants sont disponibles (ex: `.p-4`, `.px-6`, `.py-4`, `.mb-2`, `.mt-6`).
7. Le fichier est importé dans `main.tsx` après `design-tokens.css` et avant `App.css`.
8. Aucun style inline existant n'est modifié dans cette story — les classes sont disponibles mais pas encore appliquées (migration en 49.5).
9. Aucune régression visuelle.

## Tasks / Subtasks

- [ ] Tâche 1 : Créer `frontend/src/styles/utilities.css` (AC: 1)
  - [ ] En-tête de commentaire expliquant la structure et la règle d'usage

- [ ] Tâche 2 : Classes de texte (AC: 2)
  - [ ] `.text-primary { color: var(--color-text-primary); }`
  - [ ] `.text-secondary { color: var(--color-text-secondary); }`
  - [ ] `.text-muted { color: var(--color-text-muted); }`
  - [ ] `.text-headline { color: var(--color-text-headline); }`

- [ ] Tâche 3 : Classes de surface (AC: 3)
  - [ ] `.surface-glass` → background + border + backdrop-filter depuis les tokens glass
  - [ ] `.surface-card` → background card + border + radius md
  - [ ] `.surface-elevated` → background elevated + shadow card

- [ ] Tâche 4 : Classes de rayon (AC: 4)
  - [ ] `.rounded-sm`, `.rounded-md`, `.rounded-lg`, `.rounded-xl`, `.rounded-full`

- [ ] Tâche 5 : Classes d'ombre (AC: 5)
  - [ ] `.shadow-card`, `.shadow-hero`, `.shadow-nav`

- [ ] Tâche 6 : Classes d'espacement utilitaires les plus courants (AC: 6)
  - [ ] Sélectionner les 15-20 combinaisons propriété/valeur les plus répétées dans le code existant
  - [ ] `p-2/4/6/8`, `px-4/6/8`, `py-4/6/8`, `m-2/4`, `mb-2/4/6`, `mt-4/6`, `gap-2/4/6`

- [ ] Tâche 7 : Mettre à jour l'ordre d'import dans `main.tsx` (AC: 7)
  - [ ] `design-tokens.css` → `utilities.css` → `index.css` → `theme.css` → `App.css`

## Dev Notes

### Contexte technique

**Prérequis** : Stories 49.1 et 49.2 doivent être `done`. Les classes utilitaires référencent les tokens définis dans ces stories.

**Règle de design des utilitaires** :
- N'inclure que les patterns réellement répétés dans le codebase existant (minimum 3 occurrences)
- Pas de système complet à la Tailwind — seulement les 40-50 classes les plus utiles
- Pas de `!important`
- Nommage en français ou anglais, cohérent avec l'existant

### Patterns répétés identifiés dans le codebase

**Texte dynamique selon le thème** — pattern en JSX à éliminer :
```tsx
// DashboardHoroscopeSummaryCard.tsx, DayPredictionCard.tsx
style={{ color: theme === 'dark' ? 'white' : 'var(--text-1)' }}
```
→ Les variables CSS auto-adaptatives via `.dark` renderont ce pattern inutile.
→ Dans cette story : définir `--color-text-adaptive` dans `design-tokens.css` :
```css
:root { --color-text-adaptive: var(--color-text-primary); }
.dark { --color-text-adaptive: white; }
```
Et `.text-adaptive { color: var(--color-text-adaptive); }`

**Surfaces répétées** — `backdrop-filter: blur(14px)` apparaît dans HeroHoroscopeCard.css, MiniInsightCard.css, ShortcutCard.css. Le token `--surface-glass-blur: 14px` doit être dans design-tokens.css (story 49.1/49.2), et `.surface-glass` l'utilise ici.

### Ce que les classes utilitaires NE doivent PAS faire

- Ne pas remplacer les classes spécifiques aux composants (`.hero-card__cta`, `.mini-card__badge`) — celles-ci restent dans leurs fichiers CSS
- Ne pas créer un grid system ou des classes de layout — `App.css` gère le layout
- Ne pas dupliquer ce qui est déjà dans `App.css` (ex: `.panel`)

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/styles/utilities.css` |
| Modifier | `frontend/src/main.tsx` (ajouter l'import) |
| Modifier | `frontend/src/styles/design-tokens.css` (ajouter `--color-text-adaptive` et `--color-surface-glass-blur`) |
| Ne pas modifier | Composants TSX — aucun style n'est appliqué dans cette story |

### Project Structure Notes

- `utilities.css` va dans `frontend/src/styles/` (cohérent avec `theme.css` et `backgrounds.css`)
- L'ordre des imports dans `main.tsx` est critique pour la spécificité CSS. Vérifier l'ordre exact après modification.

### References

- [Source: frontend/src/styles/design-tokens.css] (créé en 49.1 et complété en 49.2)
- [Source: frontend/src/main.tsx]
- [Source: frontend/src/App.css]
- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
