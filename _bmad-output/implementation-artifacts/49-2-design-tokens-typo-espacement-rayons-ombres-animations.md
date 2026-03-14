# Story 49.2: Étendre design-tokens.css — typographie, espacement, rayons, ombres et animations

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que toutes les valeurs de typographie, espacement, rayons de bordure, ombres et durées d'animation soient définies comme tokens CSS dans `design-tokens.css`,
afin de modifier le rythme visuel du produit (taille de texte, padding, coins arrondis) en changeant une seule valeur.

## Acceptance Criteria

1. `design-tokens.css` est complété avec des sections pour typographie, espacement, rayons, ombres et animations.
2. Une échelle typographique complète est définie : tailles de `--font-size-xs` à `--font-size-2xl`, poids de `--font-weight-regular` à `--font-weight-bold`, et hauteurs de ligne `--line-height-tight/normal/relaxed`.
3. Une échelle d'espacement est définie de `--space-1` (4px) à `--space-12` (48px).
4. Les rayons de bordure sont standardisés : `--radius-sm` (8px), `--radius-md` (14px), `--radius-lg` (20px), `--radius-xl` (28px), `--radius-full` (999px).
5. Les variables d'ombre (`--shadow-hero`, `--shadow-card`, `--shadow-nav`, `--shadow-cta`) déjà dans `theme.css` sont déplacées dans `design-tokens.css` avec support light/dark.
6. Des tokens d'animation sont définis : `--duration-fast` (150ms), `--duration-normal` (250ms), `--duration-slow` (400ms), `--easing-default`, `--easing-bounce`.
7. Aucune régression visuelle ni de comportement sur aucune page du produit.

## Tasks / Subtasks

- [ ] Tâche 1 : Ajouter la section typographie dans `design-tokens.css` (AC: 2)
  - [ ] `--font-size-xs: 0.75rem` (12px)
  - [ ] `--font-size-sm: 0.875rem` (14px)
  - [ ] `--font-size-md: 1rem` (16px)
  - [ ] `--font-size-lg: 1.125rem` (18px) ← valeur magique courante dans DayPredictionCard
  - [ ] `--font-size-xl: 1.25rem` (20px)
  - [ ] `--font-size-2xl: 1.5rem` (24px)
  - [ ] `--font-weight-regular: 400`, `--font-weight-medium: 500`, `--font-weight-semibold: 600`, `--font-weight-bold: 700`
  - [ ] `--line-height-tight: 1.25`, `--line-height-normal: 1.5`, `--line-height-relaxed: 1.6` ← 1.6 est déjà dans DayPredictionCard

- [ ] Tâche 2 : Ajouter la section espacement dans `design-tokens.css` (AC: 3)
  - [ ] `--space-1: 0.25rem` (4px) à `--space-12: 3rem` (48px) en pas de 4px
  - [ ] Identifier les valeurs magiques récurrentes : `0.5rem`, `1rem`, `1.5rem`, `2rem`, `28px`, `32px`

- [ ] Tâche 3 : Ajouter la section rayons dans `design-tokens.css` (AC: 4)
  - [ ] `--radius-sm: 8px`, `--radius-md: 14px`, `--radius-lg: 20px`, `--radius-xl: 28px`, `--radius-full: 999px`
  - [ ] Documenter l'usage de chaque rayon (ex: `--radius-xl` → AstroMoodBackground, cards principales)

- [ ] Tâche 4 : Migrer les ombres depuis `theme.css` vers `design-tokens.css` (AC: 5)
  - [ ] Déplacer `--shadow-hero`, `--shadow-card`, `--shadow-nav`, `--shadow-cta` (light + dark) vers `design-tokens.css`
  - [ ] Ajouter les alias dans `theme.css` pour la rétrocompatibilité

- [ ] Tâche 5 : Ajouter la section animations dans `design-tokens.css` (AC: 6)
  - [ ] `--duration-fast: 150ms`, `--duration-normal: 250ms`, `--duration-slow: 400ms`
  - [ ] `--easing-default: cubic-bezier(0.4, 0, 0.2, 1)` (Material standard)
  - [ ] `--easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1)`

- [ ] Tâche 6 : Validation (AC: 7)
  - [ ] Vérifier que toutes les pages sont visuellement identiques avant/après

## Dev Notes

### Contexte technique

Cette story complète le travail de la story 49.1. Elle nécessite que `design-tokens.css` existe déjà avec les variables de couleur.

**Prérequis** : Story 49.1 doit être `done` avant de démarrer cette story.

### Valeurs magiques actuellement dans le code à transformer en tokens

Relevé des valeurs inline dans `DayPredictionCard.tsx` (à remplacer par les tokens) :
```
marginTop: '1.5rem'        → var(--space-6)
fontSize: "1.125rem"       → var(--font-size-lg)
lineHeight: "1.6"          → var(--line-height-relaxed)
```

Relevé dans `DashboardHoroscopeSummaryCard.tsx` :
```
marginBottom: "0.5rem"     → var(--space-2)
```

Relevé dans `AstroMoodBackground.css` :
```
border-radius: 28px        → var(--radius-xl)
padding: 32px 28px         → var(--space-8) var(--space-7)
```

Relevé dans `HeroHoroscopeCard.css` :
```
min-height: 312px          → valeur spécifique au composant, ne pas tokeniser
border-radius: (divers)    → remplacer par --radius-xl, --radius-lg
height: 48px               → var(--space-12) ou token dédié --size-btn-lg
```

### Structure finale de `design-tokens.css`

```css
/* === 1. COULEURS PRIMITIVES === */
/* === 2. TEXTE === */          ← story 49.1
/* === 3. FONDS ET SURFACES === */  ← story 49.1
/* === 4. BRAND / CTA === */   ← story 49.1
/* === 5. STATUS === */         ← story 49.1
/* === 6. BADGES === */         ← story 49.1
/* === 7. GRADIENTS THÉMATIQUES === */ ← story 49.1
/* === 8. TYPOGRAPHIE === */    ← cette story
/* === 9. ESPACEMENT === */     ← cette story
/* === 10. RAYONS === */        ← cette story
/* === 11. OMBRES === */        ← cette story (migration depuis theme.css)
/* === 12. ANIMATIONS === */    ← cette story
```

### Notes sur les ombres

Les ombres actuelles dans `theme.css` ont des valeurs différentes pour light et dark mode. Elles doivent rester dans des blocs `:root` et `.dark` dans `design-tokens.css`. Exemple :

```css
:root {
  --shadow-card: 0 4px 24px rgba(120, 80, 200, 0.10);
}
.dark {
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.40);
}
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/styles/design-tokens.css` (compléter les sections) |
| Modifier | `frontend/src/styles/theme.css` (alias pour les ombres migrées) |
| Ne pas modifier | Composants TSX ou autres CSS dans cette story |

### Project Structure Notes

- Ne pas modifier `App.css` dans cette story
- Les valeurs de rayon spécifiques à un seul composant (ex: `border-radius: 16px` dans `.shortcut-card__badge`) restent locales pour l'instant — elles seront traitées en story 49.4

### References

- [Source: frontend/src/styles/design-tokens.css] (créé en 49.1)
- [Source: frontend/src/styles/theme.css]
- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/astro/AstroMoodBackground.css]
- [Source: frontend/src/components/HeroHoroscopeCard.css]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]
- [Source: _bmad-output/implementation-artifacts/49-1-design-tokens-couleurs-semantiques-et-surfaces.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
