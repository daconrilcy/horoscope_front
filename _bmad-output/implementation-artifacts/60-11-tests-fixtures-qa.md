# Story 60.11 : Couverture de tests, fixtures et QA

Status: ready-for-dev

## Story

En tant que développeur,
je veux une couverture de tests complète sur les nouveaux contrats backend et frontend,
afin d'éviter les incohérences sémantiques et de pouvoir refactorer en confiance.

## Acceptance Criteria

1. Tests unitaires backend couvrent : mapping domaines, projection score_10, levels, ranks, climate labels, regime labels, turning point selection, best window selection.
2. Tests d'intégration backend vérifient le payload complet V4 sur 4 scénarios : journée plate, journée très polarisée, journée avec fort turning point, journée avec peu d'events.
3. Fixtures front (`frontend/src/tests/fixtures/`) sont mises à jour avec des payloads V4 complets pour chaque scénario.
4. Tests unitaires front pour chaque nouveau composant : DayClimateHero, DomainRankingCard, DayTimelineSection (refactoré), TurningPointCard, BestWindowCard, AstroFoundationSection.
5. Test de non-régression : le payload V3 (sans nouveaux champs) ne cause pas d'erreur de rendu.
6. Tests de seuils : tous les cas limites des seuils (score_10=9.0, score_10=7.5, etc.) sont testés.
7. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Tests unitaires backend (AC: 1, 6)
  - [ ] T1.1 Créer `backend/app/tests/unit/prediction/test_public_domain_taxonomy.py` :
    - Test : tous les 12 codes internes ont un mapping
    - Test : les 5 domaines publics sont définis
    - Test : `aggregate_public_domain_score` avec scores connus
    - Test : `DISPLAY_ORDER` contient exactement 5 items
  - [ ] T1.2 Créer `backend/app/tests/unit/prediction/test_public_score_mapper.py` :
    - Test seuils : to_level(9.0)="très_favorable", to_level(4.4)="exigeant"
    - Test : to_level(7.5)="favorable" (frontière)
    - Test : to_level(6.0)="stable" (frontière)
    - Test : to_level(4.5)="mitigé" (frontière)
    - Test : rank_domains tri décroissant
    - Test : to_score_10 arrondi 1 décimale
  - [ ] T1.3 Créer `backend/app/tests/unit/prediction/test_public_label_catalog.py` :
    - Test : "équilibré" absent de tous les dicts
    - Test : chaque régime a un `action_hint`
    - Test : chaque `change_type` a un `title` fallback
    - Test : chaque domaine public a un `why` template

- [ ] T2 — Tests d'intégration backend — 4 scénarios (AC: 2)
  - [ ] T2.1 Lire `backend/app/tests/integration/test_daily_prediction_api.py` pour comprendre la structure
  - [ ] T2.2 **Scénario 1 — Journée plate (flat_day=True)** :
    - Vérifier `day_climate.intensity < 4.0`
    - `turning_point == null`
    - `domain_ranking` avec tous niveaux "stable" ou "mitigé"
  - [ ] T2.3 **Scénario 2 — Journée très polarisée** :
    - Un domaine avec `score_10 >= 8.5` ET un domaine avec `score_10 <= 3.5`
    - `day_climate.watchout` non null
    - `best_window` présent
  - [ ] T2.4 **Scénario 3 — Fort turning point** :
    - `turning_point` non null avec `severity >= 0.5`
    - `turning_point.do` et `turning_point.avoid` non vides
    - `time_windows` contient un bloc avec `regime="pivot"`
  - [ ] T2.5 **Scénario 4 — Peu d'events** :
    - `astro_foundation.key_movements` 0–2 items (ou `astro_foundation = null`)
    - `decision_windows` vide ou peu peuplé
    - Pas de régression sur `summary`, `categories`, `timeline`

- [ ] T3 — Fixtures front V4 (AC: 3)
  - [ ] T3.1 Localiser `frontend/src/tests/` (ou `frontend/src/__mocks__/`)
  - [ ] T3.2 Créer `frontend/src/tests/fixtures/dailyPredictionV4Flat.json` — journée plate
  - [ ] T3.3 Créer `frontend/src/tests/fixtures/dailyPredictionV4Polarized.json` — journée polarisée
  - [ ] T3.4 Créer `frontend/src/tests/fixtures/dailyPredictionV4TurningPoint.json` — fort turning point
  - [ ] T3.5 Créer `frontend/src/tests/fixtures/dailyPredictionV4LowEvents.json` — peu d'events
  - [ ] T3.6 Chaque fixture inclut : `payload_version: "v4"`, `day_climate`, `domain_ranking`, `time_windows`, `turning_point` (null ou non), `best_window`, `astro_foundation` (null ou non)

- [ ] T4 — Tests unitaires front — nouveaux composants (AC: 4)
  - [ ] T4.1 Créer `frontend/src/tests/DayClimateHero.test.tsx` :
    - Render avec tone="positive" → titre coloré success
    - Render avec watchout=null → pas de badge watchout
    - Render avec top_domains=["pro_ambition"] → chip visible
  - [ ] T4.2 Créer `frontend/src/tests/DomainRankingCard.test.tsx` :
    - Render avec 5 domaines → 5 lignes
    - Domaine rank=1 en premier
    - Badge level="très_favorable" → couleur success
    - Pas de note /20 visible
  - [ ] T4.3 Créer `frontend/src/tests/TurningPointCard.test.tsx` :
    - turningPoint=null → aucun rendu
    - turningPoint valide → titre, do, avoid visibles
    - change_type="emergence" → badge correspondant
  - [ ] T4.4 Créer `frontend/src/tests/BestWindowCard.test.tsx` :
    - bestWindow=null → aucun rendu
    - bestWindow valide → time_range, label, why, actions visibles
  - [ ] T4.5 Créer `frontend/src/tests/AstroFoundationSection.test.tsx` :
    - astro_foundation=null → aucun rendu
    - key_movements avec 3 items → 3 lignes
    - Contenu non vide
  - [ ] T4.6 Adapter `DayTimelineSection.test.tsx` pour `time_windows` (AC: 4)

- [ ] T5 — Test de non-régression V3 (AC: 5)
  - [ ] T5.1 Créer `frontend/src/tests/DailyHoroscopePage.v3compat.test.tsx`
  - [ ] T5.2 Charger fixture V3 (sans nouveaux champs) → pas d'erreur de rendu
  - [ ] T5.3 Vérifier que les anciens composants (HeroSummaryCard en fallback) s'affichent

## Dev Notes

### Infrastructure de tests backend existante
- `backend/app/tests/unit/prediction/` — répertoire tests unitaires prediction
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py` — tests projection existants
- `backend/app/tests/integration/test_daily_prediction_api.py` — tests API intégration
- Pattern de mock : mocker `DailyPredictionService.get_or_compute()` ou utiliser fixtures JSON

### Infrastructure de tests frontend
- `frontend/src/tests/` — vérifier l'outil de test utilisé (Vitest ou Jest)
- `frontend/src/tests/dailyPredictionApi.test.ts` — test API existant à consulter
- Pattern : render + assertion sur DOM ou snapshot

### Scénario flat day
Un jour "plat" signifie `flat_day=True` dans `summary`. Côté moteur : variance faible entre catégories, `low_score_variance=True`, pas de turning point.

### Scénario polarisé
Minimum 1 catégorie publique avec score_10 ≥ 8.5 ET minimum 1 avec score_10 ≤ 3.5. Cela force un `watchout` dans `day_climate`.

### Scénario fort turning point
`V3TurningPoint` avec `severity >= 0.5` et `confidence >= 0.6`. Un bloc temporel avec `window_type="pivot"`.

### Project Structure Notes
```
backend/app/tests/unit/prediction/
  test_public_domain_taxonomy.py   ← nouveau
  test_public_score_mapper.py      ← nouveau
  test_public_label_catalog.py     ← nouveau

backend/app/tests/integration/
  test_daily_prediction_api.py     ← adapter/compléter

frontend/src/tests/
  fixtures/
    dailyPredictionV4Flat.json     ← nouveau
    dailyPredictionV4Polarized.json
    dailyPredictionV4TurningPoint.json
    dailyPredictionV4LowEvents.json
  DayClimateHero.test.tsx          ← nouveau
  DomainRankingCard.test.tsx       ← nouveau
  TurningPointCard.test.tsx        ← nouveau
  BestWindowCard.test.tsx          ← nouveau
  AstroFoundationSection.test.tsx  ← nouveau
  DailyHoroscopePage.v3compat.test.tsx ← nouveau
```

### References
- [Source: backend/app/tests/integration/test_daily_prediction_api.py] — pattern tests intégration
- [Source: backend/app/tests/unit/prediction/test_public_projection_evidence.py] — tests projection
- [Source: frontend/src/tests/dailyPredictionApi.test.ts] — pattern tests front
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
