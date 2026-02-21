# Story 1.3: Mettre en place le referentiel astrologique versionne

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a operations user,  
I want gerer un referentiel astro (planetes, signes, maisons, aspects, caracteristiques) versionne,  
so that le moteur s appuie sur des donnees metier controlees.

## Acceptance Criteria

1. Given une base PostgreSQL disponible, when les entites de referentiel sont creees et peuplees initialement, then le moteur peut lire ces donnees pour les calculs.
2. Chaque modification est liee a une version de referentiel.

## Tasks / Subtasks

- [x] Modeliser les entites de referentiel astro
  - [x] Definir modeles SQLAlchemy pour `planets`, `signs`, `houses`, `aspects`, `astro_characteristics`
  - [x] Ajouter table/version de referentiel (`reference_versions`) et relation vers les entites
  - [x] Aligner nommage DB avec conventions architecture (`snake_case`, index/uq)
- [x] Mettre en place l infrastructure PostgreSQL + migrations
  - [x] Configurer session DB et base SQLAlchemy
  - [x] Initialiser Alembic et creer migration initiale du referentiel
  - [x] Ajouter configuration env pour connexion PostgreSQL
- [x] Implementer seed initial du referentiel
  - [x] Ajouter script/service de seed idempotent
  - [x] Inserer jeu minimal coherent (planetes/signes/maisons/aspects)
  - [x] Attacher le seed a une version de referentiel explicite
- [x] Exposer la lecture du referentiel pour les stories suivantes
  - [x] Creer repository/service de lecture filtree par version active
  - [x] Ajouter endpoint API v1 de consultation referentiel (read-only)
  - [x] Standardiser reponses succes/erreur
- [x] Tracabilite des modifications et versioning
  - [x] Definir mecanisme de creation de nouvelle version de referentiel
  - [x] Garantir qu une modification ne mute pas silencieusement la version precedente
  - [x] Ajouter audit minimal des updates versionnees
- [x] Tester et valider
  - [x] Tests unitaires (repositories/services/versioning)
  - [x] Tests integration (migrations + seed + endpoint read)
  - [x] Lint + tests backend passes

## Dev Notes

- Story backend infra/data prioritaire: pas de logique UI.
- Base existante issue des stories 1.1 et 1.2:
  - FastAPI + route v1 deja en place
  - validations et conventions erreurs deja posees
  - outillage test/lint actif
- Introduire PostgreSQL/Alembic proprement sans casser l existant (healthcheck et endpoint 1.2).

### Technical Requirements

- Stack imposee:
  - PostgreSQL + SQLAlchemy + Alembic + Pydantic
- Entites minimales:
  - `planets`
  - `signs`
  - `houses`
  - `aspects`
  - `astro_characteristics`
  - `reference_versions`
- Versioning:
  - une version active lisible
  - historique immutable des versions precedentes

### Architecture Compliance

- Respect couches `api/core/domain/services/infra`.
- Acces DB uniquement via `infra/db` et services/repositories.
- API en `/v1` avec format d erreur coherent (`error.code`, `message`, `details`, `request_id`).
- Ne pas dupliquer logique de seed/versioning entre endpoints et services.

### Library / Framework Requirements

- SQLAlchemy 2.x
- Alembic
- FastAPI/Pydantic
- Redis non requis dans cette story sauf placeholder existant

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/infra/db/base.py`
  - `backend/app/infra/db/session.py` (etendue)
  - `backend/app/infra/db/models/`
  - `backend/app/infra/db/repositories/`
  - `backend/migrations/` + `alembic.ini`
  - `backend/app/services/reference_data_service.py`
  - `backend/app/api/v1/routers/reference_data.py`
  - `backend/app/tests/unit/` et `backend/app/tests/integration/`

### Testing Requirements

- Unit:
  - versioning referentiel
  - logique idempotence seed
  - lecture par version active
- Integration:
  - migration up/down de base
  - endpoint referentiel retourne donnees seed
  - update versionnee preserve historique
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 1.1 a fixe le socle monorepo et les conventions.
- Story 1.2 a introduit pattern service/domain + endpoint v1 + erreur standard.
- Conserver ces patterns pour eviter divergence de style entre routes.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.3)
- Architecture data stack: `_bmad-output/planning-artifacts/architecture.md` (Data Architecture, Project Organization)
- PRD FR4/FR5/FR6/FR7/FR8: `_bmad-output/planning-artifacts/prd.md`
- Stories precedentes: `_bmad-output/implementation-artifacts/1-1-set-up-initial-project-from-starter-template.md`, `_bmad-output/implementation-artifacts/1-2-gerer-les-donnees-natales-et-les-conversions-temporelles.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story implementation and fix pass (ruff + pytest)

### Completion Notes List

- Added SQLAlchemy models and repository for versioned astrology reference data.
- Added Alembic configuration and initial migration for reference tables.
- Added service and API endpoints for seed and read by version.
- Added unit/integration tests for idempotent seed, clone immutability and API read/404 behavior.
- Verified backend quality gates: `ruff check .` and `pytest -q` passed.
- Review fixes applied:
  - standardized error envelope for reference endpoints (`error.code/message/details/request_id`) without nested `detail`,
  - propagated real `request_id` in success and error payloads,
  - added versioned update audit events for `seed` and `clone`,
  - enforced immutable history on in-place updates of locked reference versions,
  - added Alembic upgrade/downgrade integration test for reference migration.

### File List

- _bmad-output/implementation-artifacts/1-3-mettre-en-place-le-referentiel-astrologique-versionne.md
- backend/pyproject.toml
- backend/alembic.ini
- backend/migrations/env.py
- backend/migrations/script.py.mako
- backend/migrations/versions/20260218_0001_create_reference_tables.py
- backend/migrations/versions/20260220_0017_add_reference_versions_is_locked.py
- backend/app/core/config.py
- backend/app/infra/db/base.py
- backend/app/infra/db/session.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/reference.py
- backend/app/infra/db/repositories/__init__.py
- backend/app/infra/db/repositories/reference_repository.py
- backend/app/services/reference_data_service.py
- backend/app/api/v1/routers/__init__.py
- backend/app/api/v1/routers/reference_data.py
- backend/app/main.py
- backend/app/tests/unit/test_reference_data_service.py
- backend/app/tests/integration/test_reference_data_api.py
- backend/app/tests/integration/test_reference_data_migrations.py

### Change Log

- 2026-02-20: Code-review fixes integrated (error contract, request_id propagation, audit events, immutability guard, migration up/down test).
