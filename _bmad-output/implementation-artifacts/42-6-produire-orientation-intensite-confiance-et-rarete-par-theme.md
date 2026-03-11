# Story 42.6: Produire orientation, intensité, confiance et rareté par thème

Status: done

## Story

As a product designer,
I want que chaque thème quotidien expose plusieurs dimensions de lecture,
so that le produit distingue enfin une journée neutre, une journée faible, une journée active et une journée instable.

## Acceptance Criteria

1. Le moteur calcule au minimum:
   - `score_20`
   - `intensity_20`
   - `confidence_20`
   - `rarity_percentile`
2. `score_20` représente l'orientation du thème, sans se substituer à l'intensité.
3. La formule de `confidence_20` est explicitement définie et stabilisée à partir d'au moins:
   - part de signal expliqué
   - stabilité de la courbe
   - qualité de baseline disponible ou non
   - cohérence inter-drivers
4. `rarity_percentile` est explicitement distingué d'un simple percentile relatif utilisateur.
5. Les nouvelles métriques sont dérivées des courbes lissées du moteur v3.
6. Le backend conserve une lecture lisible et compatible avec le produit quotidien.
7. Les tests métier couvrent plusieurs profils de journées contrastées.

## Tasks / Subtasks

- [x] Task 1: Définir les métriques v3 par thème (AC: 1, 2, 3, 4)
  - [x] Formaliser la sémantique de `confidence`
  - [x] Formaliser la sémantique de `rarity`
  - [x] Définir les formules de dérivation
  - [x] Définir les bornes et conventions
  - [x] Introduire les types de sortie dédiés

- [x] Task 2: Brancher ces métriques dans l'agrégation v3 (AC: 3)
  - [x] Produire les quatre dimensions pour chaque thème
  - [x] Préserver une compatibilité lisible avec la note publique

- [x] Task 3: Préparer l'usage produit des nouvelles métriques (AC: 4)
  - [x] Prévoir comment elles nourriront blocs, fenêtres et evidence pack
  - [x] Éviter de les exposer trop tôt sans garde-fous

- [x] Task 4: Tests (AC: 7)
  - [x] Tester plusieurs journées types
  - [x] Vérifier que score et intensité peuvent diverger utilement
  - [x] Vérifier que `confidence` et `rarity` ne se confondent pas avec le relatif simple

## Dev Notes

- C'est la story structurante côté produit. Elle corrige le problème actuel où `10/20` peut vouloir dire plat, ambigu, faible, ou peu lisible.
- Une journée peut être:
  - bien orientée mais peu intense
  - neutre mais très intense
  - difficile mais très lisible
- Le système doit pouvoir exprimer ces cas.
- La formule de `confidence` doit être stabilisée ici, car elle irrigue ensuite blocs, pivots, fenêtres, relatif et flat day.
- `rarity_percentile` doit représenter l'inhabituel du signal, pas seulement sa position relative dans une baseline utilisateur.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/aggregator.py`
  - `backend/app/prediction/schemas.py`
  - `backend/app/prediction/persisted_snapshot.py` pour les stories suivantes

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/aggregator.py]
- [Source: backend/app/prediction/schemas.py]
- [Source: backend/app/prediction/public_projection.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex + Gemini CLI Adversarial Fixer

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.
- Revue de code adversarial effectuée: Correction des noms de métriques, amélioration des formules de confiance et rareté.

### Completion Notes List

- Story corrigée après revue de code adversariale.
- Les métriques v3 sont maintenant dérivées des courbes lissées et la formule de confiance inclut part expliquée, stabilité, baseline et cohérence.
- Le chemin de compatibilité backend/public/persistance conserve désormais les métriques `score_20`, `intensity_20`, `confidence_20` et `rarity_percentile`.

### File List

- `_bmad-output/implementation-artifacts/42-6-produire-orientation-intensite-confiance-et-rarete-par-theme.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/api/v1/routers/predictions.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/prediction/public_projection.py`
- `backend/migrations/versions/20260311_0045_add_v3_daily_metrics_to_category_scores.py`
- `backend/app/tests/unit/test_v3_metrics.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/app/tests/integration/test_prediction_persistence.py`
