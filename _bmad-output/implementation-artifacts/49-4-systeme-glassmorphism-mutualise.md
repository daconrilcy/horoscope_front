# Story 49.4: Créer le système .glass-card mutualisé et supprimer les doublons glassmorphism

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un système CSS de glassmorphism centralisé en classes `.glass-card` avec modificateurs,
afin que le pattern glass (blur, fond semi-transparent, bordure, pseudo-éléments) soit maintenu en un seul endroit plutôt que recodé de manière légèrement différente dans trois fichiers CSS distincts.

## Acceptance Criteria

1. Le fichier `frontend/src/styles/glass.css` existe avec la classe de base `.glass-card` et les modificateurs `.glass-card--hero`, `.glass-card--mini`, `.glass-card--shortcut`.
2. La classe `.glass-card` contient les propriétés communes : `backdrop-filter: blur(var(--surface-glass-blur))`, `background: var(--color-glass-bg)`, `border: 1px solid var(--color-glass-border)`.
3. `HeroHoroscopeCard.css` ne redéclare plus les propriétés glassmorphism de base — elles viennent de `.glass-card--hero`.
4. `MiniInsightCard.css` ne redéclare plus les propriétés glassmorphism de base — elles viennent de `.glass-card--mini`.
5. `ShortcutCard.css` ne redéclare plus les propriétés glassmorphism de base — elles viennent de `.glass-card--shortcut`.
6. Les composants TSX correspondants (`HeroHoroscopeCard.tsx`, `MiniInsightCard.tsx`, `ShortcutCard.tsx`) ajoutent la classe `glass-card glass-card--hero/mini/shortcut` sur l'élément racine.
7. Le rendu visuel des trois composants est **pixel-perfect identique** avant et après la migration.
8. `AstroMoodBackground.css` utilise `.glass-card` ou les tokens partagés pour ses styles glassmorphism si applicable.

## Tasks / Subtasks

- [ ] Tâche 1 : Analyser les trois fichiers CSS pour identifier l'intersection des styles (AC: 1, 2)
  - [ ] Lire entièrement `HeroHoroscopeCard.css`, `MiniInsightCard.css`, `ShortcutCard.css`
  - [ ] Lister les propriétés communes (backdrop-filter, background, border, -webkit-backdrop-filter)
  - [ ] Lister les propriétés spécifiques à chaque variante (min-height, border-radius, padding, pseudo-éléments gradient/noise)

- [ ] Tâche 2 : Créer `frontend/src/styles/glass.css` (AC: 1, 2)
  - [ ] Classe `.glass-card` : styles communs à tous les composants glass
  - [ ] Modificateur `.glass-card--hero` : surcharges spécifiques à HeroHoroscopeCard
  - [ ] Modificateur `.glass-card--mini` : surcharges spécifiques à MiniInsightCard
  - [ ] Modificateur `.glass-card--shortcut` : surcharges spécifiques à ShortcutCard
  - [ ] Importer `glass.css` dans `main.tsx` après `utilities.css`

- [ ] Tâche 3 : Mettre à jour `HeroHoroscopeCard.css` (AC: 3)
  - [ ] Supprimer les déclarations remplacées par `.glass-card`
  - [ ] Conserver uniquement les styles uniques au hero (min-height, constellation positioning, CTA button styles, pseudo-éléments spécifiques)

- [ ] Tâche 4 : Mettre à jour `MiniInsightCard.css` (AC: 4)
  - [ ] Supprimer les déclarations remplacées par `.glass-card`
  - [ ] Conserver les gradients thématiques `.mini-card--love/work/energy` et `.mini-card--clickable`

- [ ] Tâche 5 : Mettre à jour `ShortcutCard.css` (AC: 5)
  - [ ] Supprimer les déclarations remplacées par `.glass-card`
  - [ ] Conserver les styles de badge et layout spécifiques

- [ ] Tâche 6 : Mettre à jour les composants TSX (AC: 6)
  - [ ] `HeroHoroscopeCard.tsx` : ajouter `glass-card glass-card--hero` sur l'élément racine
  - [ ] `MiniInsightCard.tsx` : ajouter `glass-card glass-card--mini` sur l'élément racine
  - [ ] `ShortcutCard.tsx` : ajouter `glass-card glass-card--shortcut` sur l'élément racine

- [ ] Tâche 7 : Vérifier `AstroMoodBackground.css` (AC: 8)
  - [ ] Si `AstroMoodBackground` utilise un glassmorphism similaire → utiliser `.glass-card` ou les tokens
  - [ ] Sinon → documenter pourquoi il ne l'utilise pas (fond plein canvas, pas de glass)

- [ ] Tâche 8 : Validation visuelle (AC: 7)
  - [ ] Comparer Dashboard (Hero Card), Mini Insight Cards et Shortcut Cards avant/après
  - [ ] Tester light et dark mode
  - [ ] Tester mobile (375px) et desktop (1024px+)

## Dev Notes

### Contexte technique

**Prérequis** : Stories 49.1, 49.2 et 49.3 doivent être `done`.

**Stack** : React 19 + CSS Modules-free (les CSS sont importés globalement). Les classes CSS sont appliquées via `className` en JSX.

### Analyse du pattern glassmorphism existant

**Pattern commun dans les 3 fichiers** (extrait approximatif) :
```css
/* Commun à hero, mini et shortcut */
background: var(--glass);           /* ou --glass-mini, --glass-shortcut */
border: 1px solid var(--glass-border);
backdrop-filter: blur(14px);
-webkit-backdrop-filter: blur(14px);
border-radius: [valeur spécifique];
```

**Spécificités hero** (`HeroHoroscopeCard.css`) :
- `::before` : radial gradient interne avec couleurs premium
- `::after` : noise texture SVG feTurbulence
- `.hero-card__chip` : pill shape
- `.hero-card__constellation` : positionnement absolu, mix-blend-mode screen
- `.hero-card__cta` : bouton gradient avec hover states

**Spécificités mini** (`MiniInsightCard.css`) :
- Gradients thématiques par modificateur (love, work, energy)
- État clickable avec effet hover lift

**Spécificités shortcut** (`ShortcutCard.css`) :
- Layout badge + content flexbox
- `.shortcut-card__badge` avec border-radius 16px

### Tokens utilisés dans `glass.css`

Les classes `glass-card` référencent les tokens définis en 49.1/49.2 :
```css
.glass-card {
  background: var(--color-glass-bg);
  border: 1px solid var(--color-glass-border);
  backdrop-filter: blur(var(--surface-glass-blur, 14px));
  -webkit-backdrop-filter: blur(var(--surface-glass-blur, 14px));
}
```

### Attention : pseudo-éléments et `::before`/`::after`

Les pseudo-éléments de `HeroHoroscopeCard.css` (gradient noise) sont spécifiques à cette carte et **ne doivent pas** aller dans `.glass-card`. Ils restent dans `HeroHoroscopeCard.css` ou passent dans `.glass-card--hero::before` et `.glass-card--hero::after`.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/styles/glass.css` |
| Modifier | `frontend/src/main.tsx` (ajouter import glass.css) |
| Modifier | `frontend/src/components/HeroHoroscopeCard.css` |
| Modifier | `frontend/src/components/MiniInsightCard.css` |
| Modifier | `frontend/src/components/ShortcutCard.css` |
| Modifier | `frontend/src/components/HeroHoroscopeCard.tsx` (className) |
| Modifier | `frontend/src/components/MiniInsightCard.tsx` (className) |
| Modifier | `frontend/src/components/ShortcutCard.tsx` (className) |
| Vérifier | `frontend/src/components/astro/AstroMoodBackground.css` |

### Project Structure Notes

- `glass.css` dans `frontend/src/styles/` (cohérent avec `theme.css`, `backgrounds.css`, `utilities.css`)
- Les fichiers CSS de composants (`HeroHoroscopeCard.css`) restent à côté de leur composant dans `frontend/src/components/`
- Ne pas déplacer les fichiers CSS de composants — seulement supprimer les lignes redondantes

### References

- [Source: frontend/src/components/HeroHoroscopeCard.css]
- [Source: frontend/src/components/MiniInsightCard.css]
- [Source: frontend/src/components/ShortcutCard.css]
- [Source: frontend/src/components/HeroHoroscopeCard.tsx]
- [Source: frontend/src/components/MiniInsightCard.tsx]
- [Source: frontend/src/components/ShortcutCard.tsx]
- [Source: frontend/src/components/astro/AstroMoodBackground.css]
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
