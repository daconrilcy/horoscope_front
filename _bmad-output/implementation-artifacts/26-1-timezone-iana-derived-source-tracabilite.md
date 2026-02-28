# Story 26.1: Timezone IANA derivee + source de tracabilite

Status: done

## Story

As a backend platform engineer,
I want Ajouter `timezone_iana` et `timezone_source` avec priorite user_provided.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une timezone utilisateur fournie **When** la preparation input est executee **Then** `timezone_source=user_provided` et la valeur n'est pas ecrasee.
2. **Given** l'option derivee activee sans timezone user **When** la resolution est executee **Then** `timezone_iana` est derivee et `timezone_source=derived`.
3. **Given** une reponse natal **When** metadata est lue **Then** `timezone_used` reflète la source effective.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-3)
  - [x] Implementer: Ajouter `timezone_iana`, `timezone_source` (`user_provided|derived`).
- [x] Task 2 (AC: 1-3)
  - [x] Implementer: Option derivee offline depuis `lat/lon` si active.
- [x] Task 3 (AC: 1-3)
  - [x] Implementer: Exposer `metadata.timezone_used` avec source effective.
- [x] Task 4 (AC: 1-3)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-3)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

### Review Follow-ups (AI)
- [x] [AI-Review][High] Add startup library availability check for `timezonefinder` and pre-load polygon data (warmup).
- [x] [AI-Review][Medium] Fix latency spike by moving `timezonefinder` initialization to app lifespan.
- [x] [AI-Review][Medium] Remove hidden DB commit side-effect in `UserAstroProfileService`.
- [x] [AI-Review][Medium] Support 4-character birth time (e.g. '9:00') in validation.
- [x] [AI-Review][Medium] Refactor brittle unit tests to use mocking for timezone derivation.
- [x] [AI-Review][Low] Add `TIMEZONE_DERIVED_ENABLED` to `.env.example`.
- [x] [AI-Review][Low] Align feature flag usage for `TIMEZONE_DERIVED_ENABLED`.

## Dev Notes

### Context

La qualite temporelle pro exige de savoir d'ou vient la timezone et de ne pas ecraser silencieusement une valeur utilisateur.

### Scope

- Ajouter `timezone_iana`, `timezone_source` (`user_provided|derived`).
- Option derivee offline depuis `lat/lon` si active.
- Exposer `metadata.timezone_used` avec source effective.

### Out of Scope

- Geocoding online additionnel.

### Technical Notes

- Derivation offline deterministic.
- Historiser la source sans stocker de payload brut geocoding.

### Tests

- Unit: precedence user_provided > derived.
- Integration: metadata timezone_used/source.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.
- Sous-option `TIMEZONE_DERIVED_ENABLED`.

### Observability

- Metric `timezone_source_total{source}`.
- Erreurs derivation timezone tracees.

### Dependencies

- 22.1
- 25.1

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

### Completion Notes List

- Timezone effective resolue avec priorite `user_provided` puis derivation offline (`derive_enabled`) via coordonnees.
- `prepare`/`calculate` exposent `timezone_used` + `timezone_source` dans metadata API.
- Observabilite ajoutee: compteurs `timezone_source_user_provided_total`, `timezone_source_derived_total`, `timezone_derivation_errors_total`.
- Tests story 26.1 completes:
  - Unit: priorite source, derivation, erreurs `missing_timezone`/`missing_coordinates`, metriques, retrocompatibilite.
  - Integration: endpoint `/natal/prepare` valide `timezone_source` (`user_provided` et `derived`) et `timezone_used`.
- Non-regression corrigee sur `UserAstroProfileService`: fallback simplified apres auto-seed si SwissEph indisponible.
- Validation locale:
  - `ruff check` sur fichiers modifies: OK.
  - `pytest -q`: 1183 passed, 3 skipped.
  - Import applicatif: `from app.main import app` OK.

### File List

- _bmad-output/implementation-artifacts/26-1-timezone-iana-derived-source-tracabilite.md
- backend/pyproject.toml
- backend/app/core/config.py
- backend/app/domain/astrology/natal_preparation.py
- backend/app/services/natal_preparation_service.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/services/natal_calculation_service.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/tests/unit/test_natal_preparation.py
- backend/app/tests/integration/test_natal_prepare_api.py
- backend/app/services/user_astro_profile_service.py

## Change Log

- 2026-02-28: Story 26.1 completee (Tasks 1-5), statut passe a `review`.
