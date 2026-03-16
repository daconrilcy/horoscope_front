# Story 58.8 : DailyPageHeader — HeaderBar éditorial de la page horoscope quotidien

Status: ready-for-dev

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir un header compact et élégant qui affiche la date du jour en grande typographie et un badge de tonalité, sans aucun contrôle utilitaire,
afin de m'immerger immédiatement dans le contexte de ma journée avant de lire la hero card.

## Acceptance Criteria

1. Le composant `DailyPageHeader` est créé à `frontend/src/components/prediction/DailyPageHeader.tsx`. Il accepte les props `date: string` (ISO), `tone: string | null`, `lang: Lang` et rend un `<header>` avec classe `daily-page-header`.
2. Le sous-composant `DayStateBadge` est créé à `frontend/src/components/prediction/DayStateBadge.tsx`. Il accepte les props `label: string`, `tone?: string | null`, `size?: "sm" | "md"` et affiche un badge glassmorphism pill avec : icône subtile, label en uppercase, point coloré.
3. `DayStateBadge` dérive sa variante visuelle (`balanced | dynamic | calm | intense | reflective`) depuis le `tone` de l'API — voir table de mapping dans les Dev Notes.
4. Le `HeaderDate` affiche la date au format "16 mars 2026" en `clamp(2rem, 4vw, 3.25rem)`, font-weight 500, letter-spacing négatif, via `toLocaleDateString` avec le `locale` dérivé de `lang`.
5. La structure HTML cible est strictement : `<header.daily-page-header> > <div.daily-page-header__content> > [h1.header-date] + [DayStateBadge]`. Pas d'éléments utilitaires (pas de refresh, pas d'avatar, pas de toggle thème).
6. Sur desktop (≥ 768px), un `<div.daily-page-header__decoration>` optionnel peut contenir une `AmbientGlow` (simple `div` avec `position: absolute` et dégradé radial violet flou, `pointer-events: none`). Sur mobile, la décoration est absente (`display: none`).
7. `DailyHoroscopePage.tsx` remplace la `<div className="daily-layout__header-bar">` (définie en story 58.7) par `<DailyPageHeader date={prediction.meta.date_local} tone={prediction.summary.overall_tone} lang={lang} />`. Le bouton refresh reste dans une `<div className="daily-layout__refresh-row">` séparée, juste après le `DailyPageHeader`.
8. Zéro style Tailwind. CSS custom vars du projet uniquement. Les variables `--ink-strong` et `--purple-500` du spec de design **ne sont pas dans le projet** — utiliser `var(--color-text-primary)` et `var(--color-primary)` à la place.
9. `tsc --noEmit` passe sans erreur. Les tests `DailyHoroscopePage.test.tsx` existants continuent de passer.
10. Les clés i18n `day_state_label` (libellé "Tonalité du jour" / "Day mood") sont ajoutées dans `predictionI18n.ts` pour le `aria-label` du badge.

## Tasks / Subtasks

- [ ] T1 — Créer `DayStateBadge.tsx` (AC: 2, 3, 8)
  - [ ] T1.1 Créer `frontend/src/components/prediction/DayStateBadge.tsx` :
    ```tsx
    import React from 'react'
    import type { Lang } from '../../i18n/predictions'
    import { getPredictionMessage } from '../../utils/predictionI18n'
    import './DayStateBadge.css'

    type ToneVariant = 'balanced' | 'dynamic' | 'calm' | 'intense' | 'reflective'

    function deriveToneVariant(tone: string | null | undefined): ToneVariant {
      switch (tone) {
        case 'positive':
        case 'push':
          return 'dynamic'
        case 'negative':
          return 'intense'
        case 'careful':
          return 'reflective'
        case 'mixed':
        case 'open':
          return 'calm'
        case 'neutral':
        case 'steady':
        default:
          return 'balanced'
      }
    }

    interface Props {
      label: string
      tone?: string | null
      lang: Lang
      size?: 'sm' | 'md'
    }

    export const DayStateBadge: React.FC<Props> = ({ label, tone, lang, size = 'md' }) => {
      const variant = deriveToneVariant(tone)
      const ariaLabel = `${getPredictionMessage('day_state_label', lang)} : ${label}`

      return (
        <div
          className={`day-state-badge day-state-badge--${variant} day-state-badge--${size}`}
          aria-label={ariaLabel}
          role="status"
        >
          <span className="day-state-badge__icon" aria-hidden="true">✦</span>
          <span className="day-state-badge__label">{label}</span>
          <span className="day-state-badge__dot" aria-hidden="true" />
        </div>
      )
    }
    ```
  - [ ] T1.2 Créer `frontend/src/components/prediction/DayStateBadge.css` (voir section CSS dans Dev Notes)

- [ ] T2 — Créer `DailyPageHeader.tsx` (AC: 1, 4, 5, 6)
  - [ ] T2.1 Créer `frontend/src/components/prediction/DailyPageHeader.tsx` :
    ```tsx
    import React from 'react'
    import type { Lang } from '../../i18n/predictions'
    import { getToneLabel } from '../../utils/predictionI18n'
    import { getLocale } from '../../utils/locale'
    import { DayStateBadge } from './DayStateBadge'
    import './DailyPageHeader.css'

    interface Props {
      date: string      // ISO date string, ex: "2026-03-16"
      tone: string | null
      lang: Lang
    }

    export const DailyPageHeader: React.FC<Props> = ({ date, tone, lang }) => {
      const locale = getLocale(lang)
      const toneLabel = getToneLabel(tone, lang)

      const formattedDate = new Date(date).toLocaleDateString(locale, {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      })

      return (
        <header className="daily-page-header">
          <div className="daily-page-header__content">
            <h1 className="header-date">{formattedDate}</h1>
            <DayStateBadge label={toneLabel} tone={tone} lang={lang} />
          </div>
          <div className="daily-page-header__decoration" aria-hidden="true">
            <div className="daily-page-header__ambient-glow" />
          </div>
        </header>
      )
    }
    ```
  - [ ] T2.2 Créer `frontend/src/components/prediction/DailyPageHeader.css` (voir section CSS dans Dev Notes)

- [ ] T3 — Ajouter la clé i18n `day_state_label` (AC: 10)
  - [ ] T3.1 Dans `frontend/src/utils/predictionI18n.ts`, ajouter dans `MESSAGES` :
    ```ts
    day_state_label: { fr: 'Tonalité du jour', en: 'Day mood' },
    ```

- [ ] T4 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 7)
  - [ ] T4.1 Ajouter l'import :
    ```ts
    import { DailyPageHeader } from '../components/prediction/DailyPageHeader'
    ```
  - [ ] T4.2 Remplacer le bloc `daily-layout__header-bar` (story 58.7) par :
    ```tsx
    {/* Zone 1 : DailyPageHeader éditorial */}
    <DailyPageHeader
      date={prediction.meta.date_local}
      tone={prediction.summary.overall_tone}
      lang={lang}
    />

    {/* Bouton refresh — séparé du header éditorial */}
    <div className="daily-layout__refresh-row">
      <button
        type="button"
        className="daily-page-refresh-button"
        onClick={handleRefresh}
        aria-label={getPredictionMessage('refresh', lang)}
      >
        <RefreshCw size={15} aria-hidden="true" />
      </button>
    </div>
    ```
  - [ ] T4.3 Supprimer les imports devenus inutiles dans `DailyHoroscopePage.tsx` si `toneLabel`, `toneColor`, `formattedDate` n'étaient plus calculés localement (ces calculs migrent dans `DailyPageHeader`)
  - [ ] T4.4 Ajouter dans `DailyHoroscopePage.css` :
    ```css
    .daily-layout__refresh-row {
      display: flex;
      justify-content: flex-end;
      margin-top: calc(-1 * var(--space-4, 1rem));
    }
    ```

- [ ] T5 — Validation et non-régression (AC: 9)
  - [ ] T5.1 `tsc --noEmit` — 0 erreur TypeScript
  - [ ] T5.2 `npx vitest run src/tests/DailyHoroscopePage.test.tsx` — tous les tests passent
  - [ ] T5.3 `npx vitest run` global — ≥ 1071 tests verts

## Dev Notes

### Mapping tone API → variante visuelle DayStateBadge

| Tone API | Variante | Palette | Description |
|---|---|---|---|
| `positive`, `push` | `dynamic` | violet lumineux | Journée favorable, élan |
| `neutral`, `steady` | `balanced` | violet doux | Journée équilibrée |
| `mixed`, `open` | `calm` | lavande/gris | Journée nuancée |
| `negative` | `intense` | prune dense | Journée exigeante |
| `careful` | `reflective` | bleu-violet froid | Journée de prudence |
| `null` / inconnu | `balanced` | violet doux | Fallback |

### CSS `DayStateBadge.css` — cible complète

```css
/* Base pill glassmorphism */
.day-state-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3, 0.75rem);
  min-height: 40px;
  padding: 0 var(--space-4, 1rem);
  border-radius: var(--radius-full, 999px);
  border: 1px solid rgba(140, 120, 210, 0.22);
  background: var(--color-glass-bg, rgba(255,255,255,0.55));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(122, 88, 220, 0.08);
}

.day-state-badge--sm {
  min-height: 32px;
  padding: 0 var(--space-3, 0.75rem);
  gap: var(--space-2, 0.5rem);
}

/* Label */
.day-state-badge__label {
  font-size: 0.875rem;
  font-weight: var(--font-weight-semibold, 600);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-secondary);
}

/* Icon */
.day-state-badge__icon {
  font-size: 0.75rem;
  opacity: 0.6;
  color: var(--color-primary);
}

/* Dot */
.day-state-badge__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* === Variantes de tone === */

/* balanced — violet doux */
.day-state-badge--balanced .day-state-badge__dot {
  background-color: var(--color-primary, #866CD0);
}

/* dynamic — violet lumineux */
.day-state-badge--dynamic {
  border-color: rgba(161, 144, 237, 0.35);
  box-shadow: 0 8px 24px rgba(122, 88, 220, 0.14);
}
.day-state-badge--dynamic .day-state-badge__dot {
  background-color: var(--color-primary-strong, #7355C7);
}
.day-state-badge--dynamic .day-state-badge__label {
  color: var(--color-primary, #866CD0);
}

/* calm — lavande/gris */
.day-state-badge--calm .day-state-badge__dot {
  background-color: var(--color-purple-2, #dfd5fc);
}

/* intense — prune dense */
.day-state-badge--intense {
  border-color: rgba(100, 60, 170, 0.30);
}
.day-state-badge--intense .day-state-badge__dot {
  background-color: #6B3FA0;
}

/* reflective — bleu-violet froid */
.day-state-badge--reflective {
  border-color: rgba(100, 130, 200, 0.28);
}
.day-state-badge--reflective .day-state-badge__dot {
  background-color: #7A9BD4;
}

/* dark mode : renforcer le fond glass */
.dark .day-state-badge {
  background: var(--color-glass-bg, rgba(255,255,255,0.08));
  border-color: var(--color-glass-border, rgba(255,255,255,0.12));
}
```

### CSS `DailyPageHeader.css` — cible complète

```css
/* Conteneur principal */
.daily-page-header {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4, 1rem);
  padding: var(--space-1, 0.25rem) 0 var(--space-2, 0.5rem);
  margin-bottom: 20px;
  overflow: hidden;
}

@media (max-width: 767px) {
  .daily-page-header {
    margin-bottom: 18px;
  }
}

/* Zone contenu (gauche) */
.daily-page-header__content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

/* Date dominante */
.header-date {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.25rem);
  line-height: 1.02;
  font-weight: var(--font-weight-medium, 500);
  letter-spacing: -0.04em;
  color: var(--color-text-primary);
}

/* Décoration (droite) — desktop seulement */
.daily-page-header__decoration {
  display: none;
  position: relative;
  width: 80px;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .daily-page-header__decoration {
    display: block;
  }
}

/* Ambient glow décoratif */
.daily-page-header__ambient-glow {
  position: absolute;
  top: -20px;
  right: -10px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(
    circle at center,
    rgba(134, 108, 208, 0.18) 0%,
    transparent 70%
  );
  pointer-events: none;
  filter: blur(16px);
}
```

### Variables CSS du projet à utiliser — mapping depuis le spec de design

Le spec de design utilise des variables fictives qui **n'existent pas** dans le projet. Voici le mapping obligatoire :

| Variable spec (fictive) | Variable projet (réelle) |
|---|---|
| `--ink-strong` | `var(--color-text-primary)` |
| `--ink-mid` | `var(--color-text-secondary)` |
| `--purple-500` | `var(--color-primary)` (#866CD0 light, #A190ED dark) |
| `--glass` | `var(--color-glass-bg)` |
| `--glass-border` | `var(--color-glass-border)` |

**Ne jamais introduire de nouvelles variables CSS racines** — utiliser uniquement celles de `design-tokens.css`.

### Principe de séparation éditorial / utilitaire

`DailyPageHeader` est **strictement éditorial** :
- ✅ Date, badge tonalité, ambient glow
- ❌ Bouton refresh, avatar, hamburger, toggle thème, tabs, CTA, sélecteur de date

Le bouton refresh reste dans `DailyHoroscopePage.tsx`, dans un `<div className="daily-layout__refresh-row">` positionné juste après `<DailyPageHeader>`.

### Positionnement dans le layout de la story 58.7

Story 58.7 prévoit une zone `daily-layout__header-bar` :
```tsx
// Story 58.7 (placeholder)
<div className="daily-layout__header-bar">
  <div className="daily-layout__date-mood">...</div>
  <button className="daily-page-refresh-button">...</button>
</div>
```

Story 58.8 remplace ce bloc par :
```tsx
// Story 58.8 (final)
<DailyPageHeader date={prediction.meta.date_local} tone={prediction.summary.overall_tone} lang={lang} />
<div className="daily-layout__refresh-row">
  <button className="daily-page-refresh-button" ...>
    <RefreshCw size={15} />
  </button>
</div>
```

Les classes `.daily-layout__date-mood`, `.daily-layout__mood-badge`, `.daily-layout__date` définies en story 58.7 deviennent **inutiles** et peuvent être supprimées de `DailyHoroscopePage.css`.

### Imports et path aliases

```ts
// Dans DailyPageHeader.tsx
import { getToneLabel } from '../../utils/predictionI18n'
import { getLocale } from '../../utils/locale'
import type { Lang } from '../../i18n/predictions'

// Dans DailyHoroscopePage.tsx (ajout)
import { DailyPageHeader } from '../components/prediction/DailyPageHeader'
```

### Accessibilité

- `<header>` avec classe CSS (pas d'attribut `role` redondant — `header` est un landmark implicite)
- `DayStateBadge` : `role="status"` + `aria-label="Tonalité du jour : Équilibrée"`
- `daily-page-header__ambient-glow` : `aria-hidden="true"` sur le parent `.daily-page-header__decoration`
- `header-date` : balise `<h1>` — vérifier qu'il n'existe pas déjà un `<h1>` dans la page (`TodayHeader` utilise `<h1 className="today-header__title">` — conflit potentiel à résoudre en changeant `header-date` en `<div>` ou en retirant le `<h1>` du `TodayHeader` sur cette page). **Recommandation** : utiliser `<h2 className="header-date">` pour éviter le conflit de hiérarchie si `TodayHeader` reste présent.

### Tests existants à ne pas casser

`DailyHoroscopePage.test.tsx` (story 58.6) vérifie l'absence de doublons avatar / toggle dans `.today-page`. `DailyPageHeader` ne contient ni avatar, ni toggle → aucun risque de régression.

### Architecture des fichiers

| Action | Fichier |
|---|---|
| Créer | `frontend/src/components/prediction/DailyPageHeader.tsx` |
| Créer | `frontend/src/components/prediction/DailyPageHeader.css` |
| Créer | `frontend/src/components/prediction/DayStateBadge.tsx` |
| Créer | `frontend/src/components/prediction/DayStateBadge.css` |
| Modifier | `frontend/src/pages/DailyHoroscopePage.tsx` |
| Modifier | `frontend/src/pages/DailyHoroscopePage.css` |
| Modifier | `frontend/src/utils/predictionI18n.ts` |

### Project Structure Notes

- Composants prédiction : `frontend/src/components/prediction/`
- Page : `frontend/src/pages/DailyHoroscopePage.tsx`
- Design tokens : `frontend/src/styles/design-tokens.css`
- Glass system : `frontend/src/styles/glass.css`
- Utils i18n prédiction : `frontend/src/utils/predictionI18n.ts`
- Locale : `frontend/src/utils/locale.ts`

### References

- Story 58.7 (layout parent) : `_bmad-output/implementation-artifacts/58-7-refonte-layout-page-horoscope-quotidien.md`
- Story 58.6 (app shell + QA) : `_bmad-output/implementation-artifacts/58-6-integration-applayout-et-qa.md`
- Design tokens : `frontend/src/styles/design-tokens.css`
- Glass system : `frontend/src/styles/glass.css`
- predictionI18n (utils) : `frontend/src/utils/predictionI18n.ts`
- i18n predictions : `frontend/src/i18n/predictions.ts`
- Tone labels mapping : `frontend/src/i18n/predictions.ts` lignes 42–51
- Tone colors mapping : `frontend/src/utils/predictionI18n.ts` lignes 37–47
- DailyHoroscopePage : `frontend/src/pages/DailyHoroscopePage.tsx`
- DayPredictionCard (pour pattern de référence) : `frontend/src/components/prediction/DayPredictionCard.tsx`
- TodayHeader : `frontend/src/components/TodayHeader.tsx`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
