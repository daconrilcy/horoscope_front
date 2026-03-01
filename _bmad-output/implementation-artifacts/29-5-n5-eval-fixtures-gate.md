# Story 29.5: N5 — Eval fixtures + publish gate

Status: done

## Story

As a QA engineer,
I want valider la qualité de l'interprétation via des fixtures de test et une gate de publication,
so that aucune régression qualitative n'atteigne la production.

## Acceptance Criteria

1. Un jeu de 7 fixtures YAML est créé, couvrant les cas nominaux et dégradés (full chart, no time, no location, minimal).
2. Les fixtures incluent les entrées (`chart_json`, `locale`, `question`) et les attentes de validation (`expected_schema_valid`, `expected_fields`).
3. Le chemin des fixtures (`eval_fixtures_path`) et le seuil de tolérance aux échecs (`eval_failure_threshold` à 0.20) sont configurés en base de données pour les deux use cases nataux.
4. La publication d'un prompt via l'API admin déclenche automatiquement le harness d'évaluation sur les fixtures associées.
5. La publication est bloquée avec une erreur 409 si le taux d'échec de l'évaluation dépasse le seuil configuré.
6. Les rapports d'évaluation sont persistés et consultables pour analyse en cas d'échec de publication.
7. Les métriques de performance et de qualité (latence, taux de fallback, status de validation) remontent dans le dashboard d'administration.

## Tasks / Subtasks

- [x] Créer les répertoires de fixtures
  - [x] `backend/app/tests/eval_fixtures/natal_interpretation_short/`
  - [x] `backend/app/tests/eval_fixtures/natal_interpretation/`
- [x] Rédiger les 7 fichiers YAML de fixtures avec des données de thèmes nataux réalistes
- [x] Mettre à jour `backend/scripts/seed_29_prompts.py`
  - [x] Ajouter la configuration `eval_fixtures_path` et `eval_failure_threshold` dans la base de données
- [x] Créer les tests unitaires du harness dans `backend/app/tests/unit/test_eval_harness_natal.py`
  - [x] Mocker le Gateway pour tester le succès et le blocage de publication (failure rate > 20%)
- [x] Vérifier et si besoin compléter la logique de "Publish Gate" dans `backend/app/api/v1/routers/admin_llm.py`
- [x] Valider que les métriques natales apparaissent dans le dashboard d'administration (`GET /v1/admin/llm/dashboard`)

## Dev Notes

- Le harness utilise le `LLMGateway` pour générer les sorties à partir des fixtures.
- En mode test, le Gateway doit être mocké pour éviter les appels API réels et les coûts associés.
- Le seuil de 20% permet une certaine flexibilité face à la variabilité de l'IA tout en garantissant un socle de qualité.

### Technical Requirements

- Backend: FastAPI/Python 3.13
- Testing: Pytest / AsyncMock / PyYAML
- Database: PostgreSQL (LlmUseCaseConfigModel, LlmCallLogModel)

### File Structure Requirements

- `backend/app/tests/eval_fixtures/natal_interpretation_short/*.yaml`
- `backend/app/tests/eval_fixtures/natal_interpretation/*.yaml`
- `backend/app/tests/unit/test_eval_harness_natal.py`
- `backend/scripts/seed_29_prompts.py` (modification)

### Testing Requirements

- Tests unitaires validant la logique du harness.
- Tests d'intégration de l'endpoint de publication (publish gate).

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 29, Story 29.5)
- Context documentation: `docs/agent/story-29-N5-eval-fixtures-gate.md`
