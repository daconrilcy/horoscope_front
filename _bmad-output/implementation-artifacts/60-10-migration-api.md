# Story 60.10 : Versionner le contrat API public et sécuriser la migration

Status: review

## Story

En tant qu'opérateur du système,
je veux que la migration vers le nouveau payload V4 ne casse pas le front en production,
afin de pouvoir déployer le backend et le frontend indépendamment sans regression.

## Acceptance Criteria

1. Tous les nouveaux champs (`day_climate`, `domain_ranking`, `time_windows`, `turning_point` singulier, `best_window`, `astro_foundation`) sont optionnels dans `DailyPredictionResponse` (default `None`) — le payload V3 reste valide.
2. Un flag `payload_version: str` est ajouté dans `DailyPredictionMeta` (`"v4"` si nouveaux champs présents, `"v3"` sinon).
3. Le front consomme les nouveaux champs seulement si présents, avec fallback vers l'ancien affichage si `payload_version != "v4"`.
4. Les anciens champs (`summary`, `categories`, `timeline`, `turning_points` liste, `decision_windows`, `micro_trends`) sont conservés dans le payload.
5. Les tests d'intégration API existants dans `backend/app/tests/integration/test_daily_prediction_api.py` passent sans modification.
6. Un test vérifie que le payload V4 ne casse pas un client qui ignore les nouveaux champs.
7. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Vérifier l'optionalité de tous les nouveaux champs (AC: 1)
  - [x] Vérifié dans `backend/app/api/v1/routers/predictions.py`.

- [x] T2 — Ajouter `payload_version` dans `DailyPredictionMeta` (AC: 2)
  - [x] Ajouté dans le DTO Pydantic et initialisé à `"v4"` dans `PublicPredictionAssembler`.

- [x] T3 — Mettre à jour le type TypeScript (AC: 3)
  - [x] Ajouté dans `frontend/src/types/dailyPrediction.ts`.
  - [x] Logique de switch implémentée dans `DailyHoroscopePage.tsx`.

- [x] T4 — S'assurer que les anciens champs sont inchangés (AC: 4)
  - [x] Vérifié via tests d'intégration.

- [x] T5 — Tests de non-régression (AC: 5, 6)
  - [x] Tests existants passent.
  - [x] Nouveau test d'intégration `backend/tests/integration/test_v4_migration.py` créé.

- [x] T6 — Documentation du contrat de migration (AC: 3)
  - [x] Créé `docs/agent/payload-migration-v3-v4.md`.

## Dev Notes
...
### File List

- `backend/app/api/v1/routers/predictions.py` (MOD)
- `backend/app/prediction/public_projection.py` (MOD)
- `frontend/src/types/dailyPrediction.ts` (MOD)
- `frontend/src/pages/DailyHoroscopePage.tsx` (MOD)
- `backend/tests/integration/test_v4_migration.py` (NEW)
- `docs/agent/payload-migration-v3-v4.md` (NEW)
