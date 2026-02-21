# Story 1.1: Set up initial project from starter template

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product engineer,  
I want initialiser le monorepo depuis le starter template retenu (FastAPI backend + React/Vite frontend),  
so that l equipe dispose d une base executable et standardisee pour developper le moteur astrologique.

## Acceptance Criteria

1. Given un repository vide ou non initialise, when le starter template est applique avec dependances installees, then les applications backend et frontend demarrent localement.
2. La structure backend en couches `api/core/domain/services/infra` est en place et exploitable pour les stories suivantes.
3. La structure frontend React/Vite TypeScript est en place avec dossiers de base (`api`, `state`, `components`, `pages`, `utils`).
4. La base de configuration projet inclut fichiers `.env.example`, orchestration Docker Compose, et conventions minimales de qualite (tests/lint) documentees.

## Tasks / Subtasks

- [x] Initialiser le monorepo et la structure racine
  - [x] Creer/valider `backend/`, `frontend/`, `shared/` (optionnel), `.env.example`, `docker-compose.yml`
  - [x] Verifier que la structure cible correspond a l architecture
- [x] Initialiser le backend FastAPI (Python 3.13)
  - [x] Initialiser projet backend avec dependances de base FastAPI
  - [x] Poser l arborescence `app/api`, `app/core`, `app/domain`, `app/services`, `app/infra`, `app/tests`
  - [x] Ajouter point d entree app (`main.py`) et endpoint de healthcheck minimal
- [x] Initialiser le frontend React + Vite + TypeScript
  - [x] Creer app Vite React TS
  - [x] Poser arborescence `src/api`, `src/state`, `src/components`, `src/pages`, `src/utils`, `src/tests`
  - [x] Ajouter shell applicatif minimal demarrable
- [x] Preparer les fondations outillage/dev
  - [x] Backend: config lint/test de base (ruff/pytest) sans sur-engineering
  - [x] Frontend: config lint/test de base (eslint/vitest) selon stack retenue
  - [x] Verifier execution locale des deux apps
- [x] Preparer les points d extension stories suivantes
  - [x] Backend: placeholders propres pour auth, db, redis, rate-limit, observabilite
  - [x] Frontend: placeholders client API central et providers d etat

## Dev Notes

- Respecter strictement la stack imposee:
  - Backend Python 3.13
  - Frontend React (TypeScript recommande)
- Starter valide par architecture: split starter (`backend` FastAPI + `frontend` Vite React TS).
- Cette story pose le socle; ne pas implementer la logique metier astrologique ici.
- Eviter toute table DB "massive upfront": seulement le minimum necessaire au boot.
- Garder les conventions d erreurs/API et organisation de dossiers alignees des maintenant.

### Technical Requirements

- Backend:
  - FastAPI en point d entree
  - Arborescence en couches: `api/core/domain/services/infra`
  - Project runtime compatible Docker Compose single host
- Frontend:
  - React + Vite + TypeScript
  - Base prete pour TanStack Query + Zustand + RHF + Zod dans stories ulterieures
- Infra:
  - `docker-compose.yml` present et coherent avec future integration PostgreSQL + Redis
- Security baseline:
  - `.env.example` present, pas de secrets hardcodes

### Architecture Compliance

- Conformite au document architecture:
  - Starter: "Split Starter (FastAPI backend + Vite React frontend)"
  - Organization backend: `api/core/domain/services/infra`
  - API style v1 et conventions de structure a prevoir des maintenant
  - Observabilite et securite vues comme concerns transverses

### Library / Framework Requirements

- Backend:
  - FastAPI (socle API)
  - Python 3.13
- Frontend:
  - React
  - Vite
  - TypeScript
- Design system alignment (terminologie):
  - UI custom leger avec Tailwind CSS + shadcn/ui + primitives Radix (implementation ulterieure)

### File Structure Requirements

- Racine:
  - `backend/`
  - `frontend/`
  - `shared/` (optionnel)
  - `.env.example`
  - `docker-compose.yml`
- Backend:
  - `backend/app/main.py`
  - `backend/app/api/`
  - `backend/app/core/`
  - `backend/app/domain/`
  - `backend/app/services/`
  - `backend/app/infra/`
  - `backend/app/tests/`
- Frontend:
  - `frontend/src/api/`
  - `frontend/src/state/`
  - `frontend/src/components/`
  - `frontend/src/pages/`
  - `frontend/src/utils/`
  - `frontend/src/tests/`

### Testing Requirements

- Backend:
  - Test minimal de demarrage app / endpoint health
  - Validation lint/format configuree pour execution locale
- Frontend:
  - Test minimal de rendu app shell
  - Validation lint configuree pour execution locale
- Critere de sortie story:
  - backend et frontend demarrent localement sans erreur bloquante

### Project Structure Notes

- Cette story est volontairement fondation.  
- Toute logique metier astro (calculs, ephemerides, versioning de regles) reste hors scope ici et commence en Story 1.2+.

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.1)
- PRD foundation phase: `_bmad-output/planning-artifacts/prd.md` (Phase 0 - Foundation, FR1-FR2)
- Architecture starter and structure: `_bmad-output/planning-artifacts/architecture.md` (Selected Starter, Project Organization, First Implementation Priority)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Create-story workflow execution
- Dev-story workflow execution
- Frontend checks: `npm run lint`, `npm run test`, `npm run build`
- Backend checks (venv active): `ruff check .`, `pytest -q`

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Monorepo split starter initialise (`backend/` FastAPI, `frontend/` React/Vite TypeScript).
- Healthcheck backend implemente et teste.
- Shell frontend minimal implemente et teste.
- Structure cible backend/frontend conforme aux conventions d architecture.
- Story finalisee et promue au statut `review`.
- Code review auto-fix applique: compose rendu plus deterministic, CORS de base ajoute, `frontend/.env.example` ajoute.
- Verification de demarrage reproductible ajoutee via `scripts/startup-smoke.ps1` (resultat: `startup_smoke_ok`).
- Story promue au statut `done` apres correction des findings High/Medium/Low.

### File List

- _bmad-output/implementation-artifacts/1-1-set-up-initial-project-from-starter-template.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- .env.example
- docker-compose.yml
- backend/pyproject.toml
- backend/.env.example
- backend/README.md
- backend/Dockerfile
- backend/app/main.py
- backend/app/api/health.py
- backend/app/core/security.py
- backend/app/core/rate_limit.py
- backend/app/infra/db/session.py
- backend/app/infra/cache/redis_client.py
- backend/app/infra/observability/metrics.py
- backend/app/tests/test_health.py
- backend/app/__init__.py
- backend/app/api/__init__.py
- backend/app/core/__init__.py
- backend/app/domain/__init__.py
- backend/app/services/__init__.py
- backend/app/infra/__init__.py
- backend/app/infra/db/__init__.py
- backend/app/infra/cache/__init__.py
- backend/app/infra/observability/__init__.py
- backend/app/tests/__init__.py
- frontend/package.json
- frontend/.env.example
- frontend/vite.config.ts
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/state/providers.ts
- frontend/src/components/AppShell.tsx
- frontend/src/pages/HomePage.tsx
- frontend/src/utils/noop.ts
- frontend/src/tests/App.test.tsx
- frontend/src/tests/setup.ts
- scripts/startup-smoke.ps1

### Change Log

- 2026-02-18: Story 1.1 implementee, tests/lint/build passes, statut passe a review.
- 2026-02-18: Code review findings corriges automatiquement (High/Medium/Low), statut passe a done.
