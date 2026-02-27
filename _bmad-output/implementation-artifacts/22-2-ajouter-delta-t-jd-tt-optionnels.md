# Story 22.2: Ajouter DeltaT et JD TT optionnels

Status: done

## Story

As a backend platform engineer,
I want Ajouter `delta_t_sec` et `jd_tt` optionnels, traces en metadata.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** `tt_enabled=true` **When** un calcul natal est execute **Then** `delta_t_sec > 0` et `jd_tt` est present.
2. **Given** `tt_enabled=false` **When** un calcul natal est execute **Then** `delta_t_sec` et `jd_tt` sont `null`.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Ajouter option `tt_enabled`.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: Calculer `delta_t_sec` et `jd_tt` si active.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Exposer `metadata.time_scale` et champs TT associes.
- [x] Task 4 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Certains audits demandent la trace TT en plus de UT, sans imposer TT a tous les appels.

### Scope

- Ajouter option `tt_enabled`.
- Calculer `delta_t_sec` et `jd_tt` si active.
- Exposer `metadata.time_scale` et champs TT associes.

### Out of Scope

- Changer la base de calcul par defaut (UT reste standard).

### Technical Notes

- Utiliser une source DeltaT deterministic/documentee.
- Encadrer DeltaT par plage plausible pour test anti-flake.

### Tests

- Unit: plages plausibles de `delta_t_sec`.
- Unit: branch coverage `tt_enabled` true/false.
- Integration: metadata/time_scale conforme.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 1.

### Observability

- Metric `time_pipeline_tt_enabled_total`.
- Log champ `time_scale` par requete.

### Dependencies

- 22.1

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

- _bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml
- _bmad/bmm/workflows/4-implementation/dev-story/instructions.xml
- backend/app/tests/integration/test_natal_prepare_api.py (red/green pour `tt_enabled` sur `/natal/prepare`)
- backend/app/tests/unit/test_natal_tt.py (validation unitaire DeltaT/JD TT)
- Commandes executees dans venv:
  - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_natal_prepare_api.py` (RED puis GREEN)
  - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/api/v1/routers/astrology_engine.py app/domain/astrology/natal_preparation.py app/tests/integration/test_natal_prepare_api.py app/tests/unit/test_natal_tt.py`
  - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_natal_tt.py app/tests/integration/test_natal_prepare_api.py`
  - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` (echec hors-perimetre sur `app/tests/unit/test_swisseph_observability.py`)

### Completion Notes List

- Endpoint `POST /v1/astrology-engine/natal/prepare` corrige pour accepter `tt_enabled` via un schema explicite (`NatalPrepareRequest`) et propager le flag au service de preparation.
- Les champs TT restent optionnels: `delta_t_sec` et `jd_tt` presents seulement quand `tt_enabled=true` (ou `SWISSEPH_PRO_MODE=true`), sinon `null`.
- `metadata.time_scale` est coherent avec le mode calcule (`TT` vs `UT`) sur l'endpoint prepare.
- Tests d'integration ajoutes pour couvrir les branches `tt_enabled=true/false` et verifier la coherence `data`/`meta`.
- Documentation backend mise a jour pour decrire l'usage de `tt_enabled` et les champs de sortie associes.
- **AI-Review Fixes**:
  - Implementation complete des polynômes NASA (Espenak & Meeus) pour les dates historiques (-500 à 2150+).
  - Correction de la précision temporelle du DeltaT: calculé avec continuité infra-journalière via JD.
  - Ajout de tests unitaires historiques (Year 1000, 1600, 1850) et de tests de continuité infra-journalière.
- Validation locale: lint cible OK; tests story 22.2 OK; suite backend complete avec 6 echecs preexistants hors story (`test_swisseph_observability`).

### File List

- _bmad-output/implementation-artifacts/22-2-ajouter-delta-t-jd-tt-optionnels.md
- backend/app/api/v1/routers/astrology_engine.py
- backend/app/domain/astrology/natal_preparation.py
- backend/app/tests/integration/test_natal_prepare_api.py
- backend/app/tests/unit/test_natal_tt.py
- backend/README.md

## Change Log

- 2026-02-27: Finalisation story 22.2 (tt_enabled sur `/natal/prepare`, tests integration true/false, documentation technique, statut `review`).
