# Story 28.6: Observabilité & Evaluation harness — logs sanitisés, replay tool, tests offline

Status: done

## Story

As a backend platform engineer,
I want un harness d'évaluation qui stocke chaque appel gateway de façon sanitisée, permet de rejouer une requête avec un prompt différent, et valide un jeu de cas tests offline avant toute publication de prompt,
so que je peux détecter une régression de comportement LLM avant qu'elle atteigne la prod, et piloter les performances du gateway par des métriques exploitables.

## Acceptance Criteria

1. **Given** chaque appel `LLMGateway.execute()` **When** il se termine (succès ou erreur) **Then** un enregistrement `LlmCallLog` est persisté avec : `use_case`, `prompt_version_id`, `persona_id`, `model`, `latency_ms`, `tokens_in`, `tokens_out`, `cost_usd_estimated`, `validation_status` (valid/repair_success/fallback/error), `repair_attempted`, `fallback_triggered`, `request_id`, `trace_id`, `input_hash` (SHA-256 de `user_input` sanitisé), `timestamp` — jamais de données utilisateur en clair. ✅
2. **Given** un admin authentifié **When** il consulte `GET /v1/admin/llm/call-logs` **Then** il reçoit les logs paginés filtrables par `use_case`, `validation_status`, `date_range`, `prompt_version_id`. ✅
3. **Given** un `request_id` existant dans `LlmCallLog` **When** un dev appelle `POST /v1/admin/llm/replay` avec `{ request_id, prompt_version_id }` **Then** le gateway réexécute la requête originale avec le nouveau `prompt_version_id` et retourne un `ReplayResult` (sans persister le résultat dans `LlmCallLog`). ✅
4. **Given** un use_case avec un `eval_fixtures_path` configuré **When** un admin publie un nouveau prompt via `PATCH /v1/admin/llm/use-cases/{key}/prompts/{id}/publish` **Then** le système exécute automatiquement le jeu de tests offline et retourne les résultats avant confirmation de publication — la publication est bloquée si le taux d'échec de validation dépasse `eval_failure_threshold` (défaut : 20 %). ✅
5. **Given** le endpoint `GET /v1/admin/llm/dashboard` **When** un admin le consulte **Then** il reçoit, par use_case et par période (24h/7j/30j) : `request_count`, `avg_latency_ms`, `p95_latency_ms`, `total_tokens`, `total_cost_usd`, `validation_status_distribution` (% valid/repair/fallback/error), `repair_rate`, `fallback_rate`, `avg_tokens_per_request`, `evidence_warning_rate` (% d'appels ayant produit au moins un item `evidence` en texte libre, non conforme au pattern UPPER_SNAKE_CASE). ✅
6. **Given** les fixtures de test offline **When** elles sont définies **Then** chaque fixture contient : `input` (user_input conforme à l'input_schema du use_case), `expected_schema_valid` (bool), `expected_fields` (dict partiel à vérifier dans la sortie), `tags` (list, ex: ["regression", "edge_case"]) — les fixtures ne contiennent pas de données utilisateur réelles. ✅
7. **Given** le replay tool **When** il est appelé en dehors d'un environnement `ENV=dev|staging` **Then** il est refusé (HTTP 403) — protection contre l'exposition en prod. ✅

## Tasks / Subtasks

- [x] Task 1 (AC: 1)
- [x] Task 2 (AC: 1)
- [x] Task 3 (AC: 2, 5)
- [x] Task 4 (AC: 3, 7)
- [x] Task 5 (AC: 4, 6)
- [x] Task 6 (AC: 4, 6)
- [x] Task 7 (AC: 1-7)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- [2026-03-01 10:00] Initializing Story 28.6 implementation.
- [2026-03-01 10:05] Context loaded. Sprint status updated to in-progress.
- [2026-03-01 14:15] Task 1, 2, 4 implemented (Models, Replay, Integration in Gateway).
- [2026-03-01 14:30] Task 3 implemented (Admin API & Dashboard).
- [2026-03-01 14:45] Task 5, 6 implemented (Eval Harness & Fixtures).
- [2026-03-01 15:10] Task 7 completed (Validation with 41 tests passing).

### Implementation Plan

1. **Task 1 & 2 (Logging & Persistence)**
   - Create SQLAlchemy models `LlmCallLog` and `LlmReplaySnapshot` in `backend/app/infra/db/models/llm_observability.py`.
   - Update `backend/app/infra/db/models/__init__.py`.
   - Generate and run Alembic migration (manual recreation for SQLite dev).
   - Integrate logging in `LLMGateway.execute()` with `input_hash` (SHA-256).
   - Implement log retention (TTL 90 days) logic and purge.

2. **Task 4 (Replay Service)**
   - Add `cryptography` to `backend/pyproject.toml`.
   - Implement `ReplayService` in `backend/app/llm_orchestration/services/replay_service.py` with AES-256 Fernet.
   - Store encrypted input in `LlmReplaySnapshot` during `LLMGateway.execute()`.

3. **Task 3 (Admin Endpoints & Dashboard)**
   - Add `GET /v1/admin/llm/call-logs` and `GET /v1/admin/llm/dashboard` to `backend/app/api/v1/routers/admin_llm.py`.
   - Implement SQL-based aggregations for the dashboard.

4. **Task 5 & 6 (Eval Harness & Fixtures)**
   - Extend `LlmUseCaseConfigModel` with `eval_fixtures_path` and `eval_failure_threshold`.
   - Implement `EvalHarness` in `backend/app/llm_orchestration/services/eval_harness.py`.
   - Create initial YAML fixtures for `natal_interpretation`, `chat_astrologer`, `tarot_reading`.
   - Integrate `EvalHarness` into the `publish` endpoint in `admin_llm.py`.

5. **Task 7 (Validation)**
   - Add comprehensive tests for logging, dashboard, replay, and eval harness.
   - Verify all ACs are met.

### Completion Notes List

- Database models `LlmCallLogModel` and `LlmReplaySnapshotModel` are operational.
- `LLMGateway` now logs every call (even errors) through a `try/finally` block.
- User input is stored encrypted (AES-256) for 7 days to allow replaying, while permanent logs only store a non-reversible `input_hash`.
- `ReplayService` allows re-running a request with a new prompt version and provides a diff of the results.
- `EvalHarness` automatically runs offline tests when publishing a prompt, blocking if the failure rate is above the threshold.
- Admin dashboard provides real-time metrics including latency, tokens, costs, and quality signals (repair rate, fallback rate, evidence warnings).
- 41 unit and integration tests verify the orchestration layer.

### File List

- `backend/app/infra/db/models/llm_observability.py`
- `backend/app/llm_orchestration/services/observability_service.py`
- `backend/app/llm_orchestration/services/replay_service.py`
- `backend/app/llm_orchestration/services/eval_harness.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/admin_models.py`
- `backend/app/core/config.py`
- `backend/app/llm_orchestration/eval_fixtures/` (3 directories with fixtures)
- `backend/app/llm_orchestration/tests/test_observability.py`
- `backend/app/llm_orchestration/tests/test_replay_service.py`
- `backend/app/llm_orchestration/tests/test_eval_harness.py`
- `backend/app/llm_orchestration/tests/conftest.py`

## Change Log

- 2026-03-01: Story créée (Epic 28, LLM Orchestration Layer).
- 2026-03-01: Mise à jour statut in-progress et plan d'implémentation.
- 2026-03-01: Implémentation terminée, tests validés, story marquée DONE.
