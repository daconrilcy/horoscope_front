# Story 58.10 : Refonte visuelle de la KeyPointsSection — grille de cartes avec jauge de force

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir les 3 points clés du jour sous forme d'une grille de cartes glassmorphisme — chacune avec une icône-pilule, un label court et une barre de progression représentant l'intensité du moment —,
afin de saisir d'un coup d'œil les temps forts de ma journée sans lire de texte long.

## Acceptance Criteria

1. [x] Un type `KeyPointItem` est créé à `frontend/src/types/keyPointsSection.ts` : `{ id: string; label: string; icon?: string; strength?: number; tone?: string }` où `strength` est compris entre 0 et 100.
2. [x] Un type `KeyPointsSectionModel` est créé dans le même fichier : `{ title: string; items: KeyPointItem[] }`.
3. [x] Un mapper `buildKeyPointsSectionModel(prediction: DailyPrediction, lang: Lang): KeyPointsSectionModel` est créé à `frontend/src/utils/keyPointsSectionMapper.ts`. Il produit jusqu'à 3 items à partir de `prediction.turning_points` (fallback : `buildDailyKeyMoments`). Pour chaque turning point : `label` = titre sémantique via `humanizeTurningPointSemantic`, `icon` = icône de la première catégorie impactée via `getCategoryMeta`, `strength` = `Math.round(moment.severity * 100)`, `tone` = `moment.change_type ?? undefined`.
4. [x] Un composant `SectionTitle` est créé à `frontend/src/components/prediction/SectionTitle.tsx`. Il accepte `{ title: string; id?: string }` et rend : `<header class="section-title"> > [div.section-title__dot] + [h3.section-title__text]{title} + [hr.section-title__line]`. Zéro style Tailwind.
5. [x] Un composant `KeyPointCard` (dans `frontend/src/components/prediction/KeyPointCard.tsx`) est **réécrit** avec la nouvelle structure : `<article class="key-point-card"> > [div.key-point-card__top > div.key-point-card__icon-pill{icon} + span.key-point-card__label{label}] + [div.key-point-card__gauge aria-hidden="true" > div.key-point-card__gauge-track > div.key-point-card__gauge-fill style="width:{strength}%"]`. Props : `{ item: KeyPointItem }`.
6. [x] Un composant `KeyPointsSection` est créé à `frontend/src/components/prediction/KeyPointsSection.tsx`. Il accepte `{ model: KeyPointsSectionModel }` et rend : `<section class="key-points-section" id="key-points"> > SectionTitle + [div.key-points-section__grid > {model.items.map(item => KeyPointCard)}]`. Rendu conditionnel : si `model.items.length === 0`, retourner `null`.
7. [x] **CSS `SectionTitle.css`** : `.section-title` en `display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-4)`. `.section-title__dot` : cercle `8px` plein `var(--color-primary)`, `border-radius: 50%`. `.section-title__text` : `font-size: 0.95rem; font-weight: 600; color: var(--color-text-primary); margin: 0`. `.section-title__line` : `flex: 1; height: 1px; border: none; background: linear-gradient(90deg, var(--color-primary), transparent); opacity: 0.3`.
8. [x] **CSS `KeyPointCard.css`** : `.key-point-card` glassmorphisme — `backdrop-filter: blur(14px)`, fond `rgba(255,255,255,0.38)` (light) / `rgba(255,255,255,0.06)` (dark via `prefers-color-scheme` ou classe `.dark`), `border-radius: 22px`, `border: 1px solid var(--glass-border)`, `padding: var(--space-4) var(--space-3)`, `box-shadow: var(--shadow-hero-card, 0 4px 20px rgba(44,28,100,0.15))`. `.key-point-card__icon-pill` : `font-size: 1.35rem; line-height: 1; background: rgba(134,108,208,0.12); border-radius: 12px; padding: 6px 8px`. `.key-point-card__label` : `font-size: 0.82rem; font-weight: 600; color: var(--color-hero-ink, var(--color-text-primary)); line-height: 1.3`. `.key-point-card__gauge-track` : `height: 6px; border-radius: 3px; background: rgba(134,108,208,0.15); overflow: hidden`. `.key-point-card__gauge-fill` : `height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--color-primary), var(--color-hero-ink-accent, var(--color-primary))); transition: width 0.4s ease`.
9. [x] **CSS `KeyPointsSection.css`** : sur `< 480px`, `.key-points-section__grid` utilise `display: flex; flex-wrap: nowrap; overflow-x: auto; scroll-snap-type: x mandatory; gap: var(--space-3); padding-bottom: var(--space-2)` avec chaque `.key-point-card` ayant `scroll-snap-align: start; min-width: 72vw; flex-shrink: 0`. Sur `≥ 480px` : `display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-3)`.
10. [x] `DailyHoroscopePage.tsx` remplace le bloc `<section className="daily-layout__section" id="key-points">` (zone 3 actuelle) par `<KeyPointsSection model={buildKeyPointsSectionModel(prediction, lang)} />`. L'import de `KeyPointCard` direct est retiré de la page (la section l'encapsule).
11. [x] `tsc --noEmit` passe sans erreur. Les tests `DailyHoroscopePage.test.tsx` continuent de passer. Le test global `npx vitest run` reste ≥ 1071 tests verts.
12. [x] Zéro style Tailwind. CSS custom vars du projet uniquement (`var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--glass)`, `var(--glass-border)`, `var(--shadow-hero-card)`).

## Tasks / Subtasks

- [x] T1 — Créer les types `KeyPointItem` et `KeyPointsSectionModel` (AC: 1, 2)
  - [x] T1.1 Créer `frontend/src/types/keyPointsSection.ts` avec `export type KeyPointItem` et `export type KeyPointsSectionModel`

- [x] T2 — Créer le mapper `buildKeyPointsSectionModel` (AC: 3)
  - [x] T2.1 Créer `frontend/src/utils/keyPointsSectionMapper.ts`
  - [x] T2.2 Importer `DailyPrediction` depuis `../types/dailyPrediction`, `Lang` depuis `../i18n/predictions`, `humanizeTurningPointSemantic` et `getCategoryMeta` depuis `../utils/predictionI18n`, `buildDailyKeyMoments` depuis `../utils/dailyAstrology`
  - [x] T2.3 Mapper les 3 premiers `turning_points` (fallback `buildDailyKeyMoments`) vers `KeyPointItem[]` : `id = moment.occurred_at_local`, `label = humanizeTurningPointSemantic(moment, lang).title || humanizeTurningPointSemantic(moment, lang).cause || '—'`, `icon = getCategoryMeta(firstCategory, lang).icon ?? '✦'`, `strength = Math.min(100, Math.round((moment.severity ?? 0.5) * 100))`, `tone = moment.change_type ?? undefined`
  - [x] T2.4 Titre de section via `getPredictionMessage('key_points_title', lang)`

- [x] T3 — Créer le composant `SectionTitle` (AC: 4, 7)
  - [x] T3.1 Créer `frontend/src/components/prediction/SectionTitle.tsx` (props `{ title: string; id?: string }`)
  - [x] T3.2 Créer `frontend/src/components/prediction/SectionTitle.css`

- [x] T4 — Réécrire `KeyPointCard` (AC: 5, 8)
  - [x] T4.1 Réécrire `frontend/src/components/prediction/KeyPointCard.tsx` — props `{ item: KeyPointItem }`, structure article + top-row + gauge
  - [x] T4.2 Réécrire `frontend/src/components/prediction/KeyPointCard.css` — glassmorphisme, icon-pill, gauge

- [x] T5 — Créer `KeyPointsSection` (AC: 6, 9)
  - [x] T5.1 Créer `frontend/src/components/prediction/KeyPointsSection.tsx`
  - [x] T5.2 Créer `frontend/src/components/prediction/KeyPointsSection.css`

- [x] T6 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 10)
  - [x] T6.1 Remplacer la zone 3 par `<KeyPointsSection model={buildKeyPointsSectionModel(prediction, lang)} />`
  - [x] T6.2 Retirer l'import direct de `KeyPointCard` depuis la page
  - [x] T6.3 Ajouter les imports de `KeyPointsSection` et `buildKeyPointsSectionMapper`

- [x] T7 — Validation et non-régression (AC: 11)
  - [x] T7.1 `tsc --noEmit` — 0 erreur TypeScript
  - [x] T7.2 `npx vitest run src/tests/DailyHoroscopePage.test.tsx` — tous les tests passent
  - [x] T7.3 `npx vitest run` global — ≥ 1071 tests verts

## Dev Notes

### Architecture

- Le projet utilise `verbatimModuleSyntax: true` → **tous les types s'importent avec `import type`**. Ne jamais écrire `import { KeyPointItem }` pour un type, toujours `import type { KeyPointItem }`.
- Pas de Tailwind. Les classes CSS doivent utiliser exclusivement `var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--glass)`, `var(--glass-border)`.
- Les tokens `--color-hero-ink` et `--color-hero-ink-accent` ont été ajoutés à `frontend/src/styles/design-tokens.css` en story 58-9. Ils sont disponibles.
- Le token `--shadow-hero-card` est également disponible dans `design-tokens.css`.

### Composants existants à préserver

- **`DailyHoroscopePage.tsx`** : ne toucher qu'à la zone 3 (KeyPointsSection), conserver toute la logique de data-fetching, normalisation `keyMoments`, `agendaSlots` et les autres zones.
- **`KeyPointCard.tsx`** : réécriture en place (les anciens props `moment: DailyPredictionTurningPoint, lang: Lang` sont remplacés par `item: KeyPointItem`). L'ancien composant n'est utilisé qu'à l'intérieur de la zone 3 de `DailyHoroscopePage.tsx` — la réécriture est donc sans risque de casse externe.

### Mapper

Le mapper `buildKeyPointsSectionModel` doit reproduire la même logique de fallback que `DailyHoroscopePage.tsx` :
- Si `prediction.turning_points.length > 0` → utiliser les `turning_points` normalisés (avec `severity`)
- Sinon → utiliser `buildDailyKeyMoments(...)` avec `severity` par défaut à `0.5`

Pour les `turning_points`, la page normalise déjà les moments dans `normalizedApiMoments` (calcul de `impacted_categories`, `change_type`, etc.). Le mapper reçoit le `prediction` brut et devra appliquer une logique simplifiée : utiliser directement `moment.impacted_categories ?? moment.next_categories ?? []` pour la catégorie principale.

### `SectionTitle` — intention de réutilisation

`SectionTitle` est conçu pour être réutilisable dans d'autres sections de la page horoscope (Timeline, Focus, Domains…) dans de futures stories. Ne pas le coupler à `KeyPointsSection`.

### Responsive

- Mobile `< 480px` : scroll horizontal avec snap. Chaque carte doit avoir `min-width: 72vw` pour que les cartes adjacentes soient partiellement visibles (affordance de scroll).
- ≥ 480px : grille 3 colonnes (pas 2). Les 3 cartes sont toujours visibles ensemble.

### Tests existants

Les tests `DailyHoroscopePage.test.tsx` ne testent pas directement le rendu des `KeyPointCard`. Ils vérifient l'absence de doublons d'avatar et de toggle. Ces guards ne sont pas affectés par cette story.

Si un test vérifie le texte d'une KeyPointCard (peu probable d'après l'historique), il faudra l'adapter au nouveau label.

### Project Structure Notes

- Nouveau fichier de types : `frontend/src/types/keyPointsSection.ts` (aux côtés de `dailyPrediction.ts`, `astroChart.ts`, etc.)
- Nouveau mapper : `frontend/src/utils/keyPointsSectionMapper.ts`
- Nouveaux composants : `frontend/src/components/prediction/SectionTitle.tsx/css`, `frontend/src/components/prediction/KeyPointsSection.tsx/css`
- Composants modifiés : `frontend/src/components/prediction/KeyPointCard.tsx/css`, `frontend/src/pages/DailyHoroscopePage.tsx`

### References

- Types existants : `frontend/src/types/dailyPrediction.ts` — `DailyPredictionTurningPoint.severity`, `DailyPredictionTurningPoint.change_type`, `DailyPredictionTurningPoint.impacted_categories`
- Utilitaires : `frontend/src/utils/predictionI18n.ts` — `humanizeTurningPointSemantic()`, `getCategoryMeta()`, `getPredictionMessage()`
- Utilitaires : `frontend/src/utils/dailyAstrology.ts` — `buildDailyKeyMoments()`
- Tokens design : `frontend/src/styles/design-tokens.css` — `--color-hero-ink`, `--color-hero-ink-accent`, `--shadow-hero-card`
- Page cible : `frontend/src/pages/DailyHoroscopePage.tsx` — zone 3, lignes 302–314
- CSS actuel KeyPointCard : `frontend/src/components/prediction/KeyPointCard.css`

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp (orchestrated by Gemini CLI)

### Debug Log References

- Created types and mapper for KeyPointsSection.
- Created SectionTitle component with CSS.
- Rewrote KeyPointCard component and CSS for new glassmorphism design.
- Created KeyPointsSection component and CSS with responsive horizontal scroll.
- Integrated KeyPointsSection into DailyHoroscopePage.
- Verified with tsc and vitest.
- Code review (claude-sonnet-4-6, 2026-03-17): fixed `item.strength ?? 0` guard in KeyPointCard, removed `as any` cast in mapper (typed `sourceMoments` as `DailyPredictionTurningPoint[]`).

### Completion Notes List

- [x] AC 1, 2: Types created.
- [x] AC 3: Mapper buildKeyPointsSectionModel implemented.
- [x] AC 4, 7: SectionTitle component and CSS created.
- [x] AC 5, 8: KeyPointCard rewritten.
- [x] AC 6, 9: KeyPointsSection created with responsive grid/scroll.
- [x] AC 10: Integrated in DailyHoroscopePage.
- [x] AC 11: tsc and vitest passed.
- [x] AC 12: No Tailwind used.

### File List

- `frontend/src/types/keyPointsSection.ts`
- `frontend/src/utils/keyPointsSectionMapper.ts`
- `frontend/src/components/prediction/SectionTitle.tsx`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/KeyPointCard.tsx`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/KeyPointsSection.tsx`
- `frontend/src/components/prediction/KeyPointsSection.css`
- `frontend/src/pages/DailyHoroscopePage.tsx`

