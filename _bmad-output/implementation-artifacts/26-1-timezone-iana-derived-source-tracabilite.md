# Story 26.1: Timezone IANA derivee + source de tracabilite

Status: ready-for-dev
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Ajouter `timezone_iana` et `timezone_source` avec priorite user_provided.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une timezone utilisateur fournie **When** la preparation input est executee **Then** `timezone_source=user_provided` et la valeur n'est pas ecrasee.
2. **Given** l'option derivee activee sans timezone user **When** la resolution est executee **Then** `timezone_iana` est derivee et `timezone_source=derived`.
3. **Given** une reponse natal **When** metadata est lue **Then** `timezone_used` reflète la source effective.

## Tasks / Subtasks

- [ ] Task 1 (AC: 1-3)
  - [ ] Implementer: Ajouter `timezone_iana`, `timezone_source` (`user_provided|derived`).
- [ ] Task 2 (AC: 1-3)
  - [ ] Implementer: Option derivee offline depuis `lat/lon` si active.
- [ ] Task 3 (AC: 1-3)
  - [ ] Implementer: Exposer `metadata.timezone_used` avec source effective.
- [ ] Task 4 (AC: 1-3)
  - [ ] Ajouter/mettre a jour les tests definis dans la section Tests
- [ ] Task 5 (AC: 1-3)
  - [ ] Mettre a jour la documentation technique et la tracabilite de la story

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

### Completion Notes List

- Story reformatee pour alignement strict create-story.

### File List

- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\26-1-timezone-iana-derived-source-tracabilite.md
