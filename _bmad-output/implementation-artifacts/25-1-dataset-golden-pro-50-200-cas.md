# Story 25.1: Dataset Golden Pro 50-200 cas

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Construire une suite Golden Pro externe avec fixtures et tolerances documentees.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** le dataset Golden Pro **When** la suite est executee **Then** toutes les assertions respectent `+-0.01deg` planetes et `+-0.05deg` angles.
2. **Given** un cas golden **When** la comparaison est faite **Then** les settings utilises (engine/ephe/frame/zodiac/house_system) sont explicites dans la fixture.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Creer fixtures 50-200 cas: datetime/tz/place_resolved/expected.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Inclure attentes: Sun/Moon/Mercury, ASC/MC, cusp I/X.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Documenter settings exacts de comparaison.
- [x] Task 4 (AC: 1-2)
  - [x] Implementer: Executer assertions avec tolerances pro.
- [x] Task 5 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 6 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le niveau audit-grade exige validation croisee sur un panel large avec settings figes.

### Scope

- Creer fixtures 50-200 cas: datetime/tz/place_resolved/expected.
- Inclure attentes: Sun/Moon/Mercury, ASC/MC, cusp I/X.
- Documenter settings exacts de comparaison.
- Executer assertions avec tolerances pro.

### Out of Scope

- Scripts de scraping externes automatiques en CI.

### Technical Notes

- Preferer fixtures statiques versionnees.
- Isoler les tests pour execution deterministe CI.

### Tests

- Golden: dataset complet.
- Sanity: validite schema fixture.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.

### Observability

- Rapport de drift par composant (planetes/angles).
- Compteur de cas en echec par categorie.

### Dependencies

- 23.4
- 24.2

### Project Structure Notes

- Story artifact: `_bmad-output/implementation-artifacts/`.
- Planning source: `_bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md]
- [Source: .gemini/commands/bmad-bmm-create-story.toml]
- [Source: _bmad/bmm/workflows/4-implementation/create-story/template.md]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- _bmad/bmm/workflows/4-implementation/create-story/workflow.yaml
- _bmad/bmm/workflows/4-implementation/create-story/instructions.xml

### Implementation Plan

- Dataset golden pro externe versionne en JSON statique (`golden-pro-v1`) avec 50 cas.
- Cas construits avec datetime locale + timezone IANA + place_resolved (lat/lon/altitude).
- Valeurs attendues figees pour Sun/Moon/Mercury et angles ASC/MC/cusp I/X.
- Settings explicites par fixture: `engine`, `ephe`, `frame`, `zodiac`, `house_system`.
- Tests dedies: validation schema dataset + assertions de precision pro (`+-0.01deg` planetes, `+-0.05deg` angles).

### Completion Notes List

- Story reformatee pour alignement strict create-story.
- Dataset golden pro versionne cree: 50 cas (`backend/app/tests/golden/pro_dataset_v1.json`).
- Loader typé ajoute pour validation stricte du schema fixture (`backend/app/tests/golden/pro_fixtures.py`).
- Tests golden pro ajoutes avec comparaisons Sun/Moon/Mercury + ASC/MC + cusp I/X et verification des settings explicites.
- Validations executees:
  - `ruff check app/tests/golden/pro_fixtures.py app/tests/unit/test_golden_pro_dataset.py`
  - `pytest -q app/tests/unit/test_golden_pro_dataset.py` -> 51 passed
  - `pytest -q app/tests/unit/test_golden_reference_swisseph.py app/tests/unit/test_natal_golden_swisseph.py app/tests/unit/test_golden_pro_dataset.py` -> 69 passed, 1 skipped

### File List

- _bmad-output/implementation-artifacts/25-1-dataset-golden-pro-50-200-cas.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/tests/golden/pro_dataset_v1.json
- backend/app/tests/golden/pro_fixtures.py
- backend/app/tests/unit/test_golden_pro_dataset.py
- backend/app/tests/unit/test_golden_reference_swisseph.py
- backend/app/tests/unit/test_natal_golden_swisseph.py

## Change Log

- 2026-02-28: Creation du dataset golden pro externe versionne (50 cas) avec settings explicites et attentes planetes/angles.
- 2026-02-28: Ajout des tests de schema et de precision pro conformes aux tolerances `+-0.01deg` et `+-0.05deg`.
