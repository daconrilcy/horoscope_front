# Story 2.1: Inscription et authentification utilisateur (JWT)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want creer un compte et me connecter de facon securisee,  
so that j accede a mes fonctionnalites personnalisees.

## Acceptance Criteria

1. Given un utilisateur non authentifie, when il cree un compte puis se connecte, then le systeme emet des tokens d acces/refresh valides.
2. Les echecs d authentification retournent des erreurs coherentes.

## Tasks / Subtasks

- [x] Definir le modele utilisateur et la persistence auth (AC: 1, 2)
  - [x] Ajouter modele DB `users` (email unique, password_hash, role minimal, timestamps)
  - [x] Ajouter migration Alembic associee
  - [x] Ajouter repository utilisateur (create/get by email/get by id)
- [x] Implementer la securite des identifiants (AC: 1, 2)
  - [x] Hash mot de passe (jamais stocker en clair)
  - [x] Verification de mot de passe a la connexion
  - [x] Validation robuste email/password et erreurs metier stables
- [x] Implementer generation JWT access + refresh (AC: 1)
  - [x] Ajouter utilitaires de signature/expiration des tokens
  - [x] Inclure claims minimales (sub, role, exp, token_type)
  - [x] Ajouter endpoint refresh token
- [x] Exposer endpoints API auth v1 (AC: 1, 2)
  - [x] `POST /v1/auth/register`
  - [x] `POST /v1/auth/login`
  - [x] `POST /v1/auth/refresh`
  - [x] Standardiser enveloppes succes/erreur (`data/meta`, `error`)
- [x] Poser les bases RBAC MVP (AC: 1)
  - [x] Roles minimaux `user`, `support`, `ops`
  - [x] Extraire role depuis token pour stories suivantes
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires (hash/verify, token generation/validation, erreurs auth)
  - [x] Tests integration (register/login/refresh + cas invalides)
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend prioritaire (pas de frontend requis).
- Ne pas casser le socle Epic 1 deja en place (`/v1/astrology-engine`, referentiel/versioning, traceability).
- Auth doit etre implementee de facon extensible pour les stories 2.x et 6.x.

### Technical Requirements

- JWT access + refresh obligatoires.
- RBAC minimal des MVP: `user`, `support`, `ops`.
- Erreurs auth coherentes et testables (identifiants invalides, email deja utilise, token invalide/expire).

### Architecture Compliance

- Respect couches `api -> services -> domain -> infra`.
- Persistence via `infra/db/repositories`.
- API versionnee `/v1`.
- Pas de secrets hardcodes (utiliser variables d environnement).

### Library / Framework Requirements

- FastAPI + Pydantic pour contrats API.
- SQLAlchemy + Alembic pour persistence utilisateurs.
- Signature JWT standard (algo explicite, expiration configuree).

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/infra/db/models/user.py`
  - `backend/app/infra/db/repositories/user_repository.py`
  - `backend/app/core/security.py`
  - `backend/app/core/rbac.py`
  - `backend/app/services/auth_service.py`
  - `backend/app/api/v1/routers/auth.py`
  - `backend/migrations/versions/*_add_users_table.py`
  - `backend/app/tests/unit/test_auth_service.py`
  - `backend/app/tests/integration/test_auth_api.py`

### Testing Requirements

- Unit:
  - password hash/verify
  - jwt create/verify
  - auth error mapping
- Integration:
  - register success + duplicate email
  - login success + bad credentials
  - refresh success + invalid/expired refresh token
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Epic 1 a deja impose:
  - format d erreurs unifie et contrats API `/v1`,
  - stack SQLAlchemy/Alembic/PostgreSQL,
  - conventions de tests et lint.
- Conserver ces patterns pour eviter divergence avant stories 2.2+.

### Git Intelligence Summary

- Historique git recent peu representatif du nouveau socle backend.
- Prioriser les conventions presentes dans `backend/app` et artefacts BMAD actuels.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.1)
- Architecture auth/security: `_bmad-output/planning-artifacts/architecture.md`
- Story precedente: `_bmad-output/implementation-artifacts/1-5-assurer-la-tracabilite-regle-donnee-resultat.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story implementation and validation (ruff + pytest)

### Completion Notes List

- Added user persistence model/repository and users migration.
- Added password hashing and JWT access/refresh token utilities.
- Added auth service with register/login/refresh and stable error mapping.
- Added API endpoints `POST /v1/auth/register`, `POST /v1/auth/login`, `POST /v1/auth/refresh`.
- Added RBAC base (`user`, `support`, `ops`) and token role claims.
- Added unit and integration tests for auth flows and failures.
- Verified backend quality gates: `ruff check .` and `pytest -q` passed.
- Review fixes applied:
  - removed hardcoded JWT fallback secret and replaced with non-hardcoded runtime secret in non-production,
  - hardened password verification for malformed stored hashes (safe `False` instead of runtime error),
  - added refresh token rotation with replay protection via persisted `jti`,
  - strengthened integration assertions for error contract (`code/message/details/request_id`),
  - clarified RBAC scope: MVP roles remain `user/support/ops`, `enterprise_admin` retained as post-MVP extension required by Epic 7.

### File List

- _bmad-output/implementation-artifacts/2-1-inscription-et-authentification-utilisateur-jwt.md
- backend/pyproject.toml
- backend/.env.example
- backend/app/core/config.py
- backend/app/core/security.py
- backend/app/core/rbac.py
- backend/app/infra/db/models/user.py
- backend/app/infra/db/models/user_refresh_token.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/repositories/user_repository.py
- backend/app/infra/db/repositories/user_refresh_token_repository.py
- backend/app/infra/db/repositories/__init__.py
- backend/app/services/auth_service.py
- backend/app/api/v1/routers/auth.py
- backend/app/api/v1/routers/__init__.py
- backend/app/main.py
- backend/migrations/env.py
- backend/migrations/versions/20260218_0003_add_users_table.py
- backend/migrations/versions/20260220_0018_add_user_refresh_tokens.py
- backend/app/tests/unit/test_auth_service.py
- backend/app/tests/integration/test_auth_api.py

### Change Log

- 2026-02-20: Code-review fixes integrated (JWT secret hardening, refresh token replay protection, malformed hash handling, stronger error-contract tests).
