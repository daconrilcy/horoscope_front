# Story 58.9 : HeroSummaryCard — Bloc hero premium de la page horoscope quotidien

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir une grande carte synthèse visuelle premium qui remplace l'actuelle `DayPredictionCard` avec un titre de tonalité impactant, le résumé narratif, la meilleure fenêtre de la journée et les tags domaines,
afin d'avoir une lecture immédiate et émotionnellement engageante de ma journée, sur fond d'étoiles animées.

## Acceptance Criteria

1. Le composant `HeroSummaryCard` est créé à `frontend/src/components/prediction/HeroSummaryCard.tsx`. Il utilise `AstroMoodBackground` comme conteneur (fond d'étoiles animées) — **les étoiles animées sont obligatoires et doivent rester**.
2. `HeroSummaryCard` accepte les props `model: HeroSummaryCardModel` et `lang: Lang`. Les données ne sont **jamais** calculées dans le composant — elles sont reçues via le view model déjà normalisé.
3. Le mapper `buildHeroSummaryCardModel()` est créé dans `frontend/src/utils/heroSummaryCardMapper.ts`. Il transforme `(prediction: DailyPredictionResponse, sign: ZodiacSign, userId: string, dayScore: number, lang: Lang) → HeroSummaryCardModel`.
4. La structure JSX interne cible est :
   ```
   AstroMoodBackground (fond étoiles animées)
   └── .hero-summary-card__inner
       ├── .hero-summary-card__content
       │   ├── h2.hero-summary-card__title
       │   │   ├── span (texte plat)
       │   │   └── span.hero-summary-card__title-highlight (mot accentué en violet)
       │   ├── p.hero-summary-card__subtitle  (overall_summary)
       │   ├── p.hero-summary-card__calibration  (si is_provisional_calibration)
       │   ├── div.hero-summary-card__divider
       │   ├── div.hero-summary-card__insight-row  (best_window si présent)
       │   └── div.hero-summary-card__tags-row  (top 3–4 catégories)
       └── div.hero-summary-card__visual (décor CSS, aria-hidden)
   ```
5. Le layout est **1 colonne sur mobile** ; **2 colonnes sur tablette (≥ 768px) et desktop (≥ 1024px)** : contenu à gauche, visuel décoratif à droite.
6. `DailyHoroscopePage.tsx` remplace le bloc `DayPredictionCard` (Zone 2) par `HeroSummaryCard` alimenté par `buildHeroSummaryCardModel()`. L'import de `DayPredictionCard` est retiré de la page (le fichier `DayPredictionCard.tsx` est conservé intact pour d'éventuels autres usages).
7. Les tests existants dans `DailyHoroscopePage.test.tsx` passent tous sans modification :
   - `overall_summary` reste visible (dans `.hero-summary-card__subtitle`)
   - "Best window" / "Meilleur créneau" reste visible (dans `.hero-summary-card__insight-row`)
   - "Dominant : Career" reste visible (dans `.hero-summary-card__insight-row`)
   - La note de calibration provisoire reste visible (dans `.hero-summary-card__calibration`)
8. Aucun style Tailwind. CSS custom vars du projet uniquement.
9. La `HeroVisual` droite est un décor CSS pur (glow radial + quelques points) — **pas d'image externe** car il n'en existe pas dans le projet. Si une `visual.src` est fournie dans le modèle, l'afficher via `<img>` avec lazy-loading et alt.
10. `prefers-reduced-motion` : le flottement de la `HeroVisual` doit être désactivé si la media query est active.
11. `tsc --noEmit` passe sans erreur. La suite Vitest complète (≥ 1071 tests) passe.

## Tasks / Subtasks

- [x] T1 — Créer les types et le mapper `buildHeroSummaryCardModel` (AC: 2, 3)
  - [x] T1.1 Créer `frontend/src/utils/heroSummaryCardMapper.ts` avec les types et la fonction
- [x] T2 — Créer `HeroSummaryCard.tsx` (AC: 1, 2, 4, 9, 10)
  - [x] T2.1 Créer `frontend/src/components/prediction/HeroSummaryCard.tsx`
- [x] T3 — Créer `HeroSummaryCard.css` (AC: 5, 8, 10)
  - [x] T3.1 Créer `frontend/src/components/prediction/HeroSummaryCard.css`
- [x] T4 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 6, 7)
  - [x] T4.1 Ajouter les imports
  - [x] T4.2 Retirer l'import `DayPredictionCard`
  - [x] T4.3 Remplacer la Zone 2 dans le rendu `prediction ? (...)`
  - [x] T4.4 Nettoyer l'import de `getCategoryLabel`
- [x] T5 — Validation et non-régression (AC: 11)
  - [x] T5.1 `tsc --noEmit` — 0 erreur TypeScript
  - [x] T5.2 `npx vitest run src/tests/DailyHoroscopePage.test.tsx` — 17/17 tests verts
  - [x] T5.3 `npx vitest run` global — ≥ 1071 tests verts

## Dev Notes

### Point critique n°1 — Les étoiles animées DOIVENT rester

`AstroMoodBackground` est un canvas WebGL/2D avec des étoiles animées, une constellation zodiacale, et des étoiles filantes. C'est le fond visuel premium de la carte. Il **doit** être le conteneur racine de `HeroSummaryCard`.

Interface exacte de `AstroMoodBackground` :
```tsx
interface AstroMoodBackgroundProps extends PropsWithChildren {
  sign: ZodiacSign       // signe zodiacal (ex: "aries", "pisces", "neutral")
  userId: string         // pour la graine du générateur aléatoire déterministe
  dateKey: string        // ex: "2026-03-16" — change les patterns jour/jour
  dayScore?: number      // 1..20, affecte la palette de couleurs
  className?: string     // CSS appliqué sur le wrapper div
}
```

Le composant rend :
```html
<div class="astro-mood-background {className}">
  <canvas aria-hidden="true" />
  <div class="astro-mood-background__content astro-context">
    {children}  ← notre hero-summary-card__inner va ici
  </div>
</div>
```

La classe `.astro-context` est déjà définie dans le CSS du projet et affecte les styles des enfants (ex: `.astro-context .day-prediction-card__calibration`). Notre `HeroSummaryCard` n'utilise pas ces overrides `.astro-context` — elle a ses propres classes.

### Point critique n°2 — Surcharge du border-radius AstroMoodBackground

`AstroMoodBackground` ne définit pas de `border-radius` dans son CSS. Le shell glass `DayPredictionCard` utilise la classe `.panel` pour ça. Pour `HeroSummaryCard`, on applique `border-radius: 32px !important` directement sur la classe `.hero-summary-card` donnée en `className` à `AstroMoodBackground`.

### Point critique n°3 — Tests existants à ne pas casser

Les tests de `DailyHoroscopePage.test.tsx` cherchent ces textes dans le DOM :

| Test | Texte cherché | Source dans HeroSummaryCard |
|---|---|---|
| `it("affiche la prediction API...")` | `overall_summary` | `.hero-summary-card__subtitle` |
| `it("bascule les libelles en anglais")` | `"Best window"` | `.hero-summary-card__insight-label` |
| `it("bascule les libelles en anglais")` | `"Dominant : Career"` | `.hero-summary-card__insight-category` |
| `it("humanise les payloads techniques")` | `overall_summary` + calibration note | `.hero-summary-card__subtitle` + `.hero-summary-card__calibration` |

Le test `it("bascule les libelles en anglais")` vérifie aussi :
```js
expect(screen.getByText("Dominant : Career")).toBeInTheDocument();
```

Dans le mapper :
```ts
categoryLabel: `${getPredictionMessage('dominant', lang)} : ${getCategoryLabel(dominant_category, lang)}`
```
→ donne `"Dominant : Career"` en EN. ✅

### Point critique n°4 — `getCategoryLabel` vs `getCategoryMeta`

- `getCategoryLabel(code, lang)` → retourne le label i18n de la catégorie
- `getCategoryMeta(code, lang)` → retourne `{ label, icon }`

Les deux sont dans `frontend/src/utils/predictionI18n.ts`. Utiliser `getCategoryMeta` pour les tags (label + icône), et `getCategoryLabel` pour les insights (juste le label).

### Point critique n°5 — `import type` obligatoire

Avec `verbatimModuleSyntax: true` dans le tsconfig, tous les types doivent être importés avec `import type` :

```ts
// ✅ Correct
import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { ZodiacSign } from '../components/astro/zodiacPatterns'

// ❌ Incorrect
import { DailyPredictionResponse } from '../types/dailyPrediction'
```

### Point critique n°6 — `getCategoryLabel` dans AdviceCard

Dans `DailyHoroscopePage.tsx`, `getCategoryLabel` est encore utilisé dans la **Zone 6 AdviceCard** :
```tsx
{getCategoryLabel(prediction.summary.best_window.dominant_category, lang)}
```
→ Ne pas retirer cet import si la Zone 6 est conservée.

### AstroMoodBackground — récupération de `sign` et `dayScore`

Dans `DailyHoroscopePage.tsx`, déjà disponibles :
```ts
const { sign, dayScore } = useDashboardAstroSummary(accessToken)
// sign : ZodiacSign (ex: "neutral" si non déterminé)
// dayScore : number (1..20, basé sur le score global de la prédiction)
```

Et `userId` :
```ts
user?.id ? String(user.id) : 'anonymous'
```

### Architecture des fichiers

| Action | Fichier |
|---|---|
| Créer | `frontend/src/components/prediction/HeroSummaryCard.tsx` |
| Créer | `frontend/src/components/prediction/HeroSummaryCard.css` |
| Créer | `frontend/src/utils/heroSummaryCardMapper.ts` |
| Modifier | `frontend/src/pages/DailyHoroscopePage.tsx` |
| Conserver intact | `frontend/src/components/prediction/DayPredictionCard.tsx` |

### CSS — aucune variable fictive

Variables interdites (n'existent pas dans le projet) : `--ink-strong`, `--ink-mid`, `--purple-500`, `--glass`, `--glass-border`

Variables autorisées : `--color-text-primary`, `--color-text-secondary`, `--color-primary`, `--color-primary-strong`, `--color-purple-2`, `--color-glass-bg`, `--color-glass-border`, `--space-*`, `--radius-*`, `--font-weight-*`, `--shadow-*`

Les textes **sur fond d'étoiles** (`AstroMoodBackground`) sont sur fond sombre → utiliser `rgba(255, 255, 255, X)` pour les couleurs de texte, pas `var(--color-text-primary)` (qui est `#1E1B2E` en light mode).

### Responsive grid

```
mobile (< 768px)
└── .hero-summary-card__inner : grid 1 colonne
    ├── .hero-summary-card__content (100%)
    └── .hero-summary-card__visual  display: none

tablet (768px–1023px)
└── .hero-summary-card__inner : grid 1.2fr 0.8fr
    ├── .hero-summary-card__content
    └── .hero-summary-card__visual  display: flex

desktop (≥ 1024px)
└── .hero-summary-card__inner : grid 1.15fr 0.85fr
    ├── .hero-summary-card__content
    └── .hero-summary-card__visual  display: flex (plus grand)
```

### Project Structure Notes

- Composants prédiction : `frontend/src/components/prediction/`
- Utilitaires : `frontend/src/utils/`
- AstroMoodBackground : `frontend/src/components/astro/AstroMoodBackground.tsx`
- ZodiacSign type : `frontend/src/components/astro/zodiacPatterns.ts`
- useDashboardAstroSummary : `frontend/src/components/dashboard/useDashboardAstroSummary.ts`

### References

- Story 58.7 (layout page) : `_bmad-output/implementation-artifacts/58-7-refonte-layout-page-horoscope-quotidien.md`
- Story 58.8 (header éditorial) : `_bmad-output/implementation-artifacts/58-8-daily-page-header-bar.md`
- DayPredictionCard (remplacé) : `frontend/src/components/prediction/DayPredictionCard.tsx`
- AstroMoodBackground (conservé) : `frontend/src/components/astro/AstroMoodBackground.tsx`
- AstroMoodBackground CSS : `frontend/src/components/astro/AstroMoodBackground.css`
- Types prédiction : `frontend/src/types/dailyPrediction.ts`
- predictionI18n utils : `frontend/src/utils/predictionI18n.ts`
- Tone codes (API → label) : `frontend/src/i18n/predictions.ts` lignes 42–51
- design-tokens.css : `frontend/src/styles/design-tokens.css`
- DailyHoroscopePage.test.tsx : `frontend/src/tests/DailyHoroscopePage.test.tsx`
- DailyHoroscopePage : `frontend/src/pages/DailyHoroscopePage.tsx`

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp (orchestrated by Gemini CLI)

### Debug Log References

- Started implementation of Story 58.9.
- Created `heroSummaryCardMapper.ts` with types and transformation logic.
- Created `HeroSummaryCard.tsx` using `AstroMoodBackground` and custom CSS.
- Integrated `HeroSummaryCard` into `DailyHoroscopePage.tsx` replacing `DayPredictionCard`.
- Verified type safety with `npx tsc --noEmit`.
- Verified component behavior and non-regression with `npx vitest run src/tests/DailyHoroscopePage.test.tsx`.

### Completion Notes List

- ✅ Component `HeroSummaryCard` created and styled with premium glassmorphism.
- ✅ Mapper `buildHeroSummaryCardModel` implemented for clean data transformation.
- ✅ Integrated into `DailyHoroscopePage.tsx` as per the new design layout.
- ✅ All existing tests in `DailyHoroscopePage.test.tsx` are passing.
- ✅ No TypeScript errors.

### Post-implementation visual refinements (2026-03-16)

Suite à review visuelle sur inspiration de design, les ajustements suivants ont été apportés :

**Mapper (`heroSummaryCardMapper.ts`)**
- Préfixe titre changé : `'Journée '` → `'Une journée '` (FR) / `'A '` (EN)
- Nouveau champ `astroTheme: string | null` dans `HeroSummaryCardModel` — phrase construite depuis `top_categories` + `overall_tone` (ex : "Journée équilibrée, principalement orientée sur Carrière et Travail."). Les `category.summary` de l'API sont **exclus** car ils contiennent des payloads techniques.

**Composant (`HeroSummaryCard.tsx`)**
- Zone `hero-summary-card__astro-theme` (icône ✦ + texte italique) remplace la `calibration` au centre.
- `calibrationNote` déplacé en bas : classe `hero-summary-card__calibration-nb` avec préfixe `NB` discret (0.72rem, couleur subtle).

**CSS (`HeroSummaryCard.css`)**
- Overlay `::before` sur `.hero-summary-card` entre canvas et contenu : `rgba(255,255,255,0.90→0)` pour faire basculer le fond étoilé vers le blanc dès la colonne gauche. Désactivé en dark mode (`.dark .hero-summary-card::before { background: none }`).
- Colonne visuelle droite : 3 sphères en verre superposées — orbe principal via `.hero-summary-card__visual-orb`, petite sphère via `.hero-summary-card__visual::before`, micro sphère via `.hero-summary-card__visual::after`. Chacune a reflets internes, ombres violettes et flottement décalé.
- Barre soulignée sous le titre via `::after` (gradient `--color-hero-ink-muted → transparent`).
- Titre highlight : `font-weight: 700` (bold).

**`AstroMoodBackground.tsx`**
- Stops du gradient canvas décalés de `(0 / 0.35 / 0.72 / 1)` à `(0 / 0.52 / 0.84 / 1)` pour que `palette.left` (blanc/lavande clair) reste dominant sur la moitié gauche.

**`design-tokens.css`**
- 5 nouvelles variables centralisées (light + dark mode) :
  - `--color-hero-ink` : `#3B2874` (light) / `rgba(245,240,255,0.92)` (dark)
  - `--color-hero-ink-muted`, `--color-hero-ink-subtle`, `--color-hero-ink-accent`
  - `--shadow-hero-card` : ombre décalée bas-droite violet

### File List

- `frontend/src/utils/heroSummaryCardMapper.ts`
- `frontend/src/components/prediction/HeroSummaryCard.tsx`
- `frontend/src/components/prediction/HeroSummaryCard.css`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/styles/design-tokens.css`
