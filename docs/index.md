# Project Documentation Index

## Project Overview
- **Type:** monorepo with 2 parts
- **Primary Languages:** Python (backend), TypeScript (frontend)
- **Architecture:** backend layered services + frontend SPA + HTTP integration

## Quick Reference

### Backend
- **Type:** backend service
- **Stack:** FastAPI, SQLAlchemy, Alembic, JWT
- **Root:** `backend/`

### Frontend
- **Type:** web SPA
- **Stack:** React, Vite, TypeScript, TanStack Query
- **Root:** `frontend/`

## Generated Documentation
- [Project Overview](./project-overview.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Architecture - Backend](./architecture-backend.md)
- [Architecture - Frontend](./architecture-frontend.md)
- [Integration Architecture](./integration-architecture.md)
- [API Contracts - Backend](./api-contracts-backend.md)
- [Data Models - Backend](./data-models-backend.md)
- [Component Inventory - Frontend](./component-inventory-frontend.md)
- [Development Guide - Backend](./development-guide-backend.md)
- [Development Guide - Frontend](./development-guide-frontend.md)
- [Deployment Guide](./deployment-guide.md)
- [Project Parts Metadata](./project-parts.json)

## Existing Documentation
- [Persona Governance](./persona-governance.md)
- [Pricing Experiment Rollback](./pricing-experiment-rollback.md)
- [Astro Research - README](./recherches%20astro/README.md)
- [Astro Deep Research Report](./recherches%20astro/deep-research-report.md)

## Getting Started
1. Commencer par [Project Overview](./project-overview.md).
2. Lire [Architecture - Backend](./architecture-backend.md) et [Architecture - Frontend](./architecture-frontend.md).
3. Utiliser [API Contracts - Backend](./api-contracts-backend.md) + [Data Models - Backend](./data-models-backend.md) pour toute extension fonctionnelle.
4. Pour les workflows opérationnels, suivre [Deployment Guide](./deployment-guide.md).

## Usage AI / Brownfield
Pour un nouveau cycle de planification brownfield (PRD/architecture), donne en entrée ce fichier:
- `docs/index.md`
