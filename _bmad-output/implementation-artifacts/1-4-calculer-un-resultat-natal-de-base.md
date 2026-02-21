# Story 1.4: Calculer un resultat natal de base

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want obtenir un calcul natal de base (positions, maisons, aspects principaux),  
so that je recois un resultat astrologique coherent.

## Acceptance Criteria

1. Given des donnees natales valides et un referentiel versionne, when la generation de calcul natal est lancee, then le moteur produit un resultat structure conforme au ruleset actif.
2. Le calcul est reproductible a entrees identiques.

## Tasks / Subtasks

- [x] Definir le contrat de sortie natal de base (AC: 1, 2)
  - [x] Ajouter des modeles Pydantic pour `natal_result` (positions planetaires, maisons, aspects majeurs, metadonnees)
  - [x] Inclure `reference_version` et `ruleset_version` dans la sortie
  - [x] Standardiser le format `{data, meta}` et erreurs `{error.code, message, details, request_id}`
- [x] Implementer le calcul natal dans le domaine/service (AC: 1, 2)
  - [x] Creer la couche `domain/astrology` pour le calcul de base (positions/maisons/aspects)
  - [x] Utiliser les donnees preparees de Story 1.2 (`/natal/prepare`) comme entree du calcul
  - [x] Utiliser le referentiel versionne de Story 1.3 pour parametrer le calcul
- [x] Ajouter endpoint API v1 de calcul natal (AC: 1, 2)
  - [x] Exposer `POST /v1/astrology-engine/natal/calculate`
  - [x] Valider les entrees, gerer erreurs deterministes et versions inexistantes
  - [x] Retourner un resultat stable a entrees/version identiques
- [x] Garantir la reproductibilite (AC: 2)
  - [x] Eliminer toute source de non-determinisme (ordre, arrondis, fallback implicites)
  - [x] Definir regles d arrondi explicites (angles, degres)
  - [x] Verifier coherence UT/JD -> calcul -> sortie
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires: calculs de base, reproductibilite, cas limites
  - [x] Tests integration: endpoint `natal/calculate` avec referentiel seeded
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend prioritaire (pas de travail frontend attendu).
- Reutiliser la preparation natale deja en place (Story 1.2) et le referentiel versionne (Story 1.3).
- La story vise un premier resultat calculatoire fiable, pas une interpretation textuelle complete.

### Technical Requirements

- Stack imposee: Python 3.13, FastAPI, SQLAlchemy 2.x, Pydantic 2.x, PostgreSQL.
- Le calcul doit se baser sur:
  - donnees natales preparees (UT/JD),
  - referentiel astrologique versionne actif,
  - regles explicites et deterministes.
- Le resultat doit inclure:
  - positions planetaires essentielles,
  - maisons principales,
  - aspects majeurs,
  - metadonnees de version (`reference_version`, `ruleset_version`).

### Architecture Compliance

- Respect strict des couches: `api -> services -> domain -> infra`.
- Aucune logique metier astro dans `api` ou `infra`.
- Contrat API uniforme `/v1` + envelope standard.
- Ne pas contourner le versioning referentiel.

### Library / Framework Requirements

- FastAPI + Pydantic pour contrats d entree/sortie.
- SQLAlchemy pour acces referentiel (lecture seule dans cette story).
- Alembic pour tout changement schema (pas de `create_all` runtime).

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/domain/astrology/calculators/natal.py`
  - `backend/app/domain/astrology/calculators/aspects.py`
  - `backend/app/domain/astrology/calculators/houses.py`
  - `backend/app/services/natal_calculation_service.py`
  - `backend/app/api/v1/routers/astrology_engine.py` (extension)
  - `backend/app/tests/unit/test_natal_calculation*.py`
  - `backend/app/tests/integration/test_natal_calculate_api.py`

### Testing Requirements

- Unit:
  - deterministic output for same inputs
  - angle/aspect computation sanity checks
  - handling missing reference version
- Integration:
  - endpoint success with seeded reference
  - 4xx coherent errors for invalid input/version
  - stable repeated calls with identical payload
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 1.3 a introduit le referentiel versionne et a corrige des points critiques:
  - seed non destructif,
  - clone de version reel,
  - endpoint de seed protege par token,
  - suppression du `create_all` runtime.
- Conserver ces garde-fous (immutabilite versionnee + gouvernance migrations) dans Story 1.4.

### Git Intelligence Summary

- Les derniers commits du repository concernent surtout une ancienne base frontend/tests.
- Pour ce projet relance, privilegier les conventions deja posees dans `backend/app` plutot que des patterns historiques non alignes.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.4)
- Architecture patterns et stack: `_bmad-output/planning-artifacts/architecture.md`
- Recherche astrologie (calculs/ephemerides): `docs/recherches astro/08_Calculs_donnees_ephemerides.md`
- Methode de lecture/cadrage restitution: `docs/recherches astro/03_Methode_de_lecture_natal.md`
- Story precedente: `_bmad-output/implementation-artifacts/1-3-mettre-en-place-le-referentiel-astrologique-versionne.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story implementation and validation (ruff + pytest)

### Completion Notes List

- Added deterministic natal calculation pipeline (planet positions, houses, major aspects).
- Added typed `NatalResult` contract with `reference_version` and `ruleset_version`.
- Added `POST /v1/astrology-engine/natal/calculate` endpoint.
- Added deterministic ordering safeguards for reference-data reads.
- Added unit and integration tests for reproducibility and missing reference version.
- Verified quality gates: `ruff check .` and `pytest -q` passed.
- Review fixes applied:
  - standardized `astrology-engine` error envelopes (no nested `detail.error`),
  - propagated real `request_id` on success and error responses,
  - added explicit `db.rollback()` in error paths for calculation endpoint,
  - ensured stable response for identical inputs by enabling deterministic `chart_id` in engine flow,
  - added integration coverage for invalid input `422` and request-id assertions.

### File List

- _bmad-output/implementation-artifacts/1-4-calculer-un-resultat-natal-de-base.md
- backend/app/core/config.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/domain/astrology/calculators/__init__.py
- backend/app/domain/astrology/calculators/natal.py
- backend/app/domain/astrology/calculators/houses.py
- backend/app/domain/astrology/calculators/aspects.py
- backend/app/services/natal_calculation_service.py
- backend/app/services/chart_result_service.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/infra/db/repositories/reference_repository.py
- backend/app/tests/unit/test_chart_result_service.py
- backend/app/tests/unit/test_natal_calculation_service.py
- backend/app/tests/integration/test_natal_calculate_api.py

### Change Log

- 2026-02-20: Code-review fixes integrated (error contract, request_id, rollback safety, stable chart_id response, extra 422 integration test).
