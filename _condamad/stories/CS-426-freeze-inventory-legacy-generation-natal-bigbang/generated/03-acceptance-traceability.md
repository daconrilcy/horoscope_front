# Acceptance Traceability

Commentaire global: cette trace relie chaque AC CS-426 aux artefacts persistants et validations executees.

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Backend natal generation routes are mapped. | Evidence only; no route code changed. | `evidence/legacy-generation-map.md`; `VC1`; `python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short`. | PASS |
| AC2 | Frontend natal generation triggers are mapped. | Evidence only; no frontend runtime changed. | `evidence/legacy-generation-map.md`; `VC2`; guard test confirms frontend source paths. | PASS |
| AC3 | Natal prompt/seed surfaces are classified. | Evidence only; no seed execution or seed edit. | `evidence/legacy-surface-classification.md`; `VC1`; `VC3`; guard test confirms allowed classifications. | PASS |
| AC4 | Cache/persistence generation surfaces are classified. | Evidence only; no model/service edit. | `evidence/legacy-surface-classification.md`; `VC4`; runtime delta check reports `runtime_delta=NONE`. | PASS |
| AC5 | Readonly surfaces are non-generative. | Evidence and guard only. | Guard test `test_readonly_rows_are_explicitly_non_generative`; readonly rows use `Non-generative` notes. | PASS |
| AC6 | Needs-decision surfaces have owners. | Evidence and guard only. | Guard test `test_classification_artifact_has_required_shape_and_decisions`; classification rows name owner and expected decision. | PASS |
| AC7 | Exposure classes are recorded. | Evidence and guard only. | Guard test confirms `public`, `admin-only`, `test-only`, `bootstrap`, and `historical` tokens in the map. | PASS |
| AC8 | `_condamad/run-state.json` remains out of scope. | No edit by this implementation. | `evidence/initial-scans.txt` VC6; `git status --short -- _condamad/run-state.json` remains pre-existing dirty. | PASS |
| AC9 | Functional application code stays unchanged. | Only evidence, story files, tracker, and one architecture test changed. | Runtime delta check reports `runtime_delta=NONE`; `git diff --name-only -- backend/app frontend/src backend/scripts backend/app/ops/llm/bootstrap backend/app/infra/db/models` has no output. | PASS |
| AC10 | Initial scans are persisted. | Evidence artifact added. | `evidence/initial-scans.txt`; guard test confirms VC1 through VC6 and required tokens. | PASS |
