# Story 60.12 : Cleanup et suppression des duplications legacy

Status: ready-for-dev

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

- [ ] T1 — Audit du code V3 résiduel (AC: 1, 2)
  - [ ] T1.1 Grep toutes les utilisations de `HeroSummaryCard` dans le codebase front
  - [ ] T1.2 Grep toutes les utilisations de `KeyPointsSection`, `FocusMomentCard`, `DetailAndScoresSection`
  - [ ] T1.3 Grep toutes les utilisations de `heroSummaryCardMapper`, `keyPointsSectionMapper`
  - [ ] T1.4 Si aucune utilisation → marquer pour suppression
  - [ ] T1.5 Si encore utilisé quelque part → NE PAS supprimer, noter dans Completion Notes

- [ ] T2 — Supprimer composants front orphelins (AC: 1)
  - [ ] T2.1 Si `HeroSummaryCard.tsx` non utilisé → supprimer
  - [ ] T2.2 Si `KeyPointsSection.tsx` non utilisé → supprimer
  - [ ] T2.3 Si `FocusMomentCard.tsx` non utilisé → supprimer
  - [ ] T2.4 Si `DetailAndScoresSection.tsx` non utilisé → supprimer
  - [ ] T2.5 Si `DailyDomainsCard.tsx` remplacé par `DomainRankingCard` → supprimer

- [ ] T3 — Supprimer mappers orphelins (AC: 2)
  - [ ] T3.1 Si `heroSummaryCardMapper.ts` non utilisé → supprimer
  - [ ] T3.2 Si `keyPointsSectionMapper.ts` non utilisé → supprimer
  - [ ] T3.3 Si `dailyDomainsCardMapper.ts` non utilisé → supprimer

- [ ] T4 — Supprimer le fallback V3 dans la page (AC: 3)
  - [ ] T4.1 Dans `DailyHoroscopePage.tsx`, supprimer la condition `isV4 / !isV4`
  - [ ] T4.2 Supprimer l'import et l'utilisation de `HeroSummaryCard`, `KeyPointsSection`, etc.
  - [ ] T4.3 Garder uniquement les composants V4

- [ ] T5 — Nettoyer le payload backend (AC: 4)
  - [ ] T5.1 Décision à documenter : supprimer ou conserver `summary.best_window` (maintenant dans `best_window`)
  - [ ] T5.2 Décision à documenter : supprimer ou conserver `summary.main_turning_point` (maintenant dans `turning_point`)
  - [ ] T5.3 Si décision de suppression prise → retirer les champs de `DailyPredictionSummary` et du `PublicSummaryPolicy`
  - [ ] T5.4 Si décision de conservation → laisser et noter comme "deprecated, to remove in Epic 61"

- [ ] T6 — Supprimer le code `payload_version` fallback (AC: 3)
  - [ ] T6.1 Si V4 est le seul mode → `payload_version` peut rester dans meta (pour observabilité) mais le code conditionnel front peut être supprimé

- [ ] T7 — Vérification finale (AC: 5, 6, 7)
  - [ ] T7.1 Grep `HeroSummaryCard`, `KeyPointsSection`, `FocusMomentCard`, `DetailAndScoresSection` → 0 résultats
  - [ ] T7.2 Grep imports de composants supprimés → 0 résultats
  - [ ] T7.3 `pytest backend/` → passe
  - [ ] T7.4 Tests frontend → passent
  - [ ] T7.5 `ruff check backend/` → passe
  - [ ] T7.6 Naviguer sur la page en dev → plus de redites visuelles

## Dev Notes

### Précautions avant suppression
**NE PAS supprimer un fichier sans avoir vérifié toutes ses utilisations.** Utiliser grep pour confirmer l'absence d'imports avant toute suppression. Cette story arrive en dernier (dépend de 60.10 et 60.11 validés).

### Candidats à la suppression (à vérifier)
- `frontend/src/components/HeroSummaryCard.tsx`
- `frontend/src/components/KeyPointsSection.tsx`
- `frontend/src/components/KeyPointCard.tsx` (sous-composant de KeyPointsSection)
- `frontend/src/components/FocusMomentCard.tsx`
- `frontend/src/components/DetailAndScoresSection.tsx`
- `frontend/src/components/DailyDomainsCard.tsx`
- `frontend/src/utils/heroSummaryCardMapper.ts`
- `frontend/src/utils/keyPointsSectionMapper.ts`
- `frontend/src/utils/dailyDomainsCardMapper.ts`

### Décision payload backend
Le nettoyage du payload (suppression `summary.best_window`, `summary.main_turning_point`) est optionnel dans cette story — il peut être différé à Epic 61 si des clients tierces consomment encore ces champs.

### Project Structure Notes
- Modification: `frontend/src/pages/DailyHoroscopePage.tsx` — suppression code fallback
- Suppression potentielle: multiples composants et mappers front
- Modification optionnelle: `backend/app/prediction/public_projection.py` + `predictions.py`

### References
- [Source: frontend/src/pages/DailyHoroscopePage.tsx] — page à nettoyer
- [Source: frontend/src/components/] — composants à auditer
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
