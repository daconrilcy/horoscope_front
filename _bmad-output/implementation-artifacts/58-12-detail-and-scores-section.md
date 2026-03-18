# Story 58.12 : Section DetailAndScoresSection — FocusMomentCard + DailyDomainsCard

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux voir sous la timeline une section à deux colonnes articulant le moment focal interprétatif (gauche) et les scores par domaine de la journée (droite),
afin d'avoir une lecture à la fois narrative et analytique de ma journée astrologique.

## Acceptance Criteria

1. [x] Le composant `DetailAndScoresSection` remplace le bloc inline `daily-layout__detail-scores` dans `DailyHoroscopePage.tsx` (Zone 5).
2. [x] `DetailAndScoresSection` utilise un grid asymétrique desktop (~1.6fr / 1fr) et un stack mobile vertical (FocusMomentCard d'abord).
3. [x] `FocusMomentCard` affiche : heure du créneau, titre interprétatif, tags de contexte (catégories dominantes), description/recommandation, CTA secondaire « Voir le détail ».
4. [x] `FocusMomentCard` affiche le slot 2h le plus significatif de la **période sélectionnée** dans `DayTimelineSection` ; si aucune période n'est sélectionnée, elle affiche le slot courant ou le meilleur slot de la journée.
5. [x] `DailyDomainsCard` affiche le titre « Domaines du jour », les 3 domaines principaux (icône + label + score + barre), les domaines secondaires (icône + label + mini-barre), et un CTA primaire violet.
6. [x] `DailyDomainsCard` se base sur les **scores de la journée complète** (`prediction.categories`), indépendamment de la période sélectionnée.
7. [x] Un décor abstrait radial mauve est présent en bas-droite de `FocusMomentCard` (pseudo-élément, purement décoratif).
8. [x] Les deux cartes partagent le même langage glassmorphism premium cohérent avec `PeriodCard` et `agenda-slot` existants.
9. [x] `tsc --noEmit` passe sans erreur.
10. [x] Les tests Vitest existants (≥ 1071) continuent de passer.

## Tasks / Subtasks

- [x] T1 — Créer les types TypeScript (AC: 3, 5)
  - [x] T1.1 Créer `frontend/src/types/detailScores.ts` avec `FocusMomentTag`, `FocusMomentCardModel`, `DailyDomainScore`, `DailyDomainsCardModel`

- [x] T2 — Créer les mappers (AC: 4, 6)
  - [x] T2.1 Créer `frontend/src/utils/focusMomentCardMapper.ts` : `buildFocusMomentCardModel(selectedPeriodKey, agendaSlots, prediction, lang)`
  - [x] T2.2 Créer `frontend/src/utils/dailyDomainsCardMapper.ts` : `buildDailyDomainsCardModel(categories, lang)`

- [x] T3 — Créer `FocusMomentCard` (AC: 3, 7, 8)
  - [x] T3.1 Créer `frontend/src/components/prediction/FocusMomentCard.tsx`
  - [x] T3.2 Créer `frontend/src/components/prediction/FocusMomentCard.css`

- [x] T4 — Créer `DailyDomainsCard` (AC: 5, 8)
  - [x] T4.1 Créer `frontend/src/components/prediction/DailyDomainsCard.tsx`
  - [x] T4.2 Créer `frontend/src/components/prediction/DailyDomainsCard.css`

- [x] T5 — Créer `DetailAndScoresSection` (AC: 1, 2)
  - [x] T5.1 Créer `frontend/src/components/prediction/DetailAndScoresSection.tsx`
  - [x] T5.2 Créer `frontend/src/components/prediction/DetailAndScoresSection.css`

- [x] T6 — Intégrer dans `DailyHoroscopePage.tsx` (AC: 1, 4)
  - [x] T6.1 Remonter `selectedPeriod` depuis `DayTimelineSection` via callback prop ou lift state
  - [x] T6.2 Remplacer le bloc `daily-layout__detail-scores` inline par `<DetailAndScoresSection ... />`
  - [x] T6.3 Ajouter les clés i18n manquantes dans `frontend/src/i18n/predictions.ts` si nécessaire

- [x] T7 — Validation (AC: 9, 10)
  - [x] T7.1 `tsc --noEmit` — 0 erreur
  - [x] T7.2 `npx vitest run` — ≥ 1071 tests verts

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### File List

- `frontend/src/types/detailScores.ts`
- `frontend/src/utils/focusMomentCardMapper.ts`
- `frontend/src/utils/dailyDomainsCardMapper.ts`
- `frontend/src/components/prediction/DetailAndScoresSection.tsx`
- `frontend/src/components/prediction/DetailAndScoresSection.css`
- `frontend/src/components/prediction/FocusMomentCard.tsx`
- `frontend/src/components/prediction/FocusMomentCard.css`
- `frontend/src/components/prediction/DailyDomainsCard.tsx`
- `frontend/src/components/prediction/DailyDomainsCard.css`
- `frontend/src/components/prediction/DayTimelineSection.tsx`
- `frontend/src/components/prediction/DayAgenda.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
