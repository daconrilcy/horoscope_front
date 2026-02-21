# Story 5.1: Export et suppression des donnees personnelles

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want exporter et supprimer mes donnees facilement,  
so that je garde le controle de mes informations.

## Acceptance Criteria

1. Given un utilisateur authentifie, when il demande un export de ses donnees, then la demande est traitee via un workflow tracable et il peut recuperer un export coherent de ses donnees personnelles.
2. Given un utilisateur authentifie, when il demande la suppression de ses donnees/compte, then la suppression est executee via un workflow tracable avec confirmation explicite de traitement.
3. Given une demande d export/suppression en echec ou invalide, when le systeme repond, then l API retourne une erreur metier stable et actionnable avec `request_id`.

## Tasks / Subtasks

- [x] Definir le workflow RGPD export/suppression MVP (AC: 1, 2, 3)
  - [x] Definir les etats de traitement (`requested`, `processing`, `completed`, `failed`) et transitions autorisees
  - [x] Definir la granularite des donnees exportees (profil, natal, billing, chat, historiques utiles)
  - [x] Definir le contrat de suppression (hard delete/soft delete cible MVP, confirmation et tracabilite)
- [x] Etendre le modele de donnees privacy et audit (AC: 1, 2)
  - [x] Ajouter modele(s) de demandes RGPD (type demande, statut, timestamps, error_reason)
  - [x] Ajouter migration Alembic associee avec index/contraintes necessaires
  - [x] Prevoir trace d audit liee aux actions sensibles (demande, execution, completion)
- [x] Implementer service backend privacy (AC: 1, 2, 3)
  - [x] Ajouter service dedie (`request_export`, `get_export_status`, `request_deletion`, `get_deletion_status`)
  - [x] Garantir idempotence des requetes repetes et transitions d etat coherentes
  - [x] Encadrer erreurs metier stables (`privacy_request_invalid`, `privacy_request_conflict`, `privacy_not_found`, etc.)
- [x] Exposer API REST v1 privacy (AC: 1, 2, 3)
  - [x] Ajouter endpoints dedies sous `/v1/privacy/*` (ou equivalent coherent) avec enveloppes `{data, meta}` / `{error:{...}}`
  - [x] Proteger via JWT + RBAC `user` (support/ops hors scope execution user self-service)
  - [x] Appliquer rate limiting global + user + user/plan
- [x] Integrer parcours frontend export/suppression (AC: 1, 2, 3)
  - [x] Ajouter client API privacy dans `frontend/src/api/`
  - [x] Ajouter UI compte/confidentialite avec actions export/suppression + etats `loading/error/empty`
  - [x] Ajouter confirmations explicites et feedback de statut de traitement
- [x] Ajouter observabilite et audit minimaux (AC: 1, 2, 3)
  - [x] Journaliser demandes RGPD avec `request_id`, user_id, type, statut
  - [x] Ajouter metriques minimales (`privacy_export_requests_total`, `privacy_delete_requests_total`, `privacy_request_failures_total`)
  - [x] Verifier tracabilite des actions sensibles pour support/ops
- [x] Tester et valider la story (AC: 1, 2, 3)
  - [x] Unit tests backend: transitions etats, idempotence, erreurs metier
  - [x] Integration tests API: auth 401/403, export/suppression succes, conflits, erreurs metier
  - [x] Tests frontend: parcours export/suppression, confirmations, etats `loading/error/empty`
  - [x] Validation finale: `ruff check .` + `pytest -q` + tests frontend

## Dev Notes

- Story source: Epic 5 Story 5.1 (FR29, FR30) demarre le volet Privacy/RGPD.
- Reutiliser strictement les patterns etablis sur billing/chat:
  - `request_id` systematique
  - RBAC explicite
  - rate limiting global + user + user/plan
  - enveloppes API standardisees
- Cette story traite le self-service user; le suivi support/ops detaille est traite par les stories suivantes (Epic 5/6).

### Technical Requirements

- Conserver API v1 REST avec schema d erreurs unifie en `snake_case`.
- Export et suppression doivent etre tracables bout-en-bout (etat + horodatage + contexte minimal).
- Idempotence obligatoire pour eviter doubles traitements sur clics repetes.
- Les donnees sensibles doivent rester chiffrees et les sorties export limitees aux donnees autorisees.
- Ne pas exposer de details techniques internes dans les messages utilisateur.

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Persistance PostgreSQL via SQLAlchemy + migration Alembic.
- Logs structures et metriques obligatoires sur operations privacy.
- Contrats OpenAPI explicites pour endpoints privacy.
- Frontend React + client API central + etats UX explicites.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic.
- DB: PostgreSQL cible (SQLite local acceptable pour tests).
- Auth: JWT access/refresh existant + RBAC minimal.
- Frontend: React + TypeScript + TanStack Query + API client centralise.
- Tests: Pytest (backend) et Vitest + Testing Library (frontend).

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/services/privacy_service.py` (nouveau)
  - `backend/app/api/v1/routers/` (nouveau routeur privacy ou extension)
  - `backend/app/infra/db/models/` (modele demandes privacy)
  - `backend/migrations/versions/` (migration privacy)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/` (client privacy)
  - `frontend/src/components/` ou `frontend/src/pages/` (espace confidentialite)
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - transitions etats demande privacy
  - idempotence export/suppression
  - erreurs metier stables
- Integration:
  - endpoints privacy proteges JWT + RBAC
  - creation et consultation de statut des demandes
  - reponses d erreur actionnables avec `request_id`
- Frontend:
  - actions export/suppression visibles
  - confirmations explicites
  - etats `loading/error/empty`

### Previous Story Intelligence

- Stories 4.1 a 4.3 ont etabli les patterns backend/frontend a reutiliser:
  - services metier dedies + routeurs fins
  - rate limiting compose (global/user/user-plan)
  - erreurs API stables et testees
  - refetch/invalidation cote UI apres mutation
- Pour 5.1, appliquer le meme niveau d exigence sur robustesse, idempotence et tracabilite.

### Git Intelligence Summary

- Historique recent axe robustesse et tests d integration; conserver une approche deltas localises et couverture tests stricte.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 5, Story 5.1)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR29, FR30, FR33, NFR5, NFR7, NFR8, NFR19)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Core Architectural Decisions, Authentication & Security, API Patterns)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (Journey 4 RGPD, etats loading/error/empty)
- Story precedente: `_bmad-output/implementation-artifacts/4-3-upgrade-modification-de-plan.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `.\.venv\Scripts\Activate.ps1; ruff check backend`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend`
- `npm run lint` (dans `frontend/`)
- `npm test -- --run` (dans `frontend/`)

### Completion Notes List

- Ajout d un workflow privacy self-service complet: export et suppression avec statuts traces, erreurs metier stables et `request_id`.
- Ajout du modele `UserPrivacyRequestModel` et migration Alembic associee avec index de consultation.
- Ajout du service privacy backend (export/suppression/statuts), metriques et logs structures.
- Ajout des endpoints REST `/v1/privacy/*` proteges JWT + RBAC user + rate limiting.
- Ajout de l integration frontend (client API + `PrivacyPanel`) avec confirmations et etats `loading/error/empty`.
- Ajout de tests unitaires et d integration backend, plus tests frontend dedies au parcours privacy.
- Validation complete executee avec succes: Ruff backend, Pytest backend (200 tests), ESLint frontend, Vitest frontend.

### File List

- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/privacy.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/privacy.py
- backend/app/main.py
- backend/app/services/privacy_service.py
- backend/app/tests/integration/test_privacy_api.py
- backend/app/tests/unit/test_privacy_service.py
- backend/migrations/env.py
- backend/migrations/versions/20260219_0009_add_user_privacy_requests.py
- frontend/src/App.tsx
- frontend/src/api/privacy.ts
- frontend/src/components/PrivacyPanel.tsx
- frontend/src/tests/PrivacyPanel.test.tsx
- _bmad-output/implementation-artifacts/5-1-export-et-suppression-des-donnees-personnelles.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
