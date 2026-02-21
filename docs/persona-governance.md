# Gouvernance Persona (Ops)

Ce document cadre la gestion des profils persona astrologue introduits par la story 11.1.

## Conventions de creation

- `profile_code`: format slug `^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$`.
- `display_name`: non vide, lisible par les equipes ops/support.
- Parametres obligatoires:
  - `tone`: `calm | direct | empathetic`
  - `prudence_level`: `standard | high`
  - `scope_policy`: `strict | balanced`
  - `response_style`: `concise | detailed`
  - `fallback_policy`: `safe_fallback | retry_once_then_safe`

## Cycle de vie profil

- `create_profile`: cree un profil en `inactive` par defaut.
- `activate_profile`: active le profil cible et desactive l'ancien actif.
- `archive_profile`: interdit sur un profil actif.
- `restore_profile`: repasse un profil archive en `inactive`.
- `rollback_active`: revient au profil precedent via `rollback_from_id` si disponible.

## Garde-fous operationnels

- RBAC: endpoints ops persona accessibles uniquement au role `ops`.
- Rate limiting dedie (`ops_persona:*`) sur lecture et mutations.
- Audit systematique des actions:
  - `ops_persona_create`
  - `ops_persona_update`
  - `ops_persona_activate`
  - `ops_persona_archive`
  - `ops_persona_restore`
  - `ops_persona_rollback`

## KPI de pilotage par persona

- Endpoint ops:
  - `GET /v1/ops/monitoring/persona-kpis?window=1h|24h|7d`
- Metriques suivies par `persona_profile`:
  - `messages_total`
  - `guidance_messages_total`
  - `llm_error_count`
  - `llm_error_rate`
  - `p95_latency_ms`

## Decision produit (cadre)

- Continuer un persona si:
  - `llm_error_rate` stable ou en baisse,
  - `p95_latency_ms` sans regression notable,
  - volume d'usage significatif.
- Revenir en arriere rapidement si:
  - hausse brutale des erreurs LLM,
  - degradation latence,
  - signaux qualitatifs ops/support negatifs.
