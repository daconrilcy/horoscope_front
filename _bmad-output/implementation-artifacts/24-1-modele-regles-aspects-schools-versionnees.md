# Story 24.1: Modele de regles d'aspects schools versionnees

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend platform engineer,
I want Versionner les regles d'aspects (schools) et les exposer en metadata.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** un ruleset aspects charge **When** il est valide **Then** chaque aspect majeur contient `code`, `angle`, `default_orb_deg`.
2. **Given** un calcul natal **When** la reponse est construite **Then** `metadata.aspect_school` et `metadata.aspect_rules_version` sont presents.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Modele: aspect `code`, `angle`, `default_orb_deg`.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Overrides: `orb_luminaries_override_deg`, `orb_pair_overrides`.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: School/version: `modern|classic|strict`.
- [x] Task 4 (AC: 1-2)
  - [x] Implementer: Exposition metadata: `aspect_school`, `aspect_rules_version`.
- [x] Task 5 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 6 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le mode cabinet demande des regles d'orbs differenciables par ecole et version.

### Scope

- Modele: aspect `code`, `angle`, `default_orb_deg`.
- Overrides: `orb_luminaries_override_deg`, `orb_pair_overrides`.
- School/version: `modern|classic|strict`.
- Exposition metadata: `aspect_school`, `aspect_rules_version`.

### Out of Scope

- Ajout d'aspects mineurs.

### Technical Notes

- Stocker version de regles comme identifiant immutable.
- Validation stricte des orbs (bornes raisonnables).

### Tests

- Unit: validation schema ruleset.
- Unit: serialization metadata school/version.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 3.

### Observability

- Metric `aspect_rules_load_total{school,version,status}`.
- Logs de validation refusee.

### Dependencies

- 23.4

### Project Structure Notes

- Story artifact: `_bmad-output/implementation-artifacts/`.
- Planning source: `_bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md]
- [Source: .gemini/commands/bmad-bmm-create-story.toml]
- [Source: _bmad/bmm/workflows/4-implementation/create-story/template.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- _bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml
- _bmad/bmm/workflows/4-implementation/dev-story/instructions.xml

### Completion Notes List

- Story reformatee pour alignement strict create-story.
- AC1: `default_orb_deg` rendu obligatoire dans la validation du ruleset, avec bornes strictes (0 < orb <= 15). Raise `NatalCalculationError(code="invalid_reference_data")` si manquant ou hors bornes.
- AC1: `orb_luminaries_override_deg` (nouveau nom) supporte en plus de `orb_luminaries` (legacy). Validation des bornes identique.
- AC1: `orb_pair_overrides` — chaque valeur de paire validee dans les bornes (0 < orb <= 15).
- AC2: `AspectSchoolType` enum (modern|classic|strict) ajoute dans `config.py`. Env var `NATAL_RULESET_DEFAULT_ASPECT_SCHOOL`, default `modern`.
- AC2: `NatalResult` enrichi de `aspect_school: str = "modern"` et `aspect_rules_version: str = "1.0.0"`. Retro-compatible (model_validate() accepte payloads anciens).
- AC2: `NatalCalculationService.calculate()` construit `aspect_rules_version = f"{aspect_school}-{ruleset_version}"` et le passe a `build_natal_result()`.
- Tests: 18 nouveaux tests unitaires dans `test_aspect_ruleset_schema.py` — tous passent. Helpers de tests existants mis a jour (ajout `default_orb_deg`).
- 5 tests pre-existants restent en echec (non lies a cette story — valides avant nos changements).

### File List

- backend/app/core/config.py
- backend/app/core/constants.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/services/natal_calculation_service.py
- backend/app/tests/unit/test_aspect_ruleset_schema.py
- backend/app/tests/unit/test_natal_metadata.py
- backend/app/tests/unit/test_natal_pipeline_swisseph.py
- backend/app/tests/unit/test_natal_tt.py
- backend/app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py
- .claude/settings.json
- _bmad-output/implementation-artifacts/24-1-modele-regles-aspects-schools-versionnees.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-28: Implementation story 24-1 — modele regles aspects schools versionnees (claude-sonnet-4-6)
  - Validation stricte `default_orb_deg` obligatoire avec bornes [0;15] dans `build_natal_result()`
  - Support `orb_luminaries_override_deg` (nouveau nom) + `orb_pair_overrides` validation bornes
  - `AspectSchoolType` enum (modern|classic|strict) dans config.py
  - `NatalResult` + `aspect_school` + `aspect_rules_version` (retro-compatible)
  - `NatalCalculationService` construit et passe `aspect_rules_version = f"{school}-{ruleset_version}"`
  - 18 tests unitaires ajoutes (`test_aspect_ruleset_schema.py`)
  - Helpers de tests existants mis a jour avec `default_orb_deg`
- 2026-02-28: Code Review Fixes (BMad-BMM)
  - Autoriser les orbes de 0.0 (aspects exacts)
  - Ajouter le paramètre `aspect_school` à `NatalCalculationService.calculate()` pour permettre l'override
  - Utiliser `AspectSchoolType` dans `NatalResult` pour plus de robustesse
  - Nettoyer la recherche des overrides d'orbes par paires
  - Compléter les tests de métadonnées dans `test_natal_metadata.py`
  - Mettre à jour la liste des fichiers de la story
