# Story 26.2: Gestion des dates historiques ambiguës (DST/fold)

Status: ready-for-dev
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Detecter les heures locales ambiguës/non-existantes et renvoyer une erreur explicite.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** une date locale ambiguë (fold DST) **When** la preparation temporelle est executee **Then** l'API retourne `422` avec `code=ambiguous_local_time` et details.
2. **Given** une date locale non-existante **When** la preparation temporelle est executee **Then** l'API retourne une erreur metier explicite documentee.

## Tasks / Subtasks

- [ ] Task 1 (AC: 1-2)
  - [ ] Implementer: Detecter local times `ambiguous` et `non-existent`.
- [ ] Task 2 (AC: 1-2)
  - [ ] Implementer: Retourner `422 ambiguous_local_time` avec details actionnables.
- [ ] Task 3 (AC: 1-2)
  - [ ] Implementer: Documenter strategie (confirmation utilisateur/fallback explicite).
- [ ] Task 4 (AC: 1-2)
  - [ ] Ajouter/mettre a jour les tests definis dans la section Tests
- [ ] Task 5 (AC: 1-2)
  - [ ] Mettre a jour la documentation technique et la tracabilite de la story

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

### Completion Notes List

- Story reformatee pour alignement strict create-story.

### File List

- C:\dev\horoscope_front\_bmad-output\implementation-artifacts\26-2-gestion-dates-historiques-ambigu-dst.md
