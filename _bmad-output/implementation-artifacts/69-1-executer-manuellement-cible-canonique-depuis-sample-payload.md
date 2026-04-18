# Story 69.1: Exécuter manuellement une cible canonique depuis un sample payload

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin ops / LLM operator,
I want déclencher explicitement une exécution LLM à partir d'une runtime preview valide,
so that je puisse vérifier le comportement réel du provider sur une cible canonique contrôlée.

## Acceptance Criteria

1. Une exécution réelle peut être déclenchée uniquement depuis une runtime preview valide.
2. Une runtime preview incomplète bloque l'action d'exécution avec un message explicite.
3. L'appel réel transporte les métadonnées runtime pertinentes (`manifest_entry_id`, provider, modèle, paramètres).
4. L'exécution suit le chemin nominal du gateway et ses garde-fous existants.

## Tasks / Subtasks

- [x] Task 1: Définir l'endpoint ou la commande admin d'exécution manuelle (AC: 1, 2, 3, 4)
  - [x] Choisir un endpoint explicite distinct de la preview.
  - [x] Définir le contrat d'entrée à partir du sample payload sélectionné.
- [x] Task 2: Brancher le déclenchement UI (AC: 1, 2)
  - [x] Ajouter l'action `Exécuter avec le LLM`.
  - [x] Afficher les préconditions et les blocages.
- [x] Task 3: Verrouiller la corrélation et la sécurité (AC: 3, 4)
  - [x] Préserver request/correlation ids et métadonnées d'observabilité.
  - [x] Vérifier permissions admin strictes.

### Review Findings

- [x] [Review][Patch] Les exécutions manuelles de samples "chat opening" perdent `last_user_msg` dans le bloc utilisateur transmis au provider [backend/app/api/v1/routers/admin_llm.py:2052]
- [x] [Review][Patch] L'endpoint `execute-sample` ne crée aucun audit event persistant pour une action admin pourtant sensible [backend/app/api/v1/routers/admin_llm.py:2005]

## Dev Notes

### Technical Requirements

- Cette story introduit un appel provider réel.
- Il ne faut pas contourner `LLMGateway` ni `ProviderRuntimeManager`.
- Le déclenchement doit être explicitement opérateur, jamais implicite au chargement de la page.

### Architecture Compliance

- Respecter les garde-fous `timeout`, `retry`, `classification d'erreurs`, `redaction`, `observability`.
- L'exécution admin doit être distinguable du trafic nominal produit.

### File Structure Requirements

- Backend admin LLM router.
- Frontend admin prompts.
- Tests backend et frontend sur succès/erreur/blocage.

### Testing Requirements

- Cas valide.
- Cas bloqué car runtime preview incomplète.
- Cas erreur provider.
- Cas accès non autorisé.

### Previous Story Intelligence

- `68.2` fournit la runtime preview sur laquelle l'exécution s'appuie.
- `66.33`, `66.37`, `66.43`, `66.44` sont des références critiques pour le comportement runtime et ops.

### Project Structure Notes

- Toute action doit être visible et explicitement confirmable côté UI.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [66-33-durcissement-operationnel-appel-provider-openai.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-33-durcissement-operationnel-appel-provider-openai.md)
- [66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-37-observabilite-d-exploitation-complete-avec-alertes-structurees-sur-les-dimensions-canoniques.md)
- [66-43-chaos-testing-provider-runtime.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-43-chaos-testing-provider-runtime.md)
- [66-44-gate-production-continue-par-snapshot.md](C:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-44-gate-production-continue-par-snapshot.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`

### Completion Notes List

- Endpoint `POST /v1/admin/llm/catalog/{manifest_entry_id}/execute-sample` (corps `{ sample_payload_id }`) : réutilise la résolution runtime preview via `_build_admin_resolved_catalog_view`, refuse si placeholders bloquants ou erreur de rendu (`runtime_preview_incomplete_for_execution`), sinon `LLMGateway.execute_request` avec `ExecutionUserInput` / `extra_context` enrichi (`_manifest_entry_id`, `_admin_manual_canonical_execution`, payload sample).
- La vue résolue expose `use_case_key` et `context_quality` pour corrélation et clients.
- Gateway : `_manifest_entry_id` issu du contexte admin n’est plus écrasé par `None` si l’assembly snapshot ne porte pas d’id.
- UI : bouton « Exécuter avec le LLM » en mode prévisualisation runtime, désactivé si sample absent ou preview incomplète ; affichage succès / erreur.
- Tests d’intégration : exécution mockée gateway + rejet preview incomplète (`test_admin_llm_catalog.py`). Front : tests existants mis à jour pour les nouveaux champs.
- Mitigation risque schéma pytest : `ensure_configured_sqlite_file_matches_alembic_head` dans `bootstrap.py` (Alembic sur `session.engine` et `settings.database_url` ; `create_all` ORM uniquement sur la base secondaire type fichier temporaire `app/tests/conftest.py`). Hook `pytest_sessionstart` évité (exécuté avant la collecte). `backend/tests/conftest.py` fixture session autouse ; `tests/integration/app_db.py` pour ouvrir la session sur le `SessionLocal` effectif ; `app/tests/integration/conftest.py` inchangé côté appel ; `AGENTS.md` et `pyproject.toml` (`testpaths` inclut `tests/integration`).
- Revue post-implémentation : l’endpoint d’exécution manuelle préserve désormais `last_user_msg` comme fallback d’entrée utilisateur pour rester cohérent avec la runtime preview, et journalise un audit event persistant `llm_catalog_execute_sample` en succès comme en échec.

### File List

- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/admin_llm_error_codes.py`
- `backend/app/llm_orchestration/gateway.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/conftest.py`
- `backend/tests/integration/app_db.py`
- `backend/app/infra/db/bootstrap.py`
- `backend/app/tests/integration/conftest.py`
- `backend/pyproject.toml`
- `AGENTS.md`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `_bmad-output/implementation-artifacts/69-1-executer-manuellement-cible-canonique-depuis-sample-payload.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-04-17 : Exécution manuelle LLM depuis sample payload (POST execute-sample, UI, tests, codes d’erreur, correctif corrélation manifest gateway).
- 2026-04-17 : Alignement SQLite pytest (fixture post-collecte, double URL Alembic, `app_db`, doc AGENTS).
- 2026-04-18 : Correctifs post-review 69.1 (`last_user_msg` préservé à l’exécution manuelle, audit trail persistant, tests d’intégration ajustés).
