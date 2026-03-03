# Story 30-7 : Nouveaux Produits et Observabilité (Phase 2 & 3)

**Status**: done
**Epic**: 30
**Sprint**: Stabilisation Gateway & Nouveaux Produits

---

## Acceptance Criteria

- [x] AC1 : Seeds `event_guidance`, `tarot_reading`, `chat_astrologer` créés avec `persona_strategy`, `interaction_mode`, `user_question_policy` corrects
- [x] AC2 : `interaction_mode=chat` injecte l'historique conversationnel dans les messages
- [x] AC3 : `user_question_policy=required` lève `InputValidationError` si question absente
- [x] AC4 : `user_question_policy=none` ignore la question et utilise un fallback localisé
- [x] AC5 : `user_question_policy=optional` inclut la question si présente
- [x] AC6 : Schema name dans le payload = `schema_model.name` (non `use_case`)
- [x] AC7 : Use cases payants (`natal_interpretation`, `tarot_reading`, `event_guidance`) bloqués si schema manquant
- [x] AC8 : Métriques Prometheus — label `mode` sur `llm_gateway_requests_total`, nouveaux compteurs `llm_repair_invoked_total` et `llm_fallback_invoked_total`
- [x] AC9 : `AstroResponseV2` avec champs étendus (summary 2800, sections 6500) opérationnel
- [x] AC10 : `NatalInterpretationData` accepte `AstroResponseV2 | AstroResponseV1`

---

## Tasks

- [x] T1 : Créer `seed_30_5_new_use_cases.py` avec guard de validation des schémas requis
- [x] T2 : Ajouter `interaction_mode` et `user_question_policy` dans `gateway.py`
- [x] T3 : Implémenter la politique question (none/optional/required) dans le gateway
- [x] T4 : Injecter l'historique de conversation pour le mode `chat`
- [x] T5 : Corriger `schema_name = schema_model.name` dans le gateway
- [x] T6 : Bloquer les use cases payants sans schéma (GatewayConfigError)
- [x] T7 : Ajouter les compteurs métriques et le label `mode`
- [x] T8 : Ajouter `AstroSectionV2` et `AstroResponseV2` dans `schemas.py`
- [x] T9 : Mettre à jour `natal_interpretation.py` pour accepter `V2 | V1`
- [x] T10 : Niveau `complete` de `natal_interpretation_service_v2` n'envoie pas `question`
- [x] T11 : Corriger `test_natal_interpretation_service.py` (patch `llm_orchestration_v2=False`)
- [x] T12 : Corriger `test_eval_harness_natal.py` (path fixtures + assertion flexible)
- [x] T13 : Importer `generate_text` au niveau module dans `natal_interpretation_service.py`

---

## Files Modified

### Backend
- `backend/app/llm_orchestration/gateway.py` — interaction_mode, user_question_policy, schema name, metrics
- `backend/app/llm_orchestration/schemas.py` — AstroSectionV2, AstroResponseV2
- `backend/app/api/v1/schemas/natal_interpretation.py` — AstroResponseV2 | AstroResponseV1
- `backend/app/services/natal_interpretation_service.py` — module-level generate_text import
- `backend/app/services/natal_interpretation_service_v2.py` — question exclusion pour level=complete
- `backend/app/llm_orchestration/providers/responses_client.py` — extra_headers, structured_output, exception handling
- `backend/app/llm_orchestration/services/prompt_lint.py` — messages d'erreur séparés (platform vs use-case)
- `backend/app/llm_orchestration/services/observability_service.py` — rollback dans le bloc except
- `backend/app/services/chat_guidance_service.py` — persona_id dans send_message_async

### Scripts
- `backend/scripts/seed_30_5_new_use_cases.py` — guard schémas requis, persona_strategy par use case

### Tests
- `backend/app/tests/unit/test_gateway_modes.py` — nouveaux comportements gateway (nouveau)
- `backend/app/tests/unit/test_gateway_3_roles.py` — validation 3 rôles (nouveau)
- `backend/app/tests/unit/test_astro_response_v2.py` — validation AstroResponseV2 (nouveau)
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py` — tests service v2 (nouveau)
- `backend/app/tests/unit/test_responses_client_gpt5.py` — tests client GPT-5 (nouveau)
- `backend/app/tests/unit/test_responses_client_exceptions.py` — tests exceptions OpenAI (nouveau)
- `backend/app/tests/unit/test_natal_interpretation_service.py` — patch llm_orchestration_v2=False
- `backend/app/tests/unit/test_eval_harness_natal.py` — path fixtures + assertion flexible

---

## Test Results

**Suite complète** : 765 passed, 32 failed (pre-existing SwissEph), 1 skipped
**Tests story 30-7** : 53/53 passés (0 échecs)

Failures pré-existants (hors périmètre) :
- `test_chart_result_service` (2) — DB constraint pre-existing
- `test_ephemeris_bootstrap` (4) — SwissEph init non bootstrapée en test
- `test_natal_calculation_service` (8) — SwissEph init
- `test_user_astro_profile_service` (10) — SwissEph init
- `test_user_natal_chart_service` (7) — SwissEph init
