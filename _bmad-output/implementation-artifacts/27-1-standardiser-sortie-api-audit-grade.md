# Story 27.1: Standardiser la sortie API audit-grade

Status: ready-for-dev
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Normaliser `metadata` et `prepared_input` pour un contrat API stable et privacy-safe.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une reponse natal pro **When** metadata/prepared_input sont inspectes **Then** tous les champs obligatoires sont presents selon le contrat.
2. **Given** des champs dupliques entre `result` et `metadata` **When** ils sont compares **Then** les valeurs sont identiques (ou le doublon est retire).
3. **Given** une reponse API **When** privacy est verifiee **Then** aucune PII adresse brute n'est exposee.

## Tasks / Subtasks

- [ ] Task 1 (AC: 1-3)
  - [ ] Implementer: Standardiser metadata: `engine`, `ephemeris_path_version/hash`, `zodiac`, `ayanamsa`, `frame`, `house_system`, `aspect_school`, `timezone_used`, `jd_ut`, `jd_tt` (si active).
- [ ] Task 2 (AC: 1-3)
  - [ ] Implementer: Standardiser prepared_input: local/utc/timestamp/jd_ut/delta_t.
- [ ] Task 3 (AC: 1-3)
  - [ ] Implementer: Garantir invariants des champs dupliques (`result` vs `metadata`) ou supprimer doublons.
- [ ] Task 4 (AC: 1-3)
  - [ ] Implementer: Referencer `place_resolved_id` plutot que donnees de lieu brutes.
- [ ] Task 5 (AC: 1-3)
  - [ ] Ajouter/mettre a jour les tests definis dans la section Tests
- [ ] Task 6 (AC: 1-3)
  - [ ] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

La sortie finale doit etre complete pour audit, sans fuite de PII.

### Scope

- Standardiser metadata: `engine`, `ephemeris_path_version/hash`, `zodiac`, `ayanamsa`, `frame`, `house_system`, `aspect_school`, `timezone_used`, `jd_ut`, `jd_tt` (si active).
- Standardiser prepared_input: local/utc/timestamp/jd_ut/delta_t.
- Garantir invariants des champs dupliques (`result` vs `metadata`) ou supprimer doublons.
- Referencer `place_resolved_id` plutot que donnees de lieu brutes.

### Out of Scope

- Evolution version majeure d'API (`/v2`).

### Technical Notes

- Verrouiller schema Pydantic de sortie.
- Ajouter tests de non-regression de contrat.

### Tests

- Unit: invariants result/metadata.
- Integration: validation schema complete et champs privacy-safe.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.

### Observability

- Metric `natal_contract_validation_failed_total`.
- Log warning sur divergence metadata/result.

### Dependencies

- 25.1
- 26.2

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

- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\27-1-standardiser-sortie-api-audit-grade.md
