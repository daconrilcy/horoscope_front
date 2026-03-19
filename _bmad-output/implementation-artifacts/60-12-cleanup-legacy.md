# Story 60.12 : Cleanup et suppression des duplications legacy

Status: review

## Story

En tant que développeur,
je veux supprimer le code legacy V3 qui n'est plus utilisé après la migration V4,
afin que la page finale soit propre, sans doublon de composants et sans champs API obsolètes.

## Acceptance Criteria

1. Les composants front V3 non réutilisés sont supprimés : `HeroSummaryCard.tsx`, `KeyPointsSection.tsx` (si remplacés par V4).
2. Les mappers V3 orphelins sont supprimés : `heroSummaryCardMapper.ts`, `keyPointsSectionMapper.ts` (si plus utilisés).
3. Le code de fallback V3 dans `DailyHoroscopePage.tsx` est supprimé (le front consomme uniquement V4).
4. Le payload `DailyPredictionResponse` peut être nettoyé des champs redondants si décision prise (ex: `summary.best_window` si remplacé par `best_window`).
5. La page finale ne contient plus trois redites du même signal.
6. Aucune importation de composant supprimé ne subsiste dans le codebase.
7. `pytest backend/` passe. Tests frontend passent. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Audit du code V3 résiduel (AC: 1, 2)
  - [x] Audit effectué via grep.

- [x] T2 — Supprimer composants front orphelins (AC: 1)
  - [x] Supprimés : `HeroSummaryCard`, `KeyPointsSection`, `KeyPointCard`, `FocusMomentCard`, `DetailAndScoresSection`, `DailyDomainsCard`.

- [x] T3 — Supprimer mappers orphelins (AC: 2)
  - [x] Supprimés : `heroSummaryCardMapper`, `keyPointsSectionMapper`, `dailyDomainsCardMapper`, `focusMomentCardMapper`.

- [x] T4 — Supprimer le fallback V3 dans la page (AC: 3)
  - [x] Nettoyage de `DailyHoroscopePage.tsx`.

- [x] T5 — Nettoyer le payload backend (AC: 4)
  - [x] Décision : conservation des champs pour Epic 61 (rétrocompatibilité étendue).

- [x] T6 — Supprimer le code `payload_version` fallback (AC: 3)
  - [x] Code conditionnel supprimé dans le front.

- [x] T7 — Vérification finale (AC: 5, 6, 7)
  - [x] Vérifié.

## Dev Notes
...
### File List

- `frontend/src/components/prediction/HeroSummaryCard.tsx` (DEL)
- `frontend/src/components/prediction/HeroSummaryCard.css` (DEL)
- `frontend/src/components/prediction/KeyPointsSection.tsx` (DEL)
- `frontend/src/components/prediction/KeyPointsSection.css` (DEL)
- `frontend/src/components/prediction/KeyPointCard.tsx` (DEL)
- `frontend/src/components/prediction/FocusMomentCard.tsx` (DEL)
- `frontend/src/components/prediction/FocusMomentCard.css` (DEL)
- `frontend/src/components/prediction/DetailAndScoresSection.tsx` (DEL)
- `frontend/src/components/prediction/DetailAndScoresSection.css` (DEL)
- `frontend/src/components/prediction/DailyDomainsCard.tsx` (DEL)
- `frontend/src/components/prediction/DailyDomainsCard.css` (DEL)
- `frontend/src/utils/heroSummaryCardMapper.ts` (DEL)
- `frontend/src/utils/keyPointsSectionMapper.ts` (DEL)
- `frontend/src/utils/dailyDomainsCardMapper.ts` (DEL)
- `frontend/src/utils/focusMomentCardMapper.ts` (DEL)
- `frontend/src/types/keyPointsSection.ts` (DEL)
- `frontend/src/types/detailScores.ts` (DEL)
- `frontend/src/pages/DailyHoroscopePage.tsx` (MOD)
