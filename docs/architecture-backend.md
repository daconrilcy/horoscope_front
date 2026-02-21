# Architecture - Backend

## Scope
Part: `backend`
Project type: `backend`

## Runtime and Framework
- Python 3.13
- FastAPI application with router composition under `/v1`
- Uvicorn ASGI runtime

## Layered Structure
- `app/api/`: request/response layer (routers, dependency guards, error envelopes)
- `app/core/`: cross-cutting concerns (config, RBAC, auth helpers, rate limit, request IDs)
- `app/services/`: business rules and use-case orchestration
- `app/infra/`: persistence models/repositories and external integration helpers

## Data Architecture
- SQLAlchemy models in `app/infra/db/models/`
- Migrations in `backend/migrations/versions/`
- Alembic controlled schema evolution
- Runtime DB URL configured by environment (SQLite local, PostgreSQL supported)

## API Surface
Primary router groups:
- Auth: `/v1/auth`
- Users/Natal: `/v1/users`, `/v1/astrology-engine`
- Chat/Guidance: `/v1/chat`, `/v1/guidance`, `/v1/chat/modules`
- Billing/B2B: `/v1/billing`, `/v1/b2b/*`
- Privacy/Audit/Ops/Support: `/v1/privacy`, `/v1/audit`, `/v1/ops/*`, `/v1/support`

## Security & Governance
- JWT-based auth flows
- Role-based restrictions (`user`, `support`, `ops`, `enterprise_admin`)
- Sensitive action audit events
- Privacy workflows (export/delete)
- Rate limiting in core middleware/helpers

## Observability
- Metrics counters/durations in `app/infra/observability/metrics.py`
- Ops monitoring endpoints summarize latency/error/quota/relevance indicators
- Pricing experimentation instrumentation and operational KPI aggregation available

## Quality Strategy
- Unit + integration tests under `backend/app/tests/`
- Quality scripts: `scripts/quality-gate.ps1`, `scripts/predeploy-check.ps1`
- Security scripts: `scripts/scan-secrets.ps1`, `scripts/security-verification.ps1`
