# Story 7.1: Espace compte entreprise et gestion des credentials API

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an enterprise admin,  
I want creer/regenerer mes cles API depuis mon espace compte,  
so that je gere l acces securise de mon organisation.

## Acceptance Criteria

1. Given un compte entreprise actif, when l admin genere une cle API, then une nouvelle cle valide est fournie selon les regles de securite.
2. Given un compte entreprise actif, when l admin regenere une cle API, then la cle precedente est invalidee et la nouvelle cle devient active.
3. Given une operation de creation/regeneration de cle API, when elle est executee, then l operation est auditee avec `request_id`, acteur, action, cible et statut.
4. Given un utilisateur non autorise, when il tente d acceder aux operations credentials B2B, then l acces est refuse via RBAC et erreurs API standardisees.

## Tasks / Subtasks

- [x] Concevoir le modele credentials API entreprise (AC: 1, 2, 3)
  - [x] Ajouter les tables/modeles SQLAlchemy pour client entreprise et credentials API actifs/archives
  - [x] Stocker uniquement un hash de secret (jamais la cle en clair), plus metadonnees d audit
  - [x] Prevoir invalidation atomique de l ancienne cle lors d une regeneration
- [x] Implementer le service backend de gestion des credentials (AC: 1, 2, 3)
  - [x] Ajouter un service `enterprise_credentials_service` (create/rotate/list metadata)
  - [x] Utiliser transactions explicites pour garantir coherence creation + invalidation + audit
  - [x] Stabiliser erreurs metier (`snake_case`) pour cas: compte inactif, role invalide, credential absent
- [x] Exposer les endpoints API v1 B2B credentials (AC: 1, 2, 4)
  - [x] Ajouter routeur REST `/v1/b2b/credentials/*`
  - [x] Appliquer RBAC strict (`enterprise_admin` ou role retenu d architecture)
  - [x] Appliquer rate limiting global + role + user
- [x] Ajouter audit systematique des actions sensibles credentials (AC: 3)
  - [x] Enregistrer evenements `b2b_api_key_create` et `b2b_api_key_rotate`
  - [x] Inclure `request_id`, acteur, cible, statut `success|failed`
  - [x] S assurer que l audit est transactionnel et non contournable
- [x] Integrer panneau frontend compte entreprise (AC: 1, 2, 4)
  - [x] Ajouter client API `frontend/src/api/enterpriseCredentials.ts`
  - [x] Ajouter panneau react pour creer/regenerer et afficher metadata (jamais le secret complet apres creation)
  - [x] Gerer explicitement les etats `loading/error/empty`
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: service credentials, invalidation, erreurs metier
  - [x] Integration tests backend: 401/403/429/200 + audit create/rotate
  - [x] Tests frontend: rendu panel, flux create/rotate, erreurs API
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 7 Story 7.1 (FR38), dans la suite de l outillage support/ops deja en place (Epic 6).
- Reutiliser les patterns etablis dans les stories precedentes:
  - routeurs v1 avec enveloppe d erreur uniforme et `request_id`
  - RBAC + rate limiting compose
  - audit des actions sensibles via `AuditService`
- Contraintes critiques:
  - ne jamais persister de secret API en clair
  - rotation de cle atomique (ancienne invalidee, nouvelle active)
  - endpoints reserves au role autorise B2B admin

### Technical Requirements

- Credentials API conformes aux exigences securite (hashage + non exposition secret persiste).
- Rotation robuste et tracable sans intervention manuelle DB.
- API errors stables (`snake_case`) et compatibles front.
- Observabilite minimale: logs structures + audit des actions credentials.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Auth/JWT/RBAC existants comme mecanisme unique d autorisation.
- SQLAlchemy + Alembic pour modeles/migrations.
- React + client API central + etats UX explicites.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest + Testing Library frontend.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/v1/routers/` (nouveau routeur credentials B2B)
  - `backend/app/services/` (nouveau service credentials entreprise)
  - `backend/app/infra/db/models/` (modeles entreprise/credentials)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - creation credential, rotation, invalidation ancienne cle
  - validations et erreurs metier
- Integration:
  - RBAC strict + rate limiting endpoints credentials
  - audit create/rotate avec champs requis
- Frontend:
  - etats `loading/error/empty`
  - flux create/regenerate et feedback utilisateur

### Previous Story Intelligence

- Story 6.2 a etabli:
  - endpoint ops monitoring avec patterns RBAC/rate limit reutilisables
  - audit des actions sensibles avec `request_id`
  - panneau frontend ops avec etats explicites
- Pour 7.1:
  - conserver ces conventions pour eviter divergence contracts API
  - appliquer le meme niveau de rigueur securite/audit sur les credentials

### Git Intelligence Summary

- Historique recent: increments courts, forte couverture tests integration sur endpoints securises.
- Continuer avec deltas limites et verification AC par tests.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.1)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR38, NFR8, NFR9, NFR18)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (RBAC, observabilite, API versioning, securite)
- UX: `_bmad-output/planning-artifacts/ux-design-specification.md` (etats `loading/error/empty`)
- Story precedente: `_bmad-output/implementation-artifacts/6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics.md`
- `.\.venv\Scripts\Activate.ps1; ruff format backend`
- `.\.venv\Scripts\Activate.ps1; ruff check backend`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_enterprise_credentials_service.py backend/app/tests/integration/test_enterprise_credentials_api.py`
- `cd frontend; npm run lint`
- `cd frontend; npm test -- --run`

### Completion Notes List

- Story creee avec contexte implementation complet pour Epic 7 Story 7.1.
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Ajout du modele entreprise + credentials API avec stockage hash du secret uniquement.
- Ajout du service credentials entreprise (liste, generation, rotation) avec invalidation atomique.
- Ajout des endpoints `/v1/b2b/credentials` (list/generate/rotate) avec RBAC `enterprise_admin`, rate limiting et audit transactionnel.
- Ajout du panneau frontend entreprise pour gestion de cle API avec etats `loading/error/empty`.
- Couverture tests backend/frontend ajoutee et suite de regression complete validee.
- Corrections post-review appliquees: migration Alembic ajoutee, contraintes DB de statut et unicite credential actif, secret de hash dedie (`API_CREDENTIALS_SECRET_KEY`), test `audit_unavailable` ajoute, et exposition UI de la cle reduite (masquage + expiration ecran).

### File List

- `_bmad-output/implementation-artifacts/7-1-espace-compte-entreprise-et-gestion-des-credentials-api.md`
- `backend/app/core/rbac.py`
- `backend/app/main.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/api/v1/routers/enterprise_credentials.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/enterprise_account.py`
- `backend/app/infra/db/models/enterprise_api_credential.py`
- `backend/app/services/enterprise_credentials_service.py`
- `backend/app/tests/unit/test_enterprise_credentials_service.py`
- `backend/app/tests/integration/test_enterprise_credentials_api.py`
- `backend/app/core/config.py`
- `backend/app/tests/unit/test_settings.py`
- `backend/migrations/env.py`
- `backend/migrations/versions/20260220_0012_add_enterprise_credentials_tables.py`
- `backend/.env.example`
- `frontend/src/App.tsx`
- `frontend/src/api/enterpriseCredentials.ts`
- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/tests/EnterpriseCredentialsPanel.test.tsx`

### Change Log

- 2026-02-20: Implementation completee Story 7.1 (modele credentials B2B, API, audit, UI, tests).
- 2026-02-20: Correctifs code-review appliques (migrations, contraintes DB, secret dedie, hardening UI secret, tests audit indisponible).
