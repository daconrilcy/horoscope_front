# Story 60.8 : Recomposer la page front autour de la nouvelle sémantique

Status: ready-for-dev

## Story

En tant qu'utilisateur,
je veux une page horoscope du jour réorganisée où chaque section répond à une question précise,
afin de ne plus voir les mêmes informations répétées et de trouver immédiatement ce que je cherche.

## Acceptance Criteria

1. La page `DailyHoroscopePage.tsx` affiche les sections dans l'ordre : DayClimateHero → DomainRankingCard → DayTimelineSection → TurningPointCard (conditionnel) → BestWindowCard → DailyAdviceCard → AstroFoundationSection.
2. Chaque composant consomme exactement un objet métier du nouveau payload (pas de recomposition dans le composant).
3. `DayClimateHero` remplace `HeroSummaryCard` — consomme `day_climate` du payload.
4. `DomainRankingCard` remplace `DailyDomainsCard` — consomme `domain_ranking` (score_10, level, rank).
5. `DayTimelineSection` est refactoré pour consommer `time_windows` (regime, label, action_hint) — plus de blocs "équilibré".
6. `TurningPointCard` est créé — consomme `turning_point` (conditionnel : rendu seulement si `turning_point != null`).
7. `BestWindowCard` est créé — consomme `best_window`.
8. `AstroFoundationSection` est créé — consomme `astro_foundation` (conditionnel).
9. Aucun composant ne contient de logique de calcul ou de transformation métier (niveau, rang, etc.).
10. La page est mobile-first, sans Tailwind, utilise exclusivement les CSS variables du projet.
11. Les chips de domaines ne sont pas répétées dans plus d'une section.
12. Les composants existants non réutilisés sont gardés (suppression dans Story 60.12).

## Tasks / Subtasks

- [ ] T1 — Mise à jour des types TypeScript (AC: 2)
  - [ ] T1.1 Dans `frontend/src/types/dailyPrediction.ts`, ajouter :
    ```typescript
    interface DailyPredictionDayClimate {
      label: string; tone: string; intensity: number; stability: number;
      summary: string; top_domains: string[]; watchout: string | null;
      best_window_ref: string | null;
    }
    interface DailyPredictionPublicDomainScore {
      key: string; label: string; score_10: number; level: string; rank: number;
      signal_label: string | null; note_20_internal: number;
    }
    interface DailyPredictionTimeWindow {
      time_range: string; label: string; regime: string;
      top_domains: string[]; action_hint: string;
    }
    interface DailyPredictionTurningPointPublic {
      time: string; title: string; change_type: string;
      affected_domains: string[]; what_changes: string; do: string; avoid: string;
    }
    interface DailyPredictionBestWindow {
      time_range: string; label: string; why: string;
      recommended_actions: string[]; is_pivot?: boolean;
    }
    interface DailyPredictionAstroFoundation {
      headline: string; key_movements: AstroKeyMovement[];
      activated_houses: AstroActivatedHouse[];
      dominant_aspects: AstroDominantAspect[];
      interpretation_bridge: string;
    }
    ```
  - [ ] T1.2 Ajouter ces champs dans `DailyPredictionResponse`

- [ ] T2 — Créer `DayClimateHero.tsx` (AC: 3)
  - [ ] T2.1 Localisation: `frontend/src/components/DayClimateHero.tsx`
  - [ ] T2.2 Props: `{ climate: DailyPredictionDayClimate; lang: Lang }`
  - [ ] T2.3 Affiche : `label` (titre hero coloré par `tone`), `summary` (sous-titre), `top_domains` (max 2 chips), `best_window_ref` (si présent), `watchout` (si présent avec icône alerte)
  - [ ] T2.4 Couleurs tone : positive→`var(--success)`, negative→`var(--danger)`, mixed→`var(--primary)`, neutral→`var(--text-2)`
  - [ ] T2.5 Style: card glassmorphisme `var(--glass)`, `var(--glass-border)`

- [ ] T3 — Créer `DomainRankingCard.tsx` (AC: 4)
  - [ ] T3.1 Localisation: `frontend/src/components/DomainRankingCard.tsx`
  - [ ] T3.2 Props: `{ domains: DailyPredictionPublicDomainScore[]; lang: Lang }`
  - [ ] T3.3 Affiche liste ordonnée par `rank` : `label`, `score_10 / 10`, barre de progression, badge `level`
  - [ ] T3.4 Badge couleur `level` : très_favorable→`var(--success)`, favorable→vert clair, stable→`var(--text-2)`, mitigé→orange, exigeant→`var(--danger)`
  - [ ] T3.5 Pas de note sur 20 visible (seulement note /10)

- [ ] T4 — Refactorer `DayTimelineSection.tsx` (AC: 5)
  - [ ] T4.1 Lire `frontend/src/components/DayTimelineSection.tsx` (ou équivalent)
  - [ ] T4.2 Adapter pour consommer `time_windows: DailyPredictionTimeWindow[]`
  - [ ] T4.3 Afficher par carte : `time_range`, `label` (titre), `regime` (badge discret), `action_hint` (texte italic), `top_domains` (chips mini)
  - [ ] T4.4 Couleur carte par `regime` : progression/fluidité→teinte verte, prudence→teinte orange, pivot→teinte primaire, récupération→teinte grise

- [ ] T5 — Créer `TurningPointCard.tsx` (AC: 6)
  - [ ] T5.1 Localisation: `frontend/src/components/TurningPointCard.tsx`
  - [ ] T5.2 Props: `{ turningPoint: DailyPredictionTurningPointPublic | null; lang: Lang }`
  - [ ] T5.3 Si `turningPoint == null` → rendu null (composant invisible)
  - [ ] T5.4 Affiche : badge heure `time`, `title` (titre fort), `what_changes` (description), chips `affected_domains`, lignes "À faire" (`do`) et "À éviter" (`avoid`)
  - [ ] T5.5 Badge `change_type` : emergence→vert, recomposition→bleu, attenuation→gris

- [ ] T6 — Créer `BestWindowCard.tsx` (AC: 7)
  - [ ] T6.1 Localisation: `frontend/src/components/BestWindowCard.tsx`
  - [ ] T6.2 Props: `{ bestWindow: DailyPredictionBestWindow | null; lang: Lang }`
  - [ ] T6.3 Si null → rendu null
  - [ ] T6.4 Affiche : badge `time_range`, `label` (titre), `why` (pourquoi), liste `recommended_actions` (bullets)
  - [ ] T6.5 Si `is_pivot` → badge supplémentaire "Point charnière"

- [ ] T7 — Créer `AstroFoundationSection.tsx` (AC: 8)
  - [ ] T7.1 Localisation: `frontend/src/components/AstroFoundationSection.tsx`
  - [ ] T7.2 Props: `{ foundation: DailyPredictionAstroFoundation | null; lang: Lang }`
  - [ ] T7.3 Si null → rendu null
  - [ ] T7.4 Section accordéon ou expandable (masquée par défaut, titre "Fondements astrologiques")
  - [ ] T7.5 Affiche : `headline`, liste `key_movements`, liste `activated_houses`, liste `dominant_aspects`, `interpretation_bridge`

- [ ] T8 — Refactorer `DailyHoroscopePage.tsx` (AC: 1, 9, 11)
  - [ ] T8.1 Lire `frontend/src/pages/DailyHoroscopePage.tsx`
  - [ ] T8.2 Remplacer `HeroSummaryCard` par `DayClimateHero` (consomme `data.day_climate`)
  - [ ] T8.3 Remplacer `DetailAndScoresSection` par `DomainRankingCard` (consomme `data.domain_ranking`)
  - [ ] T8.4 Adapter `DayTimelineSection` pour consommer `data.time_windows`
  - [ ] T8.5 Ajouter `TurningPointCard` (conditionnel sur `data.turning_point`)
  - [ ] T8.6 Ajouter `BestWindowCard` (conditionnel sur `data.best_window`)
  - [ ] T8.7 Garder `DailyAdviceCard` (déjà refactoré en Story 58.13)
  - [ ] T8.8 Ajouter `AstroFoundationSection` (conditionnel sur `data.astro_foundation`)
  - [ ] T8.9 Supprimer `KeyPointsSection` du flux principal (redondant avec TurningPointCard)

- [ ] T9 — Créer les mappers (AC: 2)
  - [ ] T9.1 Créer `frontend/src/utils/dayClimateHeroMapper.ts`
  - [ ] T9.2 Créer `frontend/src/utils/domainRankingCardMapper.ts`
  - [ ] T9.3 Créer `frontend/src/utils/turningPointCardMapper.ts`
  - [ ] T9.4 Créer `frontend/src/utils/bestWindowCardMapper.ts`
  - [ ] T9.5 Créer `frontend/src/utils/astroFoundationSectionMapper.ts`
  - [ ] T9.6 Adapter `frontend/src/utils/dayTimelineSectionMapper.ts` pour `time_windows`

## Dev Notes

### Stack frontend
- React 19, TypeScript, Vite 7
- Pas de Tailwind — uniquement CSS variables custom
- Fichiers CSS variables: `frontend/src/index.css`, `frontend/src/App.css`, `frontend/src/styles/theme.css`
- CSS variables clés: `--bg-base`, `--text-1`, `--text-2`, `--line`, `--primary`, `--primary-strong`, `--danger`, `--success`, `--glass`, `--glass-border`, `--glass-2`

### Composants existants à NE PAS supprimer dans cette story
- `HeroSummaryCard.tsx` — conserver (suppression Story 60.12)
- `KeyPointsSection.tsx` — conserver
- `DailyDomainsCard.tsx` — conserver
- `FocusMomentCard.tsx` — conserver

### Mappers existants (pattern à suivre)
- `heroSummaryCardMapper.ts` — pattern mapper existant
- `keyPointsSectionMapper.ts`
- `dailyDomainsCardMapper.ts`
- `dayTimelineSectionMapper.ts`

### Backward compatibility
Les nouveaux champs `day_climate`, `domain_ranking`, `time_windows`, `turning_point`, `best_window`, `astro_foundation` peuvent être `null` / absents si le backend est en version antérieure → gérer les fallbacks dans les mappers.

### Page actuelle — composants utilisés
Source: `frontend/src/pages/DailyHoroscopePage.tsx`
- DailyPageHeader, HeroSummaryCard, KeyPointsSection, DayTimelineSection
- DetailAndScoresSection (contient FocusMomentCard + DailyDomainsCard)
- DailyAdviceCard

### Project Structure Notes
```
frontend/src/components/
  DayClimateHero.tsx          ← nouveau
  DomainRankingCard.tsx        ← nouveau
  TurningPointCard.tsx         ← nouveau
  BestWindowCard.tsx           ← nouveau
  AstroFoundationSection.tsx   ← nouveau
  DayTimelineSection.tsx       ← refactoré
  DailyAdviceCard.tsx          ← existant (Story 58.13)

frontend/src/utils/
  dayClimateHeroMapper.ts      ← nouveau
  domainRankingCardMapper.ts   ← nouveau
  turningPointCardMapper.ts    ← nouveau
  bestWindowCardMapper.ts      ← nouveau
  astroFoundationSectionMapper.ts ← nouveau
  dayTimelineSectionMapper.ts  ← adapté

frontend/src/types/dailyPrediction.ts ← mis à jour
frontend/src/pages/DailyHoroscopePage.tsx ← réorganisé
```

### References
- [Source: frontend/src/pages/DailyHoroscopePage.tsx] — page actuelle
- [Source: frontend/src/types/dailyPrediction.ts] — types TypeScript actuels
- [Source: frontend/src/utils/heroSummaryCardMapper.ts] — pattern mapper à suivre
- [Source: frontend/src/index.css] — CSS variables disponibles
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
