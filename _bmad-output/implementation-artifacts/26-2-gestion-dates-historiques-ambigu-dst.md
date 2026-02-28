# Story 26.2: Gestion des dates historiques ambiguës (DST/fold)

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Detecter les heures locales ambiguës/non-existantes et renvoyer une erreur explicite.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une date locale ambiguë (fold DST) **When** la preparation temporelle est executee **Then** l'API retourne `422` avec `code=ambiguous_local_time` et details.
2. **Given** une date locale non-existante **When** la preparation temporelle est executee **Then** l'API retourne une erreur metier explicite documentee.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Detecter local times `ambiguous` et `non-existent`.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Retourner `422 ambiguous_local_time` avec details actionnables.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Documenter strategie (confirmation utilisateur/fallback explicite).
- [x] Task 4 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Les transitions DST historiques peuvent rendre une date locale ambiguë ou invalide; le calcul pro ne doit pas choisir silencieusement.

### Scope

- Detecter local times `ambiguous` et `non-existent`.
- Retourner `422 ambiguous_local_time` avec details actionnables.
- Documenter strategie (confirmation utilisateur/fallback explicite).

### Out of Scope

- UI de confirmation utilisateur.

### Technical Notes

- S'appuyer sur mecanisme timezone natif (fold/gap) deterministe.
- Ne pas appliquer de correction implicite cachee.

### Tests

- Unit: cas ambiguous et non-existent.
- Golden dataset: cas DST historique.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.

### Observability

- Metric `time_ambiguity_total{type}`.
- Logs structurés avec timezone/date (sans PII adresse).

### Dependencies

- 26.1

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
- _bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml
- _bmad/bmm/workflows/4-implementation/dev-story/instructions.xml

### Implementation Plan

- Ajouter une validation fold/gap deterministic dans `prepare_birth_data` avant conversion locale->UTC.
- Retourner des erreurs metier explicites (`ambiguous_local_time`, `nonexistent_local_time`) avec details actionnables.
- Instrumenter l'observabilite via `time_ambiguity_total_{type}` et logs structures.
- Couvrir les cas DST en tests unitaires + integration.
- Mettre a jour la documentation contrat API.

### Completion Notes List

- Detection DST fold/gap ajoutee dans `natal_preparation` via round-trip fold-aware (`fold=0/1`) pour differencier local time ambigu vs non-existant.
- Erreurs metier explicites retournees en `422` avec codes:
  - `ambiguous_local_time` + details (`timezone`, `local_datetime`, `candidate_offsets`, `resolution_hint`)
  - `nonexistent_local_time` + details (`timezone`, `local_datetime`, `resolution_hint`)
- Observabilite ajoutee:
  - compteurs `time_ambiguity_total_ambiguous` et `time_ambiguity_total_nonexistent`
  - logs structures `natal_preparation_local_time_ambiguous/nonexistent` sans PII adresse.
- Contrat API documente pour `/v1/astrology-engine/natal/prepare` sur les erreurs DST.
- Validation locale executee dans le venv:
  - `pytest -q app/tests/unit/test_natal_preparation.py app/tests/integration/test_natal_prepare_api.py` -> 41 passed
  - `ruff check app/main.py app/domain/astrology/natal_preparation.py app/tests/unit/test_natal_preparation.py app/tests/integration/test_natal_prepare_api.py` -> OK
  - `pytest -q` -> 1189 passed, 3 skipped
  - smoke import app -> `horoscope-backend`

### File List

- _bmad-output/implementation-artifacts/26-2-gestion-dates-historiques-ambigu-dst.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/domain/astrology/natal_preparation.py
- backend/app/tests/unit/test_natal_preparation.py
- backend/app/tests/integration/test_natal_prepare_api.py
- backend/app/main.py
- docs/api-contracts-backend.md

## Change Log

- 2026-02-28: Story 26.2 completee (Tasks 1-5), statut passe a `review`.
