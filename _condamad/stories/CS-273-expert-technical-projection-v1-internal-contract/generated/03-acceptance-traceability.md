# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The internal projection contract exists. | `docs/architecture/expert-technical-projection-v1-contract.md` created with French global file comment. | `python -B -c` path check recorded in `evidence/validation.txt`; targeted pytest PASS. | PASS |
| AC2 | The projection is internal. | Contract names `expert_technical_projection_v1` and classifies it as `interne`, `non client`, `not client-safe`. | `rg` checks over the contract and docs PASS; targeted pytest PASS. | PASS |
| AC3 | Authorized consumers are explicit. | Contract limits current use to `ADMIN` and future `ASTRO_EXPERT` as `target-only`. | `rg` checks and `test_contract_document_defines_internal_projection_shape` PASS. | PASS |
| AC4 | B2C access is denied. | Contract denies clients B2C, public-user surfaces, generated frontend clients and public routes. | `python -B -m pytest -q backend/tests/unit/test_expert_technical_projection_contract.py --tb=short` PASS. | PASS |
| AC5 | Astrology data families are defined. | Contract lists `dignity`, `conditions`, `dominance`, `aspects`, `houses` and source metadata. | `rg` checks and `test_contract_lists_allowed_astrology_families_and_evidence_links` PASS. | PASS |
| AC6 | Evidence links are defined. | Contract links `structured_facts_v1`, structured signals and `evidence_refs`. | `rg` checks and targeted pytest PASS. | PASS |
| AC7 | Raw technical payloads are excluded. | Contract excludes raw runtime traces, prompt internals, replay payloads, provider debug dumps and unrestricted diagnostics. | Runtime command proves `app.openapi()` and `app.routes` neutrality; targeted pytest PASS. | PASS |
| AC8 | Permission ownership uses CS-271. | Contract references CS-271 and `docs/architecture/admin-permission-matrix.md`; no parallel permission matrix added. | `test_contract_document_defines_internal_projection_shape` PASS. | PASS |
| AC9 | Access-log fields are specified. | Contract lists actor, role, projection id, chart or answer reference, action, decision, timestamp and correlation id. | `rg` checks and `test_access_log_fields_are_required_by_contract` PASS. | PASS |
| AC10 | Registry wording is reclassified. | `docs/architecture/official-product-primitives-public-projections.md` and current-state synthesis mark expert projection internal/non-client, no public API/client/UI. | Expert-row and current-state negative scans PASS; targeted pytest PASS. | PASS |
| AC11 | Application source surfaces remain unchanged. | CS-273 changed only docs, one backend unit contract test and story evidence; no CS-273 file is under `backend/app`, `frontend/src` or migrations. | `evidence/app-surface-status.txt` records dirty app roots as pre-existing unrelated changes and the CS-273 changed-file set excludes those roots. | PASS |
| AC12 | Evidence artifacts are persisted. | `evidence/validation.txt`, `evidence/app-surface-status.txt`, `evidence/source-checklist.md`, generated traceability and final evidence updated. | Path checks PASS; capsule validation PASS. | PASS |

Status values: `PASS`, `FAIL`, `BLOCKED`.
