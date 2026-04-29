# DB Session Allowlist

Exceptions temporaires restantes après migration du lot représentatif.

Les fichiers listés ici peuvent encore référencer `SessionLocal`, `engine` ou `db_session_module.SessionLocal` dans le harnais de tests. Toute nouvelle exception doit être ajoutée explicitement avec une raison et une condition de sortie.

| File | Pattern | Reason | Exit condition |
|---|---|---|---|
| `backend/app/tests/conftest.py` | `db_session_module.SessionLocal` | Monkeypatch global existant explicitement hors suppression complète dans cette story. | Migrer les dépendants restants vers helpers canoniques. |
| `backend/tests/evaluation/__init__.py` | `SessionLocal` | Suite évaluation historique hors lot représentatif. | Migrer vers helper ou fixture dédiée d'évaluation. |
| `backend/tests/unit/test_incident_service_user_statuses.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/test_story_61_58_full.py` | `SessionLocal` | Test legacy hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/conftest.py` | `engine` | Harness d'alignement app/tests existant, borné à la SQLite secondaire. | Supprimer quand le monkeypatch global est retiré. |
| `backend/app/tests/integration/test_admin_actions_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_ai_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_dashboard_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_entitlements_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_exports_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_llm_canonical_consumption_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_llm_config_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_logs_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_persona_endpoints.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_stripe_actions_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_admin_support_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_astrologers_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_astrologers_v2.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_audit_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_auth_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_api_entitlements.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_astrology_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_billing_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_editorial_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_entitlement_repair.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_entitlements_audit.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_reconciliation_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_b2b_usage_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_billing_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_billing_api_61_65.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_billing_api_61_66.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_chat_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_chat_multi_persona.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_chat_persona_prompting.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_consultation_catalogue.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_consultation_third_party.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_consultations_router.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_contract_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_daily_prediction_api.py` | `db_session_module.SessionLocal` | Import indirect existant hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_daily_prediction_qa.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_enterprise_credentials_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_entitlements_plans.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_geocoding_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_guidance_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_horoscope_daily_entitlement.py` | `engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_horoscope_daily_variant_narration.py` | `engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_load_smoke_critical_flows.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_natal_calculate_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_natal_chart_accurate_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_natal_chart_long_entitlement.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_batch_handle_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_event_handle_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_event_handling_history_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_events_list_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_suppression_rules_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_alert_suppression_rules_effects_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_feature_flags_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_monitoring_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_monitoring_llm_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_persona_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_privacy_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_privacy_evidence_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_reference_data_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_secret_rotation_critical_flows.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_stripe_billing_profile_service_integration.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_stripe_checkout_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_stripe_customer_portal_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_stripe_webhook_api.py` | `SessionLocal` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_support_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_thematic_consultation_entitlement.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_user_birth_profile_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/test_user_natal_chart_api.py` | `SessionLocal, engine` | Test intégration hors lot représentatif. | Migrer vers helper `app/tests/helpers/db_session.py`. |
| `backend/app/tests/integration/_subprocess/secret_rotation_restart_runner.py` | `SessionLocal, engine` | Runner subprocess hors lot représentatif. | Migrer vers helper subprocess ou fixture dédiée. |
| `backend/app/tests/unit/test_audit_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_auth_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_b2b_billing_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_b2b_editorial_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_b2b_reconciliation_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_billing_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py` | `SessionLocal` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_canonical_entitlement_mutation_audit_review_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_chart_result_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_chat_guidance_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_enterprise_api_key_auth_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_enterprise_credentials_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_enterprise_quota_usage_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_entitlement_mutation_model_structure.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_guidance_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_incident_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_natal_calculation_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_natal_golden_swisseph.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_ops_monitoring_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_persona_config_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_privacy_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_product_entitlements_models.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_reference_data_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_stripe_billing_profile_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_stripe_billing_profile_service_61_65.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_user_astro_profile_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_user_birth_profile_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
| `backend/app/tests/unit/test_user_natal_chart_service.py` | `SessionLocal, engine` | Test unitaire DB hors lot représentatif. | Migrer vers helper/fixture explicite. |
