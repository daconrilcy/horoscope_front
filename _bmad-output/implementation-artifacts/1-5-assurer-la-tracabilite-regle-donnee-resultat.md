# Story 1.5: Assurer la tracabilite regle/donnee -> resultat

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a support or operations user,  
I want connaitre precisement quelles versions de regles et de referentiel ont produit un resultat,  
so that je peux auditer et expliquer les sorties moteur.

## Acceptance Criteria

1. Given un resultat astrologique calcule, when il est persiste et restitue, then il contient les identifiants de version regle + referentiel.
2. Un audit permet de retrouver cette correspondance sans ambiguite.

## Tasks / Subtasks

- [x] Definir le modele de tracabilite des calculs (AC: 1, 2)
  - [x] Ajouter une entite de persistence type `chart_results` avec identifiants metier et versions
  - [x] Inclure au minimum: `reference_version`, `ruleset_version`, empreinte des entrees, horodatage, resultat serialize
  - [x] Definir contraintes/index pour recherche audit (par `chart_id`, `user_id` si present, `created_at`, versions)
- [x] Mettre en place migrations et repository de traçabilite (AC: 1, 2)
  - [x] Creer migration Alembic de la table de resultat trace
  - [x] Implementer repository SQLAlchemy dedie (lecture/creation)
  - [x] Respecter conventions `snake_case`, schema d erreurs uniforme
- [x] Integrer la persistence au flux de calcul natal (AC: 1, 2)
  - [x] Brancher la persistence apres `natal/calculate` successful
  - [x] Garantir que chaque resultat persiste embarque les versions utilisees
  - [x] Ajouter identifiant de sortie (`chart_id`) dans la reponse API
- [x] Exposer un endpoint de consultation audit (AC: 2)
  - [x] Ajouter endpoint read-only `GET /v1/astrology-engine/results/{chart_id}`
  - [x] Retourner versions + metadonnees de production du resultat
  - [x] Gerer les erreurs `not_found` et payload d erreur standard
- [x] Garantir l ambiguite zero sur la correspondance (AC: 2)
  - [x] Definir une empreinte deterministe des entrees (`input_hash`)
  - [x] Interdire les enregistrements incomplets (versions nulles ou resultat vide)
  - [x] Ajouter garde-fous de coherence sur la restitution audit
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires repository/service de traçabilite
  - [x] Tests integration: calcul -> persistance -> consultation audit
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend data/service/api uniquement.
- S appuyer sur la story 1.4 qui calcule deja `reference_version` et `ruleset_version`.
- Le but n est pas encore l interpretation UX, mais la gouvernance/audit des sorties moteur.

### Technical Requirements

- Stack: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, PostgreSQL.
- Le resultat persiste doit conserver:
  - versions (`reference_version`, `ruleset_version`),
  - entree de calcul traçable (`input_hash`),
  - payload resultat structure,
  - horodatage et identifiant unique.
- Les recherches d audit doivent etre deterministes et reproductibles.

### Architecture Compliance

- Respect couches: `api -> services -> domain -> infra`.
- Persistence strictement via `infra/db/repositories`.
- API `/v1` + enveloppes standard (`data/meta`, `error`).
- Pas de logique de hash/versioning dispersee dans les routers.

### Library / Framework Requirements

- Alembic obligatoire pour schema update (pas de `create_all` runtime).
- SQLAlchemy pour modeles/repositories.
- Pydantic pour contrats d API et objets metier.

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/infra/db/models/chart_result.py`
  - `backend/app/infra/db/repositories/chart_result_repository.py`
  - `backend/migrations/versions/*_add_chart_results_traceability.py`
  - `backend/app/services/chart_result_service.py`
  - `backend/app/api/v1/routers/astrology_engine.py` (extension)
  - `backend/app/tests/unit/test_chart_result_service.py`
  - `backend/app/tests/integration/test_chart_result_audit_api.py`

### Testing Requirements

- Unit:
  - creation trace avec versions obligatoires
  - calcul deterministic `input_hash`
  - refus des enregistrements incomplets
- Integration:
  - `POST /natal/calculate` persiste un resultat trace
  - `GET /results/{chart_id}` restitue versions + metadonnees
  - `404` coherent si `chart_id` absent
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 1.4 a deja:
  - un contrat `NatalResult` avec `reference_version` et `ruleset_version`,
  - endpoint `POST /v1/astrology-engine/natal/calculate`,
  - controle strict du referentiel (signs/houses/aspects),
  - reproductibilite du calcul et tests associes.
- Reutiliser ces informations pour la persistence sans redefinir les regles.

### Git Intelligence Summary

- Historique git recent non representatif du nouveau socle backend du projet.
- Prioriser les conventions actuelles des fichiers `backend/app` et artefacts BMAD.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.5)
- Architecture conventions: `_bmad-output/planning-artifacts/architecture.md`
- Story precedente: `_bmad-output/implementation-artifacts/1-4-calculer-un-resultat-natal-de-base.md`
- Story de referentiel/versioning: `_bmad-output/implementation-artifacts/1-3-mettre-en-place-le-referentiel-astrologique-versionne.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story implementation and validation (ruff + pytest)

### Completion Notes List

- Added `chart_results` persistence model with version fields, input hash and result payload.
- Added Alembic migration for traceability table and indexes.
- Added `ChartResultRepository` and `ChartResultService` for trace create/read and deterministic `input_hash`.
- Extended `POST /v1/astrology-engine/natal/calculate` to persist and return `chart_id`.
- Added `GET /v1/astrology-engine/results/{chart_id}` audit endpoint.
- Added unit/integration tests for persistence and audit retrieval.
- Verified backend quality gates: `ruff check .` and `pytest -q` passed.
- Review fixes applied:
  - removed deterministic `chart_id` reuse to keep one persisted trace per calculation,
  - aligned audit endpoint auth with JWT + RBAC (`support`/`ops`) instead of seed token,
  - reinforced integration tests for audit correspondence (`reference_version`, `ruleset_version`, `input_hash`),
  - added explicit forbidden-role coverage for audit endpoint,
  - aligned story file list with actual schema evolution (`chart_results.user_id` migration).

### File List

- _bmad-output/implementation-artifacts/1-5-assurer-la-tracabilite-regle-donnee-resultat.md
- backend/app/infra/db/models/chart_result.py
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/repositories/chart_result_repository.py
- backend/app/infra/db/repositories/__init__.py
- backend/app/services/chart_result_service.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/migrations/env.py
- backend/migrations/versions/20260218_0002_add_chart_results_traceability.py
- backend/migrations/versions/20260218_0005_add_user_id_to_chart_results.py
- backend/app/tests/unit/test_chart_result_service.py
- backend/app/tests/unit/test_natal_calculation_service.py
- backend/app/tests/integration/test_natal_calculate_api.py

### Change Log

- 2026-02-20: Code-review fixes integrated (RBAC audit access, per-call trace persistence, stronger audit assertions, file list synchronization).
