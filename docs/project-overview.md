# Project Overview

## Project
- Name: `horoscope_front`
- Repository type: monorepo (multi-part)
- Primary parts: `backend` (FastAPI, Python 3.13), `frontend` (React + Vite + TypeScript)

## Executive Summary
`horoscope_front` is a full-stack astrology product with:
- A FastAPI backend exposing versioned REST APIs under `/v1`.
- A React SPA frontend consuming centralized API clients.
- PostgreSQL/SQLite-compatible SQLAlchemy models with Alembic migrations.
- Security, privacy, billing, B2B, ops monitoring, and load/backup operational scripts.

## Technology Stack
| Category | Technology | Version/Notes |
|---|---|---|
| Backend runtime | Python | 3.13 (`backend/pyproject.toml`) |
| Backend framework | FastAPI + Uvicorn | `fastapi==0.129.0`, `uvicorn==0.41.0` |
| ORM & migrations | SQLAlchemy + Alembic | `sqlalchemy==2.0.44`, `alembic==1.16.5` |
| Auth | JWT (PyJWT) | access/refresh + RBAC |
| Frontend runtime | Node | Vite workflow |
| Frontend framework | React | `react@^19.2.0` |
| Frontend build | Vite + TypeScript | `vite@^7.3.1`, TS ~5.9 |
| Frontend data fetching | TanStack Query | `@tanstack/react-query` |
| Testing backend | Pytest | unit + integration |
| Testing frontend | Vitest + Testing Library | API/UI suites |
| DevOps scripts | PowerShell | quality gate, security, backup/restore, load test |

## Architecture Type
- Backend: layered API/service/infra architecture.
- Frontend: page + component architecture with central API client modules.
- Cross-part integration: HTTP/JSON over local dev endpoints (`localhost:5173` -> `localhost:8000`).

## Key Documentation
- [Architecture - Backend](./architecture-backend.md)
- [Architecture - Frontend](./architecture-frontend.md)
- [Integration Architecture](./integration-architecture.md)
- [API Contracts - Backend](./api-contracts-backend.md)
- [Data Models - Backend](./data-models-backend.md)
- [Development Guide - Backend](./development-guide-backend.md)
- [Development Guide - Frontend](./development-guide-frontend.md)
- [Component Inventory - Frontend](./component-inventory-frontend.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Deployment Guide](./deployment-guide.md)
