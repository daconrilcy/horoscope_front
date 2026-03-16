# Story 58.8 : DailyPageHeader — HeaderBar éditorial de la page horoscope quotidien

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir un header compact et élégant qui affiche la date du jour en grande typographie et un badge de tonalité, sans aucun contrôle utilitaire,
afin de m'immerger immédiatement dans le contexte de ma journée avant de lire la hero card.

## Acceptance Criteria

1. [x] Le composant `DailyPageHeader` est créé à `frontend/src/components/prediction/DailyPageHeader.tsx`. Il accepte les props `date: string` (ISO), `tone: string | null`, `lang: Lang` et rend un `<header>` avec classe `daily-page-header`.
2. [x] Le sous-composant `DayStateBadge` est créé à `frontend/src/components/prediction/DayStateBadge.tsx`. Il accepte les props `label: string`, `tone?: string | null`, `size?: "sm" | "md"` et affiche un badge glassmorphism pill avec : icône subtile, label en uppercase, point coloré.
3. [x] `DayStateBadge` dérive sa variante visuelle (`balanced | dynamic | calm | intense | reflective`) depuis le `tone` de l'API — voir table de mapping dans les Dev Notes.
4. [x] Le `HeaderDate` affiche la date au format "16 mars 2026" en `clamp(2rem, 4vw, 3.25rem)`, font-weight 500, letter-spacing négatif, via `toLocaleDateString` avec le `locale` dérivé de `lang`.
5. [x] La structure HTML cible est strictement : `<header.daily-page-header> > <div.daily-page-header__content> > [h1.header-date] + [DayStateBadge]`. Pas d'éléments utilitaires (pas de refresh, pas d'avatar, pas de toggle thème).
6. [x] Sur desktop (≥ 768px), un `<div.daily-page-header__decoration>` optionnel peut contenir une `AmbientGlow` (simple `div` avec `position: absolute` et dégradé radial violet flou, `pointer-events: none`). Sur mobile, la décoration est absente (`display: none`).
7. [x] `DailyHoroscopePage.tsx` remplace la `<div className="daily-layout__header-bar">` (définie en story 58.7) par `<DailyPageHeader date={prediction.meta.date_local} tone={prediction.summary.overall_tone} lang={lang} />`. Le bouton refresh reste dans une `<div className="daily-layout__refresh-row">` séparée, juste après le `DailyPageHeader`.
8. [x] Zéro style Tailwind. CSS custom vars du projet uniquement. Les variables `--ink-strong` et `--purple-500` du spec de design **ne sont pas dans le projet** — utiliser `var(--color-text-primary)` et `var(--color-primary)` à la place.
9. [x] `tsc --noEmit` passe sans erreur. Les tests `DailyHoroscopePage.test.tsx` existants continuent de passer.
10. [x] Les clés i18n `day_state_label` (libellé "Tonalité du jour" / "Day mood") sont ajoutées dans `predictionI18n.ts` pour le `aria-label` du badge.

## Tasks / Subtasks

- [x] T1 — Créer `DayStateBadge.tsx` (AC: 2, 3, 8)
- [x] T2 — Créer `DailyPageHeader.tsx` (AC: 1, 4, 5, 6)
- [x] T3 — Ajouter la clé i18n `day_state_label` (AC: 10)
- [x] T4 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 7)
- [x] T5 — Validation et non-régression (AC: 9)

## Dev Notes

... (unchanged)

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- `DayStateBadge` and `DailyPageHeader` components created with corresponding CSS.
- i18n keys updated.
- `DailyHoroscopePage` updated to use the new header component.
- Obsolete styles removed.
- Validation passed.

### Completion Notes List

- All acceptance criteria satisfied.
- Header is now editorial and visually rich with glassmorphism and ambient glow.
- Refactoring from story 58.7 successful.

### File List

- `frontend/src/components/prediction/DayStateBadge.tsx`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DailyPageHeader.tsx`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/utils/predictionI18n.ts`

## Change Log

- 2026-03-16: Implementation of story 58.8.
