# Story 2.4: Restitution lisible du theme natal

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want consulter un theme natal clair et structure,  
so that je peux comprendre facilement mes informations astrologiques.

## Acceptance Criteria

1. Given un theme natal genere, when l utilisateur ouvre la vue de restitution, then les sections sont presentees de facon lisible et coherente.
2. Les etats `loading/error/empty` sont geres explicitement.

## Tasks / Subtasks

- [x] Exposer une API de lecture du dernier theme natal utilisateur (AC: 1, 2)
  - [x] Ajouter un endpoint securise `GET /v1/users/me/natal-chart/latest`
  - [x] Recuperer le dernier `chart_result` associe a l utilisateur authentifie
  - [x] Retourner une structure stable: `chart_id`, `result`, `metadata`, `created_at`
- [x] Etendre la tracabilite pour relier resultat et utilisateur (AC: 1)
  - [x] Ajouter `user_id` dans la persistence `chart_results` (model + migration + repository)
  - [x] Adapter la generation (Story 2.3) pour persister `user_id`
  - [x] Ajouter acces repository `get_latest_by_user_id`
- [x] Construire la page React de restitution du theme natal (AC: 1, 2)
  - [x] Ajouter client API frontend centralise pour `GET /v1/users/me/natal-chart/latest`
  - [x] Ajouter hook TanStack Query dedie (`useLatestNatalChart`)
  - [x] Creer page/composants lisibles: resume, positions planetaires, maisons, aspects, metadonnees de version
- [x] Gerer explicitement tous les etats UX critiques (AC: 2)
  - [x] `loading`: skeleton/placeholder clair
  - [x] `error`: message actionnable + option de retry
  - [x] `empty`: aucun theme genere, CTA vers generation initiale
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests backend unitaires/integration pour endpoint latest
  - [x] Tests frontend composants/hook pour `loading/error/empty/success`
  - [x] Validation finale:
    - [x] backend: `ruff check .` + `pytest -q`
    - [x] frontend: `npm run test` + `npm run build`

## Dev Notes

- Story full-stack (backend + frontend).
- Le theme natal initial est deja genere par la Story 2.3 via `POST /v1/users/me/natal-chart`.
- Cette story ajoute la restitution lisible et reutilisable des donnees deja calculees.

### Technical Requirements

- API versionnee `/v1` et securisee JWT.
- Format de reponse unifie (`data/meta`) et erreurs normalisees (`error.code`, `message`, `details`, `request_id`).
- Frontend React + TypeScript avec:
  - server state via TanStack Query
  - etats `loading/error/empty` explicites

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct depuis router.
- Pas de logique metier astro dans composants UI.
- Cote frontend: API dans `src/api`, pages dans `src/pages`, composants dans `src/components`.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic.
- Frontend: React (obligatoire), TanStack Query, Zustand (si UI state necessaire), Vitest + Testing Library.

### File Structure Requirements

- Cibles backend recommandees:
  - `backend/app/infra/db/models/chart_result.py`
  - `backend/app/infra/db/repositories/chart_result_repository.py`
  - `backend/app/services/user_natal_chart_service.py`
  - `backend/app/api/v1/routers/users.py`
  - `backend/migrations/versions/*_add_user_id_to_chart_results.py`
- Cibles frontend recommandees:
  - `frontend/src/api/natalChart.ts`
  - `frontend/src/pages/NatalChartPage.tsx`
  - `frontend/src/components/natal/*`
  - `frontend/src/tests/*natal-chart*`

### Testing Requirements

- Backend integration:
  - `GET /v1/users/me/natal-chart/latest` sans token => `401`
  - utilisateur avec chart => `200`
  - utilisateur sans chart => `404` (`natal_chart_not_found`)
- Frontend:
  - rendu loading
  - rendu error
  - rendu empty
  - rendu success structure avec sections lisibles
- Validation finale:
  - backend: `ruff check .`, `pytest -q`
  - frontend: `npm run test`, `npm run build`

### Previous Story Intelligence

- Story 2.1: base auth JWT + RBAC.
- Story 2.2: profil natal utilisateur.
- Story 2.3: generation initiale + tracabilite (`chart_id`, versions, erreurs timeout/unavailable).
- Reutiliser les conventions d erreurs et l enveloppe API deja en place.

### Git Intelligence Summary

- Le backend suit deja un pattern stable de router mince + service orchestration.
- Le frontend existe en structure React/Vite; cette story doit conserver separation `api/components/pages/state`.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.4)
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md`
- Story precedente:
  - `_bmad-output/implementation-artifacts/2-3-generation-du-theme-natal-initial.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution for Story 2.4
- backend: `ruff check .`, `pytest -q`
- frontend: `npm run lint`, `npm run test`, `npm run build`

### Completion Notes List

- Added `chart_results.user_id` traceability (model/repository/service + migration `20260218_0005`).
- Added authenticated API `GET /v1/users/me/natal-chart/latest`.
- Updated natal generation flow to persist `user_id` in chart traces.
- Added frontend API client + TanStack Query hook for latest natal chart.
- Added React restitution page with explicit `loading/error/empty/success` states.
- Added backend and frontend automated tests for latest chart retrieval and UI states.
- Fixed TypeScript strict build blockers: type-only imports for B2B types and UUID-shaped test IDs in billing tests.
- Re-validated frontend quality gates: `npm run test -- --run` and `npm run build` passing.

### File List

- _bmad-output/implementation-artifacts/2-4-restitution-lisible-du-theme-natal.md
- backend/app/infra/db/models/chart_result.py
- backend/app/infra/db/repositories/chart_result_repository.py
- backend/app/services/chart_result_service.py
- backend/app/services/user_natal_chart_service.py
- backend/app/api/v1/routers/users.py
- backend/migrations/versions/20260218_0005_add_user_id_to_chart_results.py
- backend/app/tests/integration/test_user_natal_chart_api.py
- backend/app/tests/unit/test_user_natal_chart_service.py
- frontend/package.json
- frontend/src/main.tsx
- frontend/src/state/providers.tsx
- frontend/src/api/natalChart.ts
- frontend/src/pages/NatalChartPage.tsx
- frontend/src/components/B2BBillingPanel.tsx
- frontend/src/components/B2BEditorialPanel.tsx
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/index.css
- frontend/src/tests/App.test.tsx
- frontend/src/tests/NatalChartPage.test.tsx
- frontend/src/tests/BillingPanel.test.tsx
