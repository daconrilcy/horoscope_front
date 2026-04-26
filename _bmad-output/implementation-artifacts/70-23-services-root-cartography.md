# Story 70-23 - Cartographie racine `backend/app/services`

## Allowlist finale racine

| Fichier | Responsabilite dominante | Consommateurs principaux | Decision | Chemin canonique cible | Justification / tests impactes |
| --- | --- | --- | --- | --- | --- |
| `__init__.py` | Package racine neutre | Imports package `app.services` | conserver | `backend/app/services/__init__.py` | Aucun re-export; garde-fou `test_story_70_23_services_structure_guard.py`. |
| `auth_service.py` | Authentification transverse | API auth, tests auth | conserver | racine | Service transverse hors sous-domaine metier unique. |
| `feature_registry_consistency_validator.py` | Validation transverse du registre features | CI, startup/tests | conserver | racine | Traverse entitlement + b2b; garde-fou structurel. |
| `geocoding_service.py` | Geocoding transverse | user profile, natal | conserver | racine | Service reutilise par plusieurs sous-domaines. |
| `privacy_service.py` | Privacy / RGPD | endpoints privacy/support | conserver | racine | Transverse gouvernance. |
| `reference_data_service.py` | Seed / lecture reference data | prediction, admin reference | conserver | racine | Service transverse plateforme/reference. |

## Fichiers deplaces vers un namespace canonique

| Fichier racine initial | Responsabilite dominante | Consommateurs principaux | Decision | Chemin canonique cible | Tests / patch targets impactes |
| --- | --- | --- | --- | --- | --- |
| `billing_service.py` | facade billing B2C | APIs billing/support/privacy/entitlement, tests billing | deplacer + scinder | `services/billing/service.py` | patch targets et imports migres vers `app.services.billing.service`. |
| `stripe_billing_profile_service.py` | snapshot Stripe | admin users, APIs Stripe, tests Stripe | deplacer | `services/billing/stripe_billing_profile_service.py` | imports API/tests migres. |
| `stripe_checkout_service.py` | checkout Stripe | router billing, tests Stripe | deplacer | `services/billing/stripe_checkout_service.py` | imports API/tests migres. |
| `stripe_customer_portal_service.py` | portail client Stripe | router billing, tests Stripe | deplacer | `services/billing/stripe_customer_portal_service.py` | imports API/tests migres. |
| `stripe_webhook_idempotency_service.py` | idempotence webhook | webhook Stripe, tests unitaires | deplacer | `services/billing/stripe_webhook_idempotency_service.py` | patch targets migres. |
| `stripe_webhook_service.py` | orchestration webhook | router billing, tests Stripe | deplacer | `services/billing/stripe_webhook_service.py` | imports API/tests migres. |
| `pricing_experiment_service.py` | pricing experiments | main, billing API, tests pricing | deplacer | `services/billing/pricing_experiment_service.py` | imports migres. |
| `consultation_catalogue_service.py` | catalogue consultation | routers consultation/LLM | deplacer | `services/consultation/catalogue_service.py` | imports migres. |
| `consultation_fallback_service.py` | fallback consultation | precheck/LLM/tests | deplacer | `services/consultation/fallback_service.py` | imports migres. |
| `consultation_precheck_service.py` | precheck consultation | routers consultation/LLM/tests | deplacer | `services/consultation/precheck_service.py` | imports migres. |
| `consultation_third_party_service.py` | tiers consultation | routers consultation/LLM | deplacer | `services/consultation/third_party_service.py` | imports migres. |
| `astro_context_builder.py` | contexte astro LLM | guidance, tests astro context | deplacer | `services/natal/astro_context_builder.py` | imports / patch targets migres. |
| `natal_calculation_service.py` | calcul natal | users/natal APIs/tests | deplacer | `services/natal/calculation_service.py` | imports / patch targets migres. |
| `natal_pdf_export_service.py` | export PDF natal | endpoint natal/tests | deplacer | `services/natal/pdf_export_service.py` | imports / patch targets migres. |
| `natal_preparation_service.py` | preparation natal | endpoint engine/tests | deplacer | `services/natal/preparation_service.py` | imports migres. |
| `prediction_compute_runner.py` | execution moteur prediction | `daily_prediction_service`, tests | deplacer | `services/prediction/compute_runner.py` | imports migres. |
| `prediction_context_repair_service.py` | repair runtime prediction | `daily_prediction_service`, tests | deplacer + decoupler scripts | `services/prediction/context_repair_service.py` | import `scripts/*` retire; tests migres. |
| `prediction_fallback_policy.py` | fallback prediction | `daily_prediction_service` | deplacer | `services/prediction/fallback_policy.py` | imports migres. |
| `prediction_request_resolver.py` | resolution input prediction | `daily_prediction_service`, tests | deplacer | `services/prediction/request_resolver.py` | imports / patch targets migres. |
| `prediction_run_reuse_policy.py` | reuse prediction | `daily_prediction_service`, tests | deplacer | `services/prediction/run_reuse_policy.py` | imports migres. |
| `relative_scoring_service.py` | enrichissement relatif prediction | `daily_prediction_service`, tests integration prediction | deplacer | `services/prediction/relative_scoring_service.py` | imports et patch targets migres vers `app.services.prediction.relative_scoring_service`. |
| `daily_prediction_types.py` | DTO / erreurs prediction | `daily_prediction_service`, API/tests, jobs | deplacer | `services/prediction/types.py` | imports migres vers `app.services.prediction.types` ; la facade racine `daily_prediction_service.py` reste contractuelle. |
| `daily_prediction_service.py` | facade publique prediction | API prediction, QA, jobs, helpers natals | supprimer facade racine | `services/prediction/__init__.py` | imports migres vers `app.services.prediction` ; plus aucun point d entree prediction nominal a la racine. |
| `email_service.py` | Envoi email | auth, onboarding, tests email | deplacer | `services/email/service.py` | imports et patch targets migres vers `app.services.email.service`. |
| `email_provider.py` | Selection du provider email | `services/email/service.py`, tests email | deplacer | `services/email/provider.py` | regroupement mono-domaine `email/`, sans facade racine legacy. |
| `quota_usage_service.py` | Consommation quotas canonique | entitlement, billing quota, chat, admin users | deplacer | `services/quota/usage_service.py` | imports et patch targets migres vers `app.services.quota.usage_service`. |
| `quota_window_resolver.py` | Resolution fenetres de quotas | quota usage, billing, B2B, tests quota | deplacer | `services/quota/window_resolver.py` | imports migres vers `app.services.quota.window_resolver`. |
| `chart_result_service.py` | Persistance / lecture de resultats de chart | endpoints natal, LLM QA, tests chart | deplacer | `services/chart/result_service.py` | imports et patch targets migres vers `app.services.chart.result_service`. |
| `chart_json_builder.py` | Transformation de charge utile astrologique | natal, LLM generation, tests chart | deplacer | `services/chart/json_builder.py` | imports migres vers `app.services.chart.json_builder`. |
| `current_context.py` | contexte courant pour guidances LLM | `chat_guidance_service`, `guidance_service`, tests | deplacer | `services/llm_generation/guidance/current_context.py` | plus de consommation transverse hors guidance ; imports et tests migres. |
| `persona_config_service.py` | configuration des personas astrologues | generation de prompt guidance/chat, routeur ops persona, tests | deplacer | `services/llm_generation/guidance/persona_config_service.py` | le service appartient au domaine guidance/persona ; imports migres. |
| `feature_flag_service.py` | administration des feature flags | routeurs `admin_content`, `ops_feature_flags`, tests | deplacer | `services/ops/feature_flag_service.py` | rattache au namespace operationnel ; imports migres. |
| `cross_tool_report.py` | helper dev-only de rapport cross-tool | `scripts/natal-cross-tool-report-dev.py`, tests | sortir du runtime applicatif | `backend/scripts/cross_tool_report.py` | usage exclusivement script/dev ; plus de raison de rester sous `app.services`. |
| `disclaimer_registry.py` | registre statique de disclaimers | routes natales, PDF natal, interpretation LLM, tests | deplacer | `services/resources/templates/disclaimer_registry.py` | imports migres vers `app.services.resources.templates.disclaimer_registry`. |
| `audit_service.py` | audit operationnel | admin/support/b2b/privacy/tests | deplacer | `services/ops/audit_service.py` | imports API/tests migres. |
| `incident_service.py` | incidents support | support/help/tests | deplacer | `services/ops/incident_service.py` | imports migres. |
| `ops_monitoring_service.py` | monitoring ops | ops monitoring/tests | deplacer | `services/ops/monitoring_service.py` | imports migres. |
| `user_astro_profile_service.py` | astro profile utilisateur | users APIs/tests | deplacer | `services/user_profile/astro_profile_service.py` | imports / patch targets migres. |
| `user_birth_profile_service.py` | profil naissance utilisateur | users/natal/chat/guidance/tests | deplacer | `services/user_profile/birth_profile_service.py` | imports / patch targets migres. |
| `user_natal_chart_service.py` | theme natal utilisateur | users/natal/chat/guidance/tests | deplacer | `services/user_profile/natal_chart_service.py` | imports / patch targets migres. |
| `user_prediction_baseline_service.py` | baseline prediction utilisateur | jobs/tests prediction | deplacer | `services/user_profile/prediction_baseline_service.py` | imports migres. |
| `b2b_api_entitlement_gate.py` | gate API B2B | routers b2b/tests | deplacer | `services/b2b/api_entitlement_gate.py` | imports migres. |
| `b2b_astrology_service.py` | astrologie B2B | router b2b astrology/tests | deplacer | `services/b2b/astrology_service.py` | imports migres. |
| `b2b_audit_service.py` | audit B2B | routes/tests b2b | deplacer | `services/b2b/audit_service.py` | imports migres. |
| `b2b_billing_service.py` | billing B2B | route reconciliation/tests | deplacer | `services/b2b/billing_service.py` | imports migres. |
| `b2b_canonical_plan_resolver.py` | plan resolver B2B | entitlement/runtime/tests | deplacer | `services/b2b/canonical_plan_resolver.py` | imports migres. |
| `b2b_canonical_usage_service.py` | usage summary B2B | router usage/tests | deplacer | `services/b2b/canonical_usage_service.py` | imports migres. |
| `b2b_editorial_service.py` | editorial config B2B | route astrology/editorial/tests | deplacer | `services/b2b/editorial_service.py` | imports migres. |
| `b2b_entitlement_repair_service.py` | repair entitlement B2B | route repair/tests | deplacer | `services/b2b/entitlement_repair_service.py` | imports migres. |
| `b2b_reconciliation_service.py` | reconciliation B2B | router reconciliation/tests | deplacer | `services/b2b/reconciliation_service.py` | imports migres. |
| `enterprise_credentials_service.py` | credentials entreprise | deps b2b, APIs/tests | deplacer | `services/b2b/enterprise_credentials_service.py` | imports migres. |
| `enterprise_quota_usage_service.py` | quotas entreprise | entitlement b2b/tests | deplacer | `services/b2b/enterprise_quota_usage_service.py` | imports migres. |

## Fichier de test legacy supprime du runtime nominal

| Ancien chemin | Responsabilite | Decision | Cible | Justification |
| --- | --- | --- | --- | --- |
| `services/tests/__init__.py` | doublon metier natal legacy | supprimer du runtime + deplacer hors package applicatif | `backend/app/tests/unit/legacy_services/legacy_natal_interpretation_service.py` | AC4 : plus aucun package `tests` importable sous `app.services`. |
| `services/tests/conftest.py` | support tests legacy | deplacer | `backend/app/tests/unit/legacy_services/conftest.py` | hors runtime de production. |
| `services/tests/test_ai_engine_adapter_refacto.py` | test legacy | deplacer | `backend/app/tests/unit/legacy_services/test_ai_engine_adapter_refacto.py` | hors runtime. |
| `services/tests/test_natal_interpretation_service_v2_refacto.py` | test legacy | deplacer | `backend/app/tests/unit/legacy_services/test_natal_interpretation_service_v2_refacto.py` | hors runtime. |

## Denylist structurelle

- anciens chemins plats supprimes : `billing_service.py`, `consultation_*`, `natal_*`, `prediction_*`, `daily_prediction_service.py`, `daily_prediction_types.py`, `disclaimer_registry.py`, `email_*`, `quota_*`, `chart_*`, `current_context.py`, `persona_config_service.py`, `feature_flag_service.py`, `cross_tool_report.py`, `b2b_*`, `enterprise_*`, `audit_service.py`, `incident_service.py`, `ops_monitoring_service.py`, `user_*`, `stripe_*`, `pricing_experiment_service.py`, `astro_context_builder.py`
- package interdit : `backend/app/services/tests/`
- suffixes canoniques interdits dans `app.services` : `_legacy`, `_old`, `_tmp`, `_refacto`, `_new`, `_v2`
- imports interdits depuis `app.services` : `scripts.*`, `scripts/`, reexports metier via `services/__init__.py`

## Recherches negatives executees

- `rg -n "app\.services\.(astro_context_builder|audit_service|...|user_prediction_baseline_service)" backend`
- `rg -n "app\.services\.(email_service|email_provider|quota_usage_service|quota_window_resolver|chart_result_service|chart_json_builder|daily_prediction_types)\b" backend`
- `rg -n "app\.services\.(current_context|persona_config_service|feature_flag_service|daily_prediction_service|cross_tool_report)\b" backend scripts`
- `rg -n "app\.services\.(disclaimer_registry|resources\.templates\.disclaimer_registry)\b" backend scripts`
- `rg -n "app\.services\.tests|backend/app/services/tests|services/tests" backend`
- `rg -n "scripts\.|scripts/" backend/app/services`

## Garde-fous relies a la cartographie

- `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py`
- `backend/app/tests/unit/test_story_70_23_services_structure_guard.py`
