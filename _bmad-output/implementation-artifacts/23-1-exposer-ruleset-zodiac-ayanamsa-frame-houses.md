# Story 23.1: Exposer ruleset zodiac/ayanamsa/frame/house_system

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Rendre les conventions de calcul configurables via ruleset avec validation stricte.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une requete sans options explicites **When** le ruleset est resolu **Then** les defaults (`tropical/geocentric/placidus`) sont appliques.
2. **Given** `zodiac=sidereal` sans `ayanamsa` **When** la requete est validee **Then** l'API retourne `422` avec `code=missing_ayanamsa`.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Ajouter `zodiac`, `ayanamsa`, `frame`, `house_system` au ruleset/config.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Appliquer defaults si absents.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Validation: `sidereal` sans `ayanamsa` -> `422 missing_ayanamsa`.
- [x] Task 4 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le mode pro exige des conventions explicites et tracees a chaque calcul.

### Scope

- Ajouter `zodiac`, `ayanamsa`, `frame`, `house_system` au ruleset/config.
- Appliquer defaults si absents.
- Validation: `sidereal` sans `ayanamsa` -> `422 missing_ayanamsa`.

### Out of Scope

- Ajout Koch/Regiomontanus (backlog).

### Technical Notes

- Conserver typage enum strict pour eviter les modes implicites.
- Traçer le ruleset effectif en metadata.

### Tests

- Unit: resolution defaults.
- Integration: `422 missing_ayanamsa`.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 2.

### Observability

- `natal_ruleset_invalid_total{code}`.
- Log du ruleset effectif.

### Dependencies

- 22.2

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
- backend/app/services/natal_calculation_service.py
- backend/app/api/v1/routers/users.py
- backend/app/api/v1/routers/astrology_engine.py

### Completion Notes List

- Ruleset/config explicite ajoute dans `Settings` avec defaults: `zodiac=tropical`, `frame=geocentric`, `house_system=placidus`, `ayanamsa` optionnel.
- Resolution des options de calcul centralisee: options absentes resolues via defaults ruleset.
- Validation metier ajoutee: `zodiac=sidereal` sans `ayanamsa` retourne `422` avec `code=missing_ayanamsa`.
- Propagation des nouveaux champs ruleset de l'API (`users`/`astrology-engine`) vers les services de calcul.
- Tests ajoutes/mis a jour:
  - unit: resolution defaults ruleset
  - integration: `missing_ayanamsa` sur endpoint user natal chart
  - unit observabilite: mock settings complete avec nouveaux champs ruleset
- Validation executee:
  - `pytest -q` backend complet: 1033 passed, 3 skipped
  - `ruff check .` signale des dettes lint preexistantes hors scope story (fichier integration legacy)

### File List

- backend/app/core/config.py
- backend/app/services/natal_calculation_service.py
- backend/app/services/user_natal_chart_service.py
- backend/app/api/v1/routers/users.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/tests/unit/test_natal_calculation_service.py
- backend/app/tests/integration/test_user_natal_chart_api.py
- backend/app/tests/unit/test_swisseph_observability.py
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/23-1-exposer-ruleset-zodiac-ayanamsa-frame-houses.md

## Change Log

- 2026-02-27: Implementation Story 23.1 - ruleset defaults exposes (`zodiac/ayanamsa/frame/house_system`) + validation `missing_ayanamsa` + couverture tests.
