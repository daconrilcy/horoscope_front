# Story 27.1: Standardiser la sortie API audit-grade

Status: done
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

- [x] Task 1 (AC: 1-3)
  - [x] Implementer: Standardiser metadata: `engine`, `ephemeris_path_version/hash`, `zodiac`, `ayanamsa`, `frame`, `house_system`, `aspect_school`, `timezone_used`, `jd_ut`, `jd_tt` (si active).
- [x] Task 2 (AC: 1-3)
  - [x] Implementer: Standardiser prepared_input: local/utc/timestamp/jd_ut/delta_t.
- [x] Task 3 (AC: 1-3)
  - [x] Implementer: Garantir invariants des champs dupliques (`result` vs `metadata`) ou supprimer doublons.
- [x] Task 4 (AC: 1-3)
  - [x] Implementer: Referencer `place_resolved_id` plutot que donnees de lieu brutes.
- [x] Task 5 (AC: 1-3)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 6 (AC: 1-3)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

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
- backend/app/domain/astrology/natal_preparation.py
- backend/app/services/user_natal_chart_service.py
- backend/app/tests/unit/test_natal_metadata.py
- backend/app/tests/integration/test_user_natal_chart_api.py

### Implementation Plan

- Etendre `BirthPreparedData` avec des aliases canoniques (`local/utc/timestamp/delta_t`) et `place_resolved_id` pour la tracabilite privacy-safe.
- Centraliser la construction de `UserNatalChartMetadata` depuis `NatalResult` pour imposer les invariants `result` vs `metadata`.
- Instrumenter la divergence `reference_version/ruleset_version` via metric `natal_contract_validation_failed_total` et warning structure.
- Ajouter des tests de contrat unitaires/integration pour garantir les champs obligatoires et l'absence de lieu brut.

### Completion Notes List

- Metadata audit-grade standardisee: `aspect_school`, `timezone_used`, `jd_ut`, `jd_tt`, `place_resolved_id` derives du resultat de calcul.
- `prepared_input` enrichi avec aliases stables `local`, `utc`, `timestamp`, `delta_t` + propagation `place_resolved_id`.
- Invariants `result` vs `metadata` garantis via une seule fabrique metadata; divergence DB/result sur versions tracee en metric + warning.
- Tests ajoutes/mis a jour:
  - unit: `test_user_natal_chart_metadata_audit_grade_fields_present_and_consistent`
  - integration: `test_generate_natal_chart_success` (assertions contrat complet + privacy-safe)
- Validation execution:
  - `pytest -q` (backend): 1191 passed, 3 skipped
  - `ruff check` cible sur fichiers modifies: OK

### File List

- backend/app/domain/astrology/natal_preparation.py
- backend/app/services/user_natal_chart_service.py
- backend/app/tests/unit/test_natal_metadata.py
- backend/app/tests/integration/test_user_natal_chart_api.py
- _bmad-output/implementation-artifacts/27-1-standardiser-sortie-api-audit-grade.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-28: Standardisation contrat API audit-grade (metadata/prepared_input), invariants metadata/result, trace `place_resolved_id`, tests de non-regression.
- 2026-02-28: [AI-Review] Fix derive_enabled propagation, accurate mode validation, and metadata consistency checks.
