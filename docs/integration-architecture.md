# Integration Architecture

## Parts
- `frontend` (web SPA)
- `backend` (REST API)

## Integration Style
- Synchronous HTTP/JSON integration
- Frontend domain clients call backend domain routers under `/v1`

## Principal Flows
1. Auth flow:
   - Frontend -> `/v1/auth/register|login|refresh`
   - Token storage/use for subsequent API calls
2. Astrology/user flow:
   - Birth data updates -> natal chart generation/read
3. Conversation flow:
   - Chat message send/list/history + guidance endpoints
4. Commercial flow:
   - Billing checkout/retry/plan-change/quota/subscription
5. Compliance/ops flow:
   - Privacy export/delete, audit listing, ops monitoring, support incidents
6. B2B flow:
   - API key based access for enterprise astrology/editorial/usage/billing/reconciliation

## Cross-Cutting Integration Concerns
- Unified error envelope (`error.code`, `message`, `details`, `request_id`)
- Request correlation IDs for observability
- Rate limiting and auth checks at backend edge
- Security and privacy controls embedded into backend services

## Deployment Coupling
- `docker-compose.yml` defines local backend + frontend runtime dependencies
- Backend healthcheck gates frontend dependency in compose mode
