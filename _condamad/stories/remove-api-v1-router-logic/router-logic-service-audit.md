# Audit du namespace `router_logic`

## Resume

- Inventaire source: 54 fichiers Python sous `backend/app/api/v1/router_logic`.
- Decision corrigee: supprimer le namespace legacy et sortir la logique non-route de `api/v1`.
- Destination canonique: services applicatifs sous `backend/app/services/**`, par domaine existant.
- Le package intermediaire `backend/app/api/v1/handlers/**` n'est pas conserve.
- Aucun package `services/router_logic`, alias, re-export ou shim de compatibilite n'a ete cree.

## Mapping complet

| Ancien fichier | Consommateur principal | Destination / decision |
|---|---|---|
| `router_logic/__init__.py` | package import | Supprime, aucun shim |
| `admin/__init__.py` | package import | Supprime, aucun shim |
| `admin/ai.py` | `routers/admin/ai.py` | `services/llm_observability/admin_ai.py` |
| `admin/audit.py` | `routers/admin/audit.py` | `services/ops/admin_audit.py` |
| `admin/content.py` | `routers/admin/content.py` | `services/ops/admin_content.py` |
| `admin/dashboard.py` | `routers/admin/dashboard.py` | `services/ops/admin_dashboard.py` |
| `admin/exports.py` | `routers/admin/exports.py` | `services/ops/admin_exports.py` |
| `admin/llm/__init__.py` | package import | Supprime, aucun shim |
| `admin/llm/assemblies.py` | routeur admin LLM | `services/llm_generation/admin_assemblies.py` |
| `admin/llm/consumption.py` | routeur admin LLM | `services/llm_observability/admin_consumption.py` |
| `admin/llm/manual_execution.py` | routeur admin LLM, tests | `services/llm_generation/admin_manual_execution.py` |
| `admin/llm/observability.py` | routeur admin LLM | `services/llm_observability/admin_observability.py` |
| `admin/llm/prompts.py` | routeur admin LLM, registre cleanup | `services/llm_generation/admin_prompts.py` |
| `admin/llm/release_snapshots.py` | routeur admin LLM | `services/llm_generation/admin_release_snapshots.py` |
| `admin/llm/releases.py` | routeur admin LLM | `services/llm_generation/admin_releases.py` |
| `admin/llm/sample_payloads.py` | routeur admin LLM | `services/llm_generation/admin_sample_payloads.py` |
| `admin/logs.py` | `routers/admin/logs.py` | `services/ops/admin_logs.py` |
| `admin/pdf_templates.py` | `routers/admin/pdf_templates.py` | `services/natal/admin_pdf_templates.py` |
| `admin/users.py` | `routers/admin/users.py` | `services/user_profile/admin_users.py` |
| `b2b/__init__.py` | package import | Supprime, aucun shim |
| `b2b/astrology.py` | routeur B2B astrology | `services/b2b/api_astrology.py` |
| `b2b/billing.py` | routeur B2B billing | `services/b2b/api_billing.py` |
| `b2b/credentials.py` | routeur B2B credentials | `services/b2b/api_credentials.py` |
| `b2b/editorial.py` | routeur B2B editorial | `services/b2b/api_editorial.py` |
| `b2b/usage.py` | routeur B2B usage, tests | `services/b2b/api_usage.py` |
| `internal/__init__.py` | package import | Supprime, aucun shim |
| `internal/llm/__init__.py` | package import | Supprime, aucun shim |
| `internal/llm/qa.py` | routeur QA interne | `services/llm_generation/internal_qa.py` |
| `ops/__init__.py` | package import | Supprime, aucun shim |
| `ops/b2b/__init__.py` | package import | Supprime, aucun shim |
| `ops/b2b/entitlement_repair.py` | routeur ops B2B repair | `services/b2b/ops_entitlement_repair_api.py` |
| `ops/b2b/entitlements_audit.py` | routeur ops B2B audit | `services/b2b/ops_entitlements_audit_api.py` |
| `ops/b2b/reconciliation.py` | routeur ops B2B reconciliation | `services/b2b/ops_reconciliation_api.py` |
| `ops/entitlement_mutation_audits.py` | routeurs ops entitlement, tests | `services/canonical_entitlement/audit/api_mutation_audits.py` |
| `ops/feature_flags.py` | routeur feature flags | `services/ops/api_feature_flags.py` |
| `ops/monitoring.py` | routeur monitoring | `services/ops/api_monitoring.py` |
| `ops/persona.py` | routeur persona | `services/ops/api_persona.py` |
| `public/__init__.py` | package import | Supprime, aucun shim |
| `public/astrologers.py` | routeur public astrologers | `services/user_profile/public_astrologers.py` |
| `public/astrology_engine.py` | routeur astrology engine | `services/chart/public_astrology_engine.py` |
| `public/audit.py` | routeur public audit, tests | `services/ops/public_audit.py` |
| `public/auth.py` | routeur auth, tests | `services/auth/public_support.py` |
| `public/billing.py` | routeur billing | `services/billing/public_billing.py` |
| `public/chat.py` | routeur chat | `services/llm_generation/chat/public_chat.py` |
| `public/consultations.py` | routeur consultations | `services/consultation/public_consultations.py` |
| `public/email.py` | routeur email | `services/email/public_email.py` |
| `public/entitlements.py` | routeur entitlements | `services/entitlement/public_entitlements.py` |
| `public/geocoding.py` | routeur geocoding | `services/geocoding/public_support.py` |
| `public/natal_interpretation.py` | routeur natal interpretation | `services/llm_generation/natal/public_interpretation.py` |
| `public/predictions.py` | routeur predictions, QA interne | `services/prediction/public_predictions.py` |
| `public/privacy.py` | routeur privacy, tests | `services/privacy/public_support.py` |
| `public/reference_data.py` | routeur reference data | `services/reference_data/public_support.py` |
| `public/support.py` | routeur support, tests | `services/ops/public_support.py` |
| `public/users.py` | routeur users | `services/user_profile/public_users.py` |

## Validation d'architecture

- `backend/app/api/v1/router_logic`: absent.
- `backend/app/api/v1/handlers`: absent.
- `app.api.v1.router_logic`: non importable.
- Aucun hit `app.api.v1.router_logic`, `api/v1/handlers` ou `app.api.v1.handlers` dans `backend/app`, `backend/tests` ou `backend/docs`.
- Les routeurs API v1 importent les services par domaine; les schemas et erreurs restent dans `backend/app/api/v1`.
