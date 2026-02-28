# Story 27.2: Documentation dev reglages/erreurs/validation

Status: ready-for-dev
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

- [ ] Task 1 (AC: 1-3)
  - [ ] Implementer: Documenter defaults/options (`zodiac`, `ayanamsa`, `frame`, `house_system`, aspects school, TT).
- [ ] Task 2 (AC: 1-3)
  - [ ] Implementer: Documenter erreurs standardisees `422` et `503`.
- [ ] Task 3 (AC: 1-3)
  - [ ] Implementer: Ajouter guide de validation via suite Golden Pro.
- [ ] Task 4 (AC: 1-3)
  - [ ] Implementer: Ajouter exemples d'appels endpoints.
- [ ] Task 5 (AC: 1-3)
  - [ ] Ajouter/mettre a jour les tests definis dans la section Tests
- [ ] Task 6 (AC: 1-3)
  - [ ] Mettre a jour la documentation technique et la tracabilite de la story

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

### Completion Notes List

- Story reformatee pour alignement strict create-story.

### File List

- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\27-2-documentation-dev-reglages-erreurs-validation.md
