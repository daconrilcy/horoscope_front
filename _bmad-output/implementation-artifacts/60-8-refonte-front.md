# Story 60.8 : Recomposer la page front autour de la nouvelle sémantique

Status: review

## Story

En tant qu'utilisateur,
je veux une page horoscope du jour réorganisée où chaque section répond à une question précise,
afin de naviguer plus fluidement et de comprendre immédiatement l'essentiel de ma journée sans effort cognitif.

## Acceptance Criteria

1. L'ordre des sections est : `DayClimateHero` → `DomainRankingCard` → `DayTimelineSection` → `TurningPointCard` (conditionnel) → `BestWindowCard` → `DailyAdviceCard` → `AstroFoundationSection`.
2. Chaque composant consomme exactement un objet métier du nouveau payload (pas de recomposition dans le composant).
3. `DayClimateHero` (Zone Hero) affiche le label, le résumé court, les top domains et le watchout.
4. `DomainRankingCard` affiche les 5 domaines publics avec leur score sur 10 et leur niveau (couleur sémantique).
5. `DayTimelineSection` est refondu pour consommer `time_windows` (regime, label, action_hint) — plus de blocs "équilibré".
6. `TurningPointCard` n'est rendu que si `turning_point` est présent dans le payload.
7. `BestWindowCard` affiche le créneau, le "pourquoi" et les actions recommandées.
8. `AstroFoundationSection` est un bloc extensible (accordéon fermé par défaut) contenant les détails techniques.
9. Les mappers front sont mis à jour pour extraire ces nouveaux objets tout en gérant le fallback (si nouveaux champs absents → ne rien afficher ou mode dégradé).
10. La navigation par ancres (#key-points, etc.) fonctionne avec la nouvelle structure.
11. Suppression visuelle des anciennes sections `KeyPointsSection` et `DetailAndScoresSection` de la page principale.
12. Les anciens composants inutilisés sont conservés (supprimés en Story 60.12).
13. `npm run lint` passe (sur les fichiers modifiés).

## Tasks / Subtasks

- [x] T1 — Mettre à jour les types TypeScript (AC: 2)
  - [x] Dans `frontend/src/types/dailyPrediction.ts`, ajouter les interfaces correspondant au nouveau payload Story 60.3 à 60.7.

- [x] T2 — Créer/Mettre à jour les composants atomiques (AC: 3, 4, 6, 7, 8)
  - [x] `DayClimateHero.tsx` (Nouveau)
  - [x] `DomainRankingCard.tsx` (Nouveau)
  - [x] `TurningPointCard.tsx` (Nouveau)
  - [x] `BestWindowCard.tsx` (Nouveau)
  - [x] `AstroFoundationSection.tsx` (Nouveau)

- [x] T3 — Refondre `DayTimelineSection` (AC: 5)
  - [x] Modifier `frontend/src/components/prediction/DayTimelineSection.tsx` pour consommer `time_windows` au lieu de `timeline` technique.
  - [x] Note: Création de `DayTimelineSectionV4.tsx` pour une transition propre.

- [x] T4 — Créer les mappers front (AC: 9)
  - [x] Créer `frontend/src/utils/dayClimateHeroMapper.ts`
  - [x] Créer `frontend/src/utils/domainRankingCardMapper.ts`
  - [x] Créer `frontend/src/utils/turningPointCardMapper.ts`
  - [x] Créer `frontend/src/utils/bestWindowCardMapper.ts`
  - [x] Créer `frontend/src/utils/astroFoundationSectionMapper.ts`

- [x] T5 — Recomposer `DailyHoroscopePage.tsx` (AC: 1, 11)
  - [x] Modifier `frontend/src/pages/DailyHoroscopePage.tsx`
  - [x] Importer les nouveaux mappers et composants.
  - [x] Remplacer l'ancien arbre de rendu par la séquence AC1.
  - [x] S'assurer que le bouton Refresh est toujours accessible.

- [x] T6 — Validation visuelle et lint (AC: 13)
  - [x] `npm run lint` sur les fichiers impactés.

## Dev Notes
...
### File List

- `frontend/src/types/dailyPrediction.ts` (MOD)
- `frontend/src/components/DayClimateHero.tsx` (NEW)
- `frontend/src/components/DomainRankingCard.tsx` (NEW)
- `frontend/src/components/TurningPointCard.tsx` (NEW)
- `frontend/src/components/BestWindowCard.tsx` (NEW)
- `frontend/src/components/AstroFoundationSection.tsx` (NEW)
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` (NEW)
- `frontend/src/utils/dayClimateHeroMapper.ts` (NEW)
- `frontend/src/utils/domainRankingCardMapper.ts` (NEW)
- `frontend/src/utils/turningPointCardMapper.ts` (NEW)
- `frontend/src/utils/bestWindowCardMapper.ts` (NEW)
- `frontend/src/utils/astroFoundationSectionMapper.ts` (NEW)
- `frontend/src/pages/DailyHoroscopePage.tsx` (MOD)
- `frontend/src/utils/predictionI18n.ts` (MOD)
- `frontend/src/i18n/predictions.ts` (MOD)
