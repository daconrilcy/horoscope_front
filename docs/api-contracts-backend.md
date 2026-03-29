# API Contracts - Backend

## Base
- Versioned REST base: `/v1`
- Content type: JSON
- Error envelope shape:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "request_id": "string"
  }
}
```

## Router Groups
- `/v1/auth` - register/login/refresh/me
- `/v1/users` - profile/birth data/natal chart user endpoints
- `/v1/astrology-engine` - engine operations and deterministic traceability helpers
- `/v1/chat` and `/v1/chat/modules` - messaging and module interactions
- `/v1/guidance` - guidance generation endpoints
- `/v1/billing` - checkout/retry/plan/quota/subscription
- `/v1/privacy` - export/delete and status workflows
- `/v1/audit` - audit listing/query
- `/v1/support` - support incident APIs
- `/v1/ops/*` - monitoring, persona, feature-flag and operational endpoints
- `/v1/b2b/*` - enterprise credentials, astrology, editorial, usage, billing, reconciliation
- `/v1/reference-data` - reference data admin/clone/seed actions

## Auth Modes
- Bearer JWT for user/support/ops/admin routes
- API key header (`X-API-Key`) for B2B enterprise routes

## Contract Source of Truth
- FastAPI OpenAPI schema generated from router definitions and Pydantic models.
- Endpoint decorators located in `backend/app/api/v1/routers/`.

## `/v1/entitlements/me` - Plan Commercial et Droits Effectifs
- Fournit un état complet et consolidé des droits d'accès de l'utilisateur.
- Champs principaux au top-level : `plan_code`, `billing_status`.
- Liste des `features` avec pour chacune :
  - `granted` (bool) : accès autorisé ou non.
  - `reason_code` (str) : motif de l'autorisation ou du refus (`granted`, `feature_not_in_plan`, `billing_inactive`, `quota_exhausted`, `binding_disabled`, `subject_not_eligible`).
  - `quota_remaining`, `quota_limit` : état du quota si applicable.
  - `access_mode` : mode d'accès (`quota`, `unlimited`, `disabled`).
- Suffisance frontend : permet de piloter l'affichage des CTAs et des messages d'upgrade sans appel supplémentaire.

## `/v1/astrology-engine/natal/prepare` - DST Local Time Errors
- Ambiguous local time during DST fold returns `422` with `error.code = ambiguous_local_time`.
- Non-existent local time during DST gap returns `422` with `error.code = nonexistent_local_time`.
- Error details include:
  - `timezone` (IANA timezone used for conversion)
  - `local_datetime` (local date-time rejected)
  - `candidate_offsets` (list of possible UTC offsets for ambiguous times)
  - `resolution_hint` (actionable fallback guidance)
