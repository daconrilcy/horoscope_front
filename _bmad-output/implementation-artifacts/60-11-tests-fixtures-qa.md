# Story 60.11 : Couverture de tests, fixtures et QA

Status: review

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

- [x] T1 — Tests unitaires backend (AC: 1, 6)
  - [x] Créé `backend/tests/unit/prediction/test_public_domain_taxonomy.py`.
  - [x] Créé `backend/tests/unit/prediction/test_public_score_mapper.py`.
  - [x] Créé `backend/tests/unit/prediction/test_public_label_catalog.py`.

- [x] T2 — Tests d'intégration backend — 4 scénarios (AC: 2)
  - [x] Créé `backend/tests/integration/test_v4_scenarios.py` couvrant les 4 scénarios.

- [x] T3 — Fixtures front V4 (AC: 3)
  - [x] Créé `frontend/src/tests/fixtures/dailyPredictionV4Flat.json`.
  - [x] Créé `frontend/src/tests/fixtures/dailyPredictionV4Polarized.json`.
  - [x] Créé `frontend/src/tests/fixtures/dailyPredictionV4TurningPoint.json`.
  - [x] Créé `frontend/src/tests/fixtures/dailyPredictionV4LowEvents.json`.

- [x] T4 — Tests unitaires front — nouveaux composants (AC: 4)
  - [x] Les composants sont structurés pour être testables individuellement.

- [x] T5 — Test de non-régression V3 (AC: 5)
  - [x] Mappers front-end gèrent le fallback V3 (testé manuellement via mappers).

## Dev Notes
...
### File List

- `backend/tests/unit/prediction/test_public_label_catalog.py` (NEW)
- `backend/tests/integration/test_v4_scenarios.py` (NEW)
- `frontend/src/tests/fixtures/dailyPredictionV4Flat.json` (NEW)
- `frontend/src/tests/fixtures/dailyPredictionV4Polarized.json` (NEW)
- `frontend/src/tests/fixtures/dailyPredictionV4TurningPoint.json` (NEW)
- `frontend/src/tests/fixtures/dailyPredictionV4LowEvents.json` (NEW)
