# Audit des constantes API

## Périmètre

Audit AC14/AC19 sur `backend/app/api` après centralisation des constantes partagées.

## Constantes centralisées

| Constante | Ancien emplacement actif | Propriétaire canonique | Consommateurs |
|---|---|---|---|
| `ADMIN_MANUAL_*` | routeurs et logique admin LLM | `backend/app/api/v1/constants.py` | main, routeur admin LLM, logique admin LLM, tests |
| `VALID_VIEWS`, `MAX_PAGE_SIZE`, `DEFAULT_DRILLDOWN_LIMIT` | consommation LLM admin | `backend/app/api/v1/constants.py` | routeur, logique, schémas consommation |
| `LOCALE_PATTERN`, `BLOCKED_CATEGORIES` | sample payloads admin LLM | `backend/app/api/v1/constants.py` | logique et schémas sample payloads |
| `PDF_TEMPLATE_CONFIG_DOC` | schémas/templates PDF | `backend/app/api/v1/constants.py` | schémas PDF |
| `CHAT_TEMPORARY_UNAVAILABLE_MESSAGE` | routeur chat public | `backend/app/api/v1/constants.py` | routeur et schéma chat |
| `VALID_ASTROLOGER_PROFILES` | utilisateurs publics | `backend/app/api/v1/constants.py` | routeur et schéma users |
| `VALID_RESOLUTION_SOURCES` | audit entitlements ops B2B | `backend/app/api/v1/constants.py` | routeur et schéma ops B2B |
| `DEFAULT_CONFIG_TEXTS`, `DEFAULT_EDITORIAL_TEMPLATES`, `CALIBRATION_RULE_DESCRIPTIONS` | content admin routeur/logique/schéma | `backend/app/api/v1/constants.py` | routeur, logique et schéma content |
| `FEATURES_TO_QUERY` | entitlements public routeur/logique | `backend/app/api/v1/constants.py` | routeur et logique entitlements |
| `CONSULTATION_TYPE_ALIASES` | schéma consultation public | `backend/app/api/v1/constants.py` | normalisation consultation |
| `LEGACY_USE_CASE_KEYS_REMOVED` | admin LLM routeur/logique/schéma | `backend/app/api/v1/constants.py` | routeur, logique, schéma admin LLM |

## Garde

`backend/app/tests/unit/test_api_router_architecture.py` vérifie que les constantes suivies ne sont plus redéfinies dans `routers`, `router_logic` ou `schemas`.

## Scan final attendu

`rg -n "^[A-Z][A-Z0-9_]+\\s*[:=]" app/api --glob "*.py"` ne doit plus remonter de constantes API suivies hors `app/api/v1/constants.py`.
