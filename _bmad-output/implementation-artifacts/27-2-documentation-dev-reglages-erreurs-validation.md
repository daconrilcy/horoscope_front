# Story 27.2: Documentation dev reglages/erreurs/validation

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Documenter les reglages calcul pro, erreurs 422/503 et mode de validation Golden Pro.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** un developpeur backend/front **When** il lit la documentation **Then** il peut reproduire un calcul pro avec settings figes.
2. **Given** une erreur `422/503` **When** elle survient **Then** la documentation indique causes probables et actions de remediation.
3. **Given** la suite Golden Pro **When** elle est executee **Then** les tolerances et prerequis sont clairement decrits.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3)
  - [x] Implementer: Documenter defaults/options (`zodiac`, `ayanamsa`, `frame`, `house_system`, aspects school, TT).
- [x] Task 2 (AC: 1-3)
  - [x] Implementer: Documenter erreurs standardisees `422` et `503`.
- [x] Task 3 (AC: 1-3)
  - [x] Implementer: Ajouter guide de validation via suite Golden Pro.
- [x] Task 4 (AC: 1-3)
  - [x] Implementer: Ajouter exemples d'appels endpoints.
- [x] Task 5 (AC: 1-3)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 6 (AC: 1-3)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le niveau pro doit etre operable par les equipes dev/qa/ops avec une documentation executable.

### Scope

- Documenter defaults/options (`zodiac`, `ayanamsa`, `frame`, `house_system`, aspects school, TT).
- Documenter erreurs standardisees `422` et `503`.
- Ajouter guide de validation via suite Golden Pro.
- Ajouter exemples d'appels endpoints.

### Out of Scope

- Tutoriel utilisateur final grand public.

### Technical Notes

- Mettre a jour README/Docs techniques impactes.
- Garder exemples alignes avec contrat story 27.1.

### Tests

- Doc checks: liens valides, exemples executables.
- Smoke manuel: scenario "from scratch" documente.

### Rollout / Feature Flag

- Phase 3 finalisation avant passage general availability.

### Observability

- N/A runtime.
- Tracer version doc liee au `ephemeris_path_version`.

### Dependencies

- 27.1

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
- docs/natal-pro-dev-guide.md
- backend/app/tests/unit/test_natal_pro_docs.py
- backend/README.md
- docs/index.md

### Implementation Plan

- Ajouter une documentation technique unique pour le mode natal pro avec:
  - reglages figes de reproductibilite (`zodiac`, `ayanamsa`, `frame`, `house_system`, `aspect_school`, `tt_enabled`)
  - cartographie erreurs 422/503 avec causes/remediations
  - procedure de validation Golden Pro (prerequis, commandes, tolerances)
  - exemples d'appels endpoints prepare/calculate executables
- Lier ce guide dans la doc existante (index docs + README backend).
- Ajouter des tests docs pour valider:
  - presence des sections obligatoires
  - presence des exemples endpoint critiques
  - resolution des liens markdown locaux.

### Completion Notes List

- Story reformatee pour alignement strict create-story.
- Guide ajoute: `docs/natal-pro-dev-guide.md` avec:
  - settings pro figes et defaults runtime
  - erreurs standardisees 422/503 (causes + remediations)
  - guide validation Golden Pro (dataset, tolerances, prerequis)
  - exemples `POST /v1/astrology-engine/natal/prepare` et `POST /v1/astrology-engine/natal/calculate`.
- Index doc et README backend mis a jour pour exposer le guide pro.
- Tests doc ajoutes: `backend/app/tests/unit/test_natal_pro_docs.py`.
- Validation executee (venv actif):
  - `pytest -q app/tests/unit/test_natal_pro_docs.py` -> 3 passed
  - `pytest -q` (backend) -> 1194 passed, 3 skipped
  - `ruff check app/tests/unit/test_natal_pro_docs.py --fix` puis `ruff check app/tests/unit/test_natal_pro_docs.py` -> OK
  - `ruff check .` (backend complet) -> echec sur erreurs preexistantes hors scope story.

### File List

- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\27-2-documentation-dev-reglages-erreurs-validation.md
- C:\dev\horoscope_front\docs\natal-pro-dev-guide.md
- C:\dev\horoscope_front\docs\index.md
- C:\dev\horoscope_front\backend\README.md
- C:\dev\horoscope_front\backend\app\tests\unit\test_natal_pro_docs.py
- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\sprint-status.yaml

## Change Log

- 2026-02-28: Ajout du guide technique "natal pro" (reglages, erreurs 422/503, validation Golden Pro, exemples endpoints), tests doc associes, et mise a jour index/README backend.
