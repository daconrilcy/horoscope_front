# Source Tree Analysis

## High-Level Structure

```text
horoscope_front/
├── backend/                      # FastAPI application, domain/services/infra, tests, migrations
│   ├── app/
│   │   ├── api/                  # Routers and API dependencies
│   │   ├── core/                 # Config, security, rate limiting, request id
│   │   ├── infra/                # DB models/repos, llm, observability, cache
│   │   ├── services/             # Business use-cases
│   │   └── tests/                # Unit + integration tests
│   ├── migrations/               # Alembic migrations
│   ├── pyproject.toml            # Python package + deps
│   └── README.md                 # Backend runbook
├── frontend/                     # React/Vite app, API clients, pages, UI panels, tests
│   ├── src/
│   │   ├── api/                  # Centralized API client modules
│   │   ├── components/           # Functional feature panels
│   │   ├── pages/                # Route-level pages
│   │   ├── state/                # Providers and app-level state plumbing
│   │   └── tests/                # Vitest suites
│   └── package.json              # Frontend scripts and deps
├── scripts/                      # Ops scripts: quality, security, backup/restore, load tests
├── docs/                         # Knowledge and runbooks
├── _bmad/                        # BMAD method assets/workflows
├── _bmad-output/                 # BMAD generated planning/implementation artifacts
└── docker-compose.yml            # Local multi-service orchestration
```

## Critical Entry Points
- Backend application: `backend/app/main.py`
- Backend API routers: `backend/app/api/v1/routers/*.py`
- Frontend bootstrap: `frontend/src/main.tsx`
- Frontend app shell/routing: `frontend/src/App.tsx`

## Integration Paths
- Frontend API modules in `frontend/src/api/` call backend `/v1/*` endpoints.
- Ops and platform workflows rely on scripts in `scripts/`.
- Data lifecycle is managed through SQLAlchemy models + Alembic migrations.

## Test Topology
- Backend unit tests: `backend/app/tests/unit/`
- Backend integration tests: `backend/app/tests/integration/`
- Frontend tests: `frontend/src/tests/`

## Configuration Surface
- Root env template: `.env.example`
- Backend config: `backend/app/core/config.py`
- Compose orchestration: `docker-compose.yml`
- Migration config: `backend/alembic.ini`
