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
