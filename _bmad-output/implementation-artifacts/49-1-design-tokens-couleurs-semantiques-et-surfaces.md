# Story 49.1: Créer design-tokens.css — variables de couleurs sémantiques, surfaces et status

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que toutes les variables de couleur (texte, fond, surfaces, badges, status, gradients) soient définies en un seul fichier `design-tokens.css`,
afin de pouvoir modifier n'importe quelle couleur du produit en changeant une seule déclaration.

## Acceptance Criteria

1. Le fichier `frontend/src/styles/design-tokens.css` existe et contient **toutes** les variables de couleur du produit organisées par catégorie sémantique.
2. Le support light/dark est géré par la classe `.dark` sur `<html>` ou `<body>`, sans duplication de logique en JSX.
3. Les variables existantes dans `index.css` et `theme.css` sont **préservées comme alias** pointant vers les nouveaux tokens (rétrocompatibilité totale, aucune régression visuelle).
4. Les couleurs de badges (`--badge-chat`, `--badge-consultation`, `--badge-amour`, `--badge-travail`, `--badge-energie`) sont centralisées dans `design-tokens.css`.
5. Les gradients de mini-cards (`--love-g1/g2`, `--work-g1/g2`, `--energy-g1/g2`) et les couleurs de constellation sont centralisés.
6. Le fichier est importé dans `frontend/src/main.tsx` **avant** `App.css` et `theme.css`.
7. Aucune régression visuelle sur les pages Dashboard, Daily Horoscope et Settings (light et dark).

## Tasks / Subtasks

- [ ] Tâche 1 : Créer `frontend/src/styles/design-tokens.css` (AC: 1, 2)
  - [ ] Section `/* === COULEURS PRIMITIVES === */` : palette de base (neutres, brand, status)
  - [ ] Section `/* === TEXTE === */` : `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-text-headline` pour light ET dark (via `.dark`)
  - [ ] Section `/* === FONDS === */` : `--color-bg-base`, `--color-bg-surface`, `--color-bg-elevated`, gradients `--color-bg-top/mid/bot`
  - [ ] Section `/* === SURFACES GLASS === */` : `--color-glass-bg`, `--color-glass-bg-2`, `--color-glass-border` pour light ET dark
  - [ ] Section `/* === BRAND/CTA === */` : `--color-cta-left`, `--color-cta-right`, `--color-primary`, `--color-primary-strong`, `--color-btn-text`
  - [ ] Section `/* === STATUS === */` : `--color-success`, `--color-error`, `--color-danger`, `--color-warning`
  - [ ] Section `/* === BADGES === */` : `--color-badge-chat`, `--color-badge-consultation`, `--color-badge-amour`, `--color-badge-travail`, `--color-badge-energie`
  - [ ] Section `/* === GRADIENTS THÉMATIQUES === */` : `--color-love-g1/g2`, `--color-work-g1/g2`, `--color-energy-g1/g2`
  - [ ] Section `/* === CONSTELLATION === */` : `--color-constellation` light et dark

- [ ] Tâche 2 : Ajouter les alias de rétrocompatibilité dans `theme.css` ou `index.css` (AC: 3)
  - [ ] `--text-1: var(--color-text-primary)` etc. pour chaque variable renommée
  - [ ] Vérifier que `App.css` et les composants qui utilisent les anciens noms ne cassent pas

- [ ] Tâche 3 : Mettre à jour l'ordre d'import dans `main.tsx` (AC: 6)
  - [ ] `import './styles/design-tokens.css'` en premier, avant `'./index.css'` et `'./App.css'`

- [ ] Tâche 4 : Validation visuelle (AC: 7)
  - [ ] Vérifier Dashboard light et dark mode visuellement
  - [ ] Vérifier Daily Horoscope light et dark mode
  - [ ] Vérifier Settings

## Dev Notes

### Contexte technique

**Stack frontend** : React 19 + Vite 7 + TypeScript. Pas de Tailwind, pas de CSS-in-JS. Tout est en variables CSS custom properties.

**Fichiers CSS actuels à conserver :**
- `frontend/src/index.css` — variables root actuelles + font family → garder, ajouter les alias
- `frontend/src/styles/theme.css` — dual-thème `.dark` → garder, les valeurs seront remplacées par des références aux nouveaux tokens
- `frontend/src/App.css` — layout et classes applicatives → ne pas toucher dans cette story

**Variables actuellement dans `index.css` :**
```css
--bg-base, --bg-sheen, --text-1, --text-2, --line,
--primary, --primary-strong, --danger, --success
```

**Variables actuellement dans `theme.css` (light + `.dark`) :**
```css
/* Texte */
--text-1, --text-2, --text-3, --text-headline
/* Fonds */
--bg-top, --bg-mid, --bg-bot
/* Glass */
--glass, --glass-2, --glass-border
/* CTA */
--cta-l, --cta-r
/* Status */
--success, --error, --btn-text
/* Badges */
--badge-chat, --badge-consultation, --badge-amour, --badge-travail, --badge-energie
/* Ombres */
--shadow-hero, --shadow-card, --shadow-nav, --shadow-cta (light et dark variants)
/* Mini-cards gradients */
--love-g1, --love-g2, --work-g1, --work-g2, --energy-g1, --energy-g2
/* Constellation */
--constellation-color
```

### Convention de nommage des nouveaux tokens

```
--color-{catégorie}-{rôle}        → couleurs
--color-{catégorie}-{rôle}-{état} → états hover/active/disabled
```

Exemples :
- `--color-text-primary` (remplace `--text-1`)
- `--color-text-secondary` (remplace `--text-2`)
- `--color-glass-bg` (remplace `--glass`)
- `--color-badge-amour` (inchangé dans le nom, déplacé dans le fichier centralisé)

### Ordre d'import recommandé dans `main.tsx`

```typescript
import './styles/design-tokens.css'  // ← NOUVEAU, en premier
import './index.css'                   // font, reset global
import './styles/theme.css'            // alias rétrocompat + overrides dark
import './App.css'                     // layout et classes applicatives
```

### Stratégie de rétrocompatibilité

**NE PAS** supprimer les anciens noms de variables dans cette story. Ajouter des alias dans `theme.css` :

```css
:root {
  /* Alias rétrocompatibilité — à supprimer en story 49.5 */
  --text-1: var(--color-text-primary);
  --text-2: var(--color-text-secondary);
  --glass: var(--color-glass-bg);
  /* ... etc */
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/styles/design-tokens.css` |
| Modifier | `frontend/src/main.tsx` (ordre d'import) |
| Modifier | `frontend/src/styles/theme.css` (alias rétrocompat) |
| Ne pas modifier | `frontend/src/App.css`, composants TSX |

### Project Structure Notes

- Le fichier `design-tokens.css` doit aller dans `frontend/src/styles/` (même dossier que `theme.css` et `backgrounds.css`)
- Le fichier `main.tsx` se trouve à `frontend/src/main.tsx`
- La classe dark est appliquée via `frontend/src/state/ThemeProvider.tsx` — vérifier qu'elle cible bien `document.documentElement` ou `document.body`

### References

- [Source: frontend/src/index.css]
- [Source: frontend/src/styles/theme.css]
- [Source: frontend/src/main.tsx]
- [Source: frontend/src/state/ThemeProvider.tsx]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
