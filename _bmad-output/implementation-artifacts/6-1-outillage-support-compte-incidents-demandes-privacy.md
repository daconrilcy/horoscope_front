# Story 6.1: Outillage support (compte, incidents, demandes privacy)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a support user,  
I want acceder au contexte compte et gerer incidents/demandes RGPD,  
so that je peux resoudre les demandes client efficacement.

## Acceptance Criteria

1. Given un agent support autorise, when il consulte un dossier utilisateur, then il voit les informations necessaires (compte, abonnement, demandes privacy).
2. Given un agent support autorise, when il cree, met a jour ou clot un incident (compte, abonnement, contenu), then l incident est persiste avec statut, priorite et horodatage.
3. Given une action support sensible, when elle est executee, then l action est soumise au RBAC et journalisee avec un audit consultable (`request_id`, acteur, action, cible, statut).
4. Given une demande RGPD existante, when le support suit son traitement, then le statut est visible et coherent avec le workflow privacy existant.

## Tasks / Subtasks

- [x] Definir le domaine incident support et son contrat API (AC: 2)
  - [x] Definir les statuts incidents MVP (`open`, `in_progress`, `resolved`, `closed`) et transitions autorisees
  - [x] Definir priorites minimales (`low`, `medium`, `high`) et regles de validation
  - [x] Definir le schema API v1 (creation, listing, detail, mise a jour) avec erreurs metier stables
- [x] Exposer le contexte compte support unifie (AC: 1, 4)
  - [x] Reutiliser/etendre l endpoint support existant de contexte utilisateur (profil + abonnement + RGPD)
  - [x] Ajouter pagination/filtres minimaux si necessaire pour incidents et demandes RGPD
  - [x] Garantir format de reponse standard `{data, meta}` et `request_id` systematique
- [x] Implementer la persistance et les services incidents (AC: 2)
  - [x] Ajouter modele DB incident + migration Alembic (index recherche support)
  - [x] Ajouter service metier dedie (`incident_service`) avec validations metier
  - [x] Integrer audit automatique des actions incident sensibles (create/update/close)
- [x] Appliquer securite et garde-fous operatoires (AC: 3)
  - [x] Restreindre endpoints support/incident aux roles `support` et `ops`
  - [x] Appliquer rate limiting global + par role/utilisateur
  - [x] Uniformiser les erreurs d autorisation (`insufficient_role`) et metier (`incident_not_found`, `incident_invalid_transition`)
- [x] Integrer le panneau support cote frontend (AC: 1, 2, 4)
  - [x] Ajouter client API dans `frontend/src/api/` pour incidents + contexte support
  - [x] Ajouter composant/page support avec etats `loading/error/empty`
  - [x] Afficher timeline minimale (incidents + demandes RGPD + derniers evenements d audit utiles)
- [x] Observabilite et qualite (AC: 2, 3)
  - [x] Ajouter logs structures (`request_id`, actor_role, incident_id, action, status)
  - [x] Ajouter metriques (`support_incidents_total`, `support_incidents_open`, `support_incidents_resolution_seconds`)
  - [x] Assurer correlation audit <-> incident sans fuite de donnees sensibles
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: transitions incident, validations, erreurs metier
  - [x] Integration tests backend: RBAC, CRUD incidents, consultation contexte support, audit
  - [x] Tests frontend: affichage contexte/support panel, actions incident, etats UX critiques
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 6 Story 6.1 (FR13, FR34), avec dependances directes sur les acquis Epic 5 (FR32/FR33).
- Cette story lance l epic support/ops: prioriser un socle simple et robuste (lecture contexte + gestion incidents MVP) avant dashboards avances (Story 6.2).
- Reutiliser les patterns deja presents dans le code:
  - routeurs FastAPI v1 (`/v1/...`), erreurs standardisees, enveloppe `{data, meta}`
  - `request_id` de bout en bout
  - RBAC `user/support/ops` via dependances auth
  - audit via `AuditService` et model `audit_events`

### Technical Requirements

- Le support doit acceder au dossier utilisateur sans elevating privilege hors `support|ops`.
- Les incidents doivent etre tracables (statut, priorite, timestamps, assignee optionnel, lien user).
- Le suivi RGPD doit reutiliser le workflow privacy existant (pas de duplication de logique RGPD).
- Les reponses API doivent rester versionnees (`/v1`) et coherentes avec les contrats existants.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Persistance PostgreSQL via SQLAlchemy + migrations Alembic.
- Limitation de debit via Redis (global + role/utilisateur selon endpoint).
- Logs structures + metriques + audit obligatoires sur actions support sensibles.
- UI React: client API central + TanStack Query (ou pattern deja en place), etats UX explicites.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Auth/Security: JWT access+refresh + RBAC minimal (`support`, `ops`).
- Frontend: React + TypeScript, TanStack Query, formulaires valides (pattern existant).
- Tests: Pytest (backend), Vitest + Testing Library (frontend).

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/v1/routers/users.py` (extension contexte support existant)
  - `backend/app/api/v1/routers/` (nouveau routeur incidents support si separation utile)
  - `backend/app/services/incident_service.py` (nouveau)
  - `backend/app/infra/db/models/` (modele incident)
  - `backend/migrations/versions/` (migration incidents)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/` (client support/incidents)
  - `frontend/src/components/` ou `frontend/src/pages/` (panel support)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - transitions incident et validations de priorite/statut
  - erreurs metier stables et codes attendus
- Integration:
  - acces interdit role `user`, autorise `support|ops`
  - parcours CRUD incident + lecture contexte compte/RGPD
  - verification des evenements d audit sur actions sensibles
- Frontend:
  - etats `loading/error/empty`
  - creation/mise a jour/cloture incident
  - affichage contexte compte + abonnements + demandes RGPD

### Git Intelligence Summary

- Commits recents majoritairement axes tests et robustesse; conserver le meme standard (tests d integration forts + deltas localises).
- Le code existant contient deja des briques reutilisables: `AuditService`, routeurs privacy/billing, RBAC et conventions d erreurs.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 6, Story 6.1)
- PRD: `_bmad-output/planning-artifacts/prd.md` (Journey Support/RGPD, FR13, FR34, FR32, FR33)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (JWT/RBAC, API v1, rate limiting Redis, observabilite)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (Journey RGPD, etats `loading/error/empty`, acces support)
- Code existant pertinent:
  - `backend/app/api/v1/routers/users.py`
  - `backend/app/api/v1/routers/privacy.py`
  - `backend/app/api/v1/routers/audit.py`
  - `backend/app/services/audit_service.py`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; ruff format backend`
- `.\.venv\Scripts\Activate.ps1; ruff check backend`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend`
- `npm run lint` (dans `frontend/`)
- `npm test -- --run` (dans `frontend/`)

### Completion Notes List

- Ajout du modele `SupportIncidentModel` + migration Alembic `20260219_0011_add_support_incidents.py`.
- Ajout du service `IncidentService` (creation/listing/mise a jour, transitions controlees, metriques incidents).
- Ajout du routeur `backend/app/api/v1/routers/support.py`:
  - `GET /v1/support/users/{user_id}/context`
  - `GET /v1/support/incidents`
  - `POST /v1/support/incidents`
  - `PATCH /v1/support/incidents/{incident_id}`
- RBAC `support|ops` + rate limiting global/role/user + erreurs standardisees.
- Audit des actions incidents via `AuditService` (`support_incident_create`, `support_incident_update`, `support_incident_close`).
- Ajout frontend:
  - client API `frontend/src/api/support.ts`
  - panel `frontend/src/components/SupportOpsPanel.tsx`
  - integration dans `frontend/src/App.tsx`
- Ajout tests:
  - backend unit `backend/app/tests/unit/test_incident_service.py`
  - backend integration `backend/app/tests/integration/test_support_api.py`
  - frontend `frontend/src/tests/SupportOpsPanel.test.tsx`
- Validation complete OK: `ruff check backend`, `pytest -q backend`, `npm run lint`, `npm test -- --run`.

### File List

- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/support.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/support_incident.py
- backend/app/main.py
- backend/app/services/incident_service.py
- backend/app/tests/integration/test_support_api.py
- backend/app/tests/unit/test_incident_service.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0011_add_support_incidents.py
- frontend/src/App.tsx
- frontend/src/api/support.ts
- frontend/src/components/SupportOpsPanel.tsx
- frontend/src/tests/SupportOpsPanel.test.tsx
- _bmad-output/implementation-artifacts/6-1-outillage-support-compte-incidents-demandes-privacy.md

### Change Log

- 2026-02-19: Implementation completee de la story 6.1 (backend support incidents + contexte compte + frontend panel support + tests).
- 2026-02-19: Corrections post code-review appliquees (detail incident, timeline audit, suivi RGPD detaille, suppression effet de bord billing, tests rate limit).

## Senior Developer Review (AI)

### Outcome

Approve

### Key Fixes Applied

- `HIGH` Endpoint detail incident ajoute: `GET /v1/support/incidents/{incident_id}`.
- `HIGH` Suivi RGPD rendu exploitable dans le panel support (liste des demandes + statuts).
- `HIGH` Timeline minimale completee avec evenements d audit recents dans le contexte support.
- `MEDIUM` Suppression de l effet de bord lecture abonnement dans contexte support (`get_subscription_status_readonly`).
- `MEDIUM` Couverture tests completee avec cas `429` support.
