# Story 21.2: Initialisation SwissEph robuste + erreurs explicites

Status: done

## Story

As a backend platform engineer,
I want Durcir l'initialisation SwissEph avec codes d'erreur 503 explicites.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** un fichier ephemerides absent **When** l'init swisseph est demandee **Then** l'API retourne `503` avec `code=ephemeris_data_missing` et `details.missing_file`.
2. **Given** une erreur technique d'initialisation **When** le moteur demarre **Then** l'API retourne `503` avec `code=swisseph_init_failed`.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Retourner `503 ephemeris_data_missing` avec `missing_file`.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Retourner `503 swisseph_init_failed` pour echec init non lie aux fichiers.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Normaliser payload erreur API.
- [x] Task 4 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

L'API doit distinguer clairement une indisponibilite data ephemerides d'un echec d'initialisation moteur.

### Scope

- Retourner `503 ephemeris_data_missing` avec `missing_file`.
- Retourner `503 swisseph_init_failed` pour echec init non lie aux fichiers.
- Normaliser payload erreur API.

### Out of Scope

- Strategie de retry infra.
- Fallback automatique vers moteur simplified.

### Technical Notes

- Mapper les exceptions bas niveau vers erreurs metier stables.
- Conserver correlation id et contexte minimal non-PII.

### Tests

- Unit: mocks filesystem + init provider, verification codes/details.
- Integration: endpoint natal renvoie 503 conforme.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 1.

### Observability

- `swisseph_errors_total{code}` incremente selon code metier.
- Logs structures avec `request_id`, `engine`, `error_code`.

### Dependencies

- 21.1

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

- Echecs pre-existants dans test_natal_calculate_api.py et test_user_natal_chart_api.py (401 par pollution d'etat entre tests) confirmes hors scope story 21-2

### Completion Notes List

- Story reformatee pour alignement strict create-story.
- AC1: `EphemerisDataMissingError` enrichi avec `missing_file: str | None` (defaut None). La methode `_compute_ephemeris_path_hash` leve maintenant l'erreur avec le nom du fichier manquant.
- AC2: Les exception handlers globaux dans `main.py` retournent desormais un payload normalise avec `details` (dict incluant `missing_file` si applicable) et `request_id`.
- Task 3: L'endpoint `/v1/ephemeris/status` inclut maintenant `details` et `request_id` dans toutes ses reponses 503. Il accepte un parametre `Request` pour resoudre le request_id.
- Observabilite: Nouvelle metrique unifiee `swisseph_errors_total|code=<code>` incrementee a cote des metriques existantes `swisseph_init_errors_total` et `swisseph_data_missing_total`.
- Tests: 12 nouveaux tests unitaires (36 total, 36 passes) + 10 nouveaux tests integration (21 total, 21 passes). Suite complete: 942 passes vs 919 avant (aucune regression).
- Durcissement post-review: validation des fichiers ephemerides requise au bootstrap (`validate_required_files=True`) pour garantir AC1 sans dependre d'un mode runtime.
- Ajout de 2 tests d'integration sur le vrai endpoint `/v1/astrology-engine/natal/calculate` pour verifier les 503 `ephemeris_data_missing` et `swisseph_init_failed`.
- Tracabilite mise a jour: liste de fichiers synchronisee avec les changements source constates en workspace.

### File List

- backend/app/core/ephemeris.py
- backend/app/main.py
- backend/app/api/v1/routers/ephemeris.py
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/core/config.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/infra/db/repositories/reference_repository.py
- backend/app/services/natal_calculation_service.py
- backend/app/services/user_natal_chart_service.py
- backend/app/tests/unit/test_ephemeris_bootstrap.py
- backend/app/tests/integration/test_ephemeris_api.py
- backend/app/tests/unit/test_natal_metadata.py
- backend/app/tests/unit/test_reference_data_service.py
- backend/app/tests/unit/test_settings.py
- frontend/src/api/natalChart.ts
- frontend/src/pages/BirthProfilePage.tsx
- _bmad-output/implementation-artifacts/21-2-initialisation-swisseph-robuste-erreurs-explicites.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-02-27: Implementation story 21-2 — EphemerisDataMissingError.missing_file, payload 503 normalise (details + request_id), metrique swisseph_errors_total{code}, 23 nouveaux tests (claude-sonnet-4-6)
- 2026-02-27: Fix review 21-2 — validation fichiers obligatoire au bootstrap + tests endpoint natal/calculate + file list synchronisee (codex-gpt-5)
