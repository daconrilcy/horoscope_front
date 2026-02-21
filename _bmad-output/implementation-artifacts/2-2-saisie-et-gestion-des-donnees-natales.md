# Story 2.2: Saisie et gestion des donnees natales

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want renseigner et modifier mes donnees de naissance (date, heure, lieu),  
so that le moteur puisse produire mon theme de maniere personnalisee.

## Acceptance Criteria

1. Given un utilisateur authentifie, when il enregistre ses donnees natales, then les donnees sont validees et persistees.
2. Toute donnee invalide est rejetee avec message explicite.

## Tasks / Subtasks

- [x] Definir le modele de donnees natales utilisateur (AC: 1, 2)
  - [x] Ajouter table `user_birth_profiles` (FK `user_id`, date/heure/lieu/timezone, timestamps)
  - [x] Ajouter contraintes d unicite par utilisateur (profil actif unique)
  - [x] Creer migration Alembic associee
- [x] Ajouter repository et service de gestion des donnees natales (AC: 1, 2)
  - [x] Repository CRUD (`get_by_user_id`, `upsert`)
  - [x] Service metier avec validations et normalisations
  - [x] Reutiliser le module de preparation natale de Story 1.2 pour validation coherence
- [x] Exposer endpoints API v1 securises (AC: 1, 2)
  - [x] `GET /v1/users/me/birth-data`
  - [x] `PUT /v1/users/me/birth-data`
  - [x] Exiger token access valide et role `user` (ou compatible RBAC)
- [x] Standardiser erreurs explicites (AC: 2)
  - [x] Mapper erreurs de validation vers codes stables (`invalid_birth_input`, `invalid_timezone`, etc.)
  - [x] Retourner enveloppes API conformes (`error.code`, `message`, `details`, `request_id`)
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires service/repository (upsert, validation, lecture)
  - [x] Tests integration API (`GET/PUT` + auth + cas invalides)
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend uniquement, depend de 2.1 pour l auth JWT.
- S appuyer sur `BirthInput` et `prepare_birth_data` deja implementes pour eviter duplication.
- Conserver la separation stricte `api -> services -> domain -> infra`.

### Technical Requirements

- Persistence PostgreSQL via SQLAlchemy + Alembic.
- Auth obligatoire (JWT access token) sur endpoints profil natal.
- Validation explicite des champs:
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - `birth_timezone`

### Architecture Compliance

- Aucun acces DB direct depuis router.
- Pas de logique metier dans la couche API.
- Conventions de reponse/erreur identiques aux stories precedentes.

### Library / Framework Requirements

- FastAPI + Pydantic (schemas input/output).
- SQLAlchemy 2.x + Alembic (modeles/migrations).
- Reutiliser utilitaires auth/JWT de Story 2.1.

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/infra/db/models/user_birth_profile.py`
  - `backend/app/infra/db/repositories/user_birth_profile_repository.py`
  - `backend/app/services/user_birth_profile_service.py`
  - `backend/app/api/v1/routers/users.py`
  - `backend/migrations/versions/*_add_user_birth_profiles.py`
  - `backend/app/tests/unit/test_user_birth_profile_service.py`
  - `backend/app/tests/integration/test_user_birth_profile_api.py`

### Testing Requirements

- Unit:
  - validation des payloads
  - upsert profil natal par utilisateur
  - rejection des inputs invalides
- Integration:
  - `PUT` sans token => `401`
  - `PUT` valide => persisted
  - `GET` => retourne profil courant
  - erreurs explicites pour timezone/date/heure invalides
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 2.1 a introduit:
  - users + JWT access/refresh
  - router auth
  - base RBAC (`user/support/ops`)
- Story 1.2 fournit deja la logique de validation/conversion natale: la reutiliser.

### Git Intelligence Summary

- Eviter toute divergence de conventions; suivre le style backend etabli sur les stories 1.x et 2.1.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.2)
- Story auth precedente: `_bmad-output/implementation-artifacts/2-1-inscription-et-authentification-utilisateur-jwt.md`
- Story validation natale: `_bmad-output/implementation-artifacts/1-2-gerer-les-donnees-natales-et-les-conversions-temporelles.md`
- Architecture conventions: `_bmad-output/planning-artifacts/architecture.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution for Story 2.2
- `ruff check .`
- `pytest -q`

### Completion Notes List

- Added secure `/v1/users/me/birth-data` GET/PUT endpoints with JWT access-token auth.
- Implemented explicit validation error mapping (`invalid_birth_input`, `invalid_timezone`, etc.).
- Added Alembic migration `20260218_0004` for `user_birth_profiles`.
- Added unit and integration test coverage for birth-profile service/API flows.
- Hardened birth input schema with strict payload validation (`extra=forbid`) and DB-aligned string length bounds.
- Added global request validation envelope handling and malformed JSON integration coverage.
- Fixed Alembic deprecation warning via `path_separator = os` in Alembic config.
- Added structured error logging on DB persistence failure for `/v1/users/me/birth-data`.
- Git review scope for this story is limited to backend files listed below due to unrelated repository-wide frontend deletions.

### File List

- _bmad-output/implementation-artifacts/2-2-saisie-et-gestion-des-donnees-natales.md
- backend/app/api/v1/routers/users.py
- backend/app/api/v1/routers/__init__.py
- backend/app/main.py
- backend/app/domain/astrology/natal_preparation.py
- backend/migrations/versions/20260218_0004_add_user_birth_profiles.py
- backend/alembic.ini
- backend/app/tests/unit/test_user_birth_profile_service.py
- backend/app/tests/integration/test_user_birth_profile_api.py
