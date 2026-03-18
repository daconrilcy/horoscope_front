# Story 58.13 : DailyAdviceCard — Conseil du jour

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir en bas de la page un encart "Conseil du jour" présentant un conseil personnalisé,
afin d'avoir une recommandation actionnable pour orienter ma journée.

## Acceptance Criteria

1. [x] Le composant `DailyAdviceCard` est créé et intégré dans `DailyHoroscopePage.tsx` après `DetailAndScoresSection` (Zone 6), prenant toute la largeur de la zone centrale.
2. [x] Le fond, la bordure et l'ombre sont identiques à `PeriodCard` — même langage glassmorphism : `background: rgba(252, 250, 255, 0.58)`, `border: 2px solid rgba(200, 190, 240, 0.35)`, `box-shadow: 0 2px 12px rgba(134, 108, 208, 0.06)`, `backdrop-filter: blur(4px)`, `border-radius: 18px`. En dark mode : `background: var(--background-unselected-cell)`.
3. [x] Le composant affiche : icône `Lightbulb` (Lucide) dans un badge circulaire violet (`background: rgba(134, 108, 208, 0.15)`, `color: var(--primary)`), titre "Conseil du jour" en gras à côté du badge, texte du conseil (`model.advice`) + emphase (`model.emphasis`) en `<strong>` sur la ligne suivante.
4. [x] Le texte est fourni par `DailyAdviceCardModel { title: string; advice: string; emphasis: string }` — le composant ne hardcode aucun texte.
5. [x] Un mapper `buildDailyAdviceCardModel(prediction, lang)` retourne un modèle avec texte fixe placeholder (structuré pour recevoir ultérieurement un texte généré par LLM via `prediction.summary.llm_advice` ou champ équivalent).
6. [x] Le bouton "Optimiser ma journée" (`daily-domains-card__cta`) est supprimé : retrait du JSX `DailyDomainsCard.tsx`, du CSS `DailyDomainsCard.css` (section footer + cta), de `ctaLabel` dans `DailyDomainsCardModel` (`detailScores.ts`), et de `ctaLabel` dans `dailyDomainsCardMapper.ts`.
7. [x] `tsc --noEmit` passe sans erreur.
8. [x] Les tests Vitest existants (≥ 1071) continuent de passer.

## Tasks / Subtasks

- [x] T1 — Supprimer le CTA "Optimiser ma journée" (AC: 6)
  - [x] T1.1 Retirer `ctaLabel: string` de `DailyDomainsCardModel` dans `frontend/src/types/detailScores.ts`
  - [x] T1.2 Retirer `<footer>` + `<button>` du JSX de `DailyDomainsCard.tsx`
  - [x] T1.3 Retirer `.daily-domains-card__footer` et `.daily-domains-card__cta` de `DailyDomainsCard.css`
  - [x] T1.4 Retirer `ctaLabel: getPredictionMessage('optimize_day_cta', lang)` de `dailyDomainsCardMapper.ts`

- [x] T2 — Créer le type `DailyAdviceCardModel` (AC: 4)
  - [x] T2.1 Ajouter dans `frontend/src/types/detailScores.ts` :
    ```ts
    export interface DailyAdviceCardModel {
      title: string
      advice: string
      emphasis: string
    }
    ```

- [x] T3 — Créer le mapper (AC: 5)
  - [x] T3.1 Créer `frontend/src/utils/dailyAdviceCardMapper.ts` :
    ```ts
    import type { DailyPredictionResponse } from '../types/dailyPrediction'
    import type { Lang } from '../i18n/predictions'
    import type { DailyAdviceCardModel } from '../types/detailScores'
    import { getPredictionMessage } from './predictionI18n'

    export function buildDailyAdviceCardModel(
      _prediction: DailyPredictionResponse,
      lang: Lang
    ): DailyAdviceCardModel {
      // TODO: utiliser prediction.summary.llm_advice quand disponible
      return {
        title: getPredictionMessage('daily_advice_title', lang),
        advice: getPredictionMessage('daily_advice_placeholder', lang),
        emphasis: getPredictionMessage('daily_advice_emphasis_placeholder', lang),
      }
    }
    ```

- [x] T4 — Ajouter les clés i18n (AC: 3, 5)
  - [x] T4.1 Ajouter dans `frontend/src/i18n/predictions.ts` (section MESSAGES) :
    - `daily_advice_title` : `{ fr: 'Conseil du jour', en: 'Daily advice' }`
    - `daily_advice_placeholder` : `{ fr: 'Prenez le temps d'ajuster votre espace et d'organiser votre soirée.', en: 'Take time to adjust your space and organize your evening.' }`
    - `daily_advice_emphasis_placeholder` : `{ fr: 'Un apaisement profond vous attend.', en: 'A deep sense of calm awaits you.' }`

- [x] T5 — Créer `DailyAdviceCard` (AC: 1, 2, 3)
  - [x] T5.1 Créer `frontend/src/components/prediction/DailyAdviceCard.tsx`
  - [x] T5.2 Créer `frontend/src/components/prediction/DailyAdviceCard.css`

- [x] T6 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 1)
  - [x] T6.1 Importer `DailyAdviceCard` et `buildDailyAdviceCardModel`
  - [x] T6.2 Ajouter après `<DetailAndScoresSection ... />` :
    ```tsx
    {/* Zone 6 : DailyAdviceCard — Conseil du jour */}
    <DailyAdviceCard model={buildDailyAdviceCardModel(prediction, lang)} />
    ```
  - [x] T6.3 L'actuel `{/* Zone 6 : AdviceCard + CTA */}` (best_window block) devient Zone 7

- [x] T7 — Validation (AC: 7, 8)
  - [x] T7.1 `tsc --noEmit` — 0 erreur
  - [x] T7.2 `npx vitest run` — ≥ 1071 tests verts

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### File List

- `frontend/src/types/detailScores.ts`
- `frontend/src/utils/dailyAdviceCardMapper.ts`
- `frontend/src/components/prediction/DailyAdviceCard.tsx`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/prediction/DailyDomainsCard.tsx`
- `frontend/src/components/prediction/DailyDomainsCard.css`
- `frontend/src/utils/dailyDomainsCardMapper.ts`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/pages/DailyHoroscopePage.tsx`
