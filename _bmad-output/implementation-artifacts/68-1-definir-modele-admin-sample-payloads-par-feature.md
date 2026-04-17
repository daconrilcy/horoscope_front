# Story 68.1: Définir le modèle admin des sample payloads par feature

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin platform operator,
I want disposer d'un modèle de `sample payload` réutilisable par feature et locale,
so that je puisse prévisualiser les prompts avec des données runtime réalistes mais non sensibles.

## Acceptance Criteria

1. Un sample payload admin porte au minimum `name`, `feature`, `locale`, `payload_json`, `description`, `is_default` ou un statut équivalent.
2. Les sample payloads sont bornés par feature/locale et validés selon une cohérence minimale.
3. Un sample payload `natal` peut contenir `chart_json` et d'autres placeholders runtime requis.
4. Les données stockées et affichées respectent la redaction et ne doivent pas être de vraies données utilisateur.

## Tasks / Subtasks

- [x] Task 1: Définir le contrat backend des sample payloads (AC: 1, 2, 3, 4)
  - [x] Choisir persistance DB, config admin ou stockage contrôlé existant.
  - [x] Définir les schémas API CRUD minimaux.
  - [x] Définir les règles de validation par feature.
- [x] Task 2: Exposer une lecture admin exploitable (AC: 1, 2)
  - [x] Lister les samples disponibles par feature/locale.
  - [x] Identifier un sample par défaut ou recommandé.
- [x] Task 3: Verrouiller sécurité et QA (AC: 4)
  - [x] Tester la redaction et les validations.
  - [x] Tester qu'aucune donnée sensible non autorisée n'est exposée.

## Dev Notes

### Technical Requirements

- Le terme recommandé est `sample payload` plutôt que `fake user`.
- Ne pas introduire un modèle centré faux-compte utilisateur alors que le besoin réel est un payload runtime.
- Prévoir des payloads compatibles avec `chart_json` et futurs placeholders runtime d'autres features.

### Architecture Compliance

- Les sample payloads servent à alimenter les placeholders runtime de la chaîne canonique existante.
- Ils ne doivent pas contourner le gateway ni la politique de redaction.

### File Structure Requirements

- Backend probable: nouveaux modèles/routers admin LLM ou extension du domaine `admin_llm`.
- Frontend: future consommation dans `AdminPromptsPage.tsx` et `frontend/src/api/adminPrompts.ts`.

### Testing Requirements

- CRUD minimal backend.
- Validation feature/locale.
- Non-fuite de données sensibles.

### Previous Story Intelligence

- Les stories 67.x ont préparé la surface UI et la sémantique de preview.
- Cette story pose le socle de données nécessaire à la runtime preview, sans exécuter le provider.

### Project Structure Notes

- Réutiliser les patterns admin existants et le style des endpoints `admin_llm`.

### References

- [docs/llm-prompt-generation-by-feature.md](C:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [architecture.md](C:/dev/horoscope_front/_bmad-output/planning-artifacts/architecture.md)
- [admin_llm.py](C:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Source backlog: `epics-admin-llm-preview-execution.md`
- Implémentation backend: modèle SQLAlchemy + migration Alembic + routeur admin dédié.
- Validation: `.\.venv\Scripts\Activate.ps1; cd backend; ruff check ...; pytest -q tests/integration/test_admin_llm_sample_payloads.py`

### Completion Notes List

- Story file created from BMAD backlog.
- Ajout du modèle `LlmSamplePayloadModel` + migration `20260417_0069` pour persister les sample payloads administrables par `feature`/`locale`.
- Ajout du routeur `admin_llm_sample_payloads` (CRUD minimal + listing avec `recommended_default_id`) sous `/v1/admin/llm/sample-payloads`.
- Validation métier implémentée: feature canonique supportée, locale au format `xx-XX`, payload JSON non vide, `chart_json` obligatoire pour `natal`, rejet de clés sensibles (credentials/identifiants).
- QA sécurité: tests d'intégration couvrant CRUD/lecture par défaut recommandé et rejets des payloads sensibles.
- Durcissements post-review: `flush()` avant promotion de default via POST/PATCH, validation des noms trimés, support explicite de `description: null` en PATCH.
- Conflits d'unicité traduits en erreurs métier `409` (`sample_payload_name_conflict`, `sample_payload_default_conflict`) au lieu d'erreurs `500`.
- Harmonisation des codes d'erreur via enum partagé `AdminLlmErrorCode` (scope `admin_llm*`).

### File List

- `_bmad-output/implementation-artifacts/68-1-definir-modele-admin-sample-payloads-par-feature.md`
- `backend/app/infra/db/models/llm_sample_payload.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/migrations/versions/20260417_0069_add_llm_sample_payloads.py`
- `backend/app/api/v1/routers/admin_llm_sample_payloads.py`
- `backend/app/api/v1/routers/admin_llm_error_codes.py`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/admin_llm_assembly.py`
- `backend/app/main.py`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
- `backend/tests/integration/test_admin_llm_catalog.py`

### Change Log

- 2026-04-17: Implémentation complète story 68.1 (modèle DB + migration + API admin CRUD/listing + validations sécurité + tests intégration).
- 2026-04-17: Correctifs post-review 68.1 (robustesse transactionnelle default, validation `name` trimé, PATCH `description=null`, mapping `IntegrityError` en `409` métier, centralisation codes d'erreur admin LLM).
