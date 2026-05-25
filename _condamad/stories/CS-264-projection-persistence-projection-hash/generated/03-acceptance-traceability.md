# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | A persisted projection row carries `projection_hash`. | `backend/app/infra/db/models/projection_persistence.py`; `ProjectionPersistenceService.persist_from_builder`. | `python -B -m pytest -q tests/unit/projections ...` PASS; full backend pytest PASS. | PASS |
| AC2 | Equal canonical payloads keep one stable hash. | `backend/app/domain/astrology/projections/projection_hash.py`. | `tests/unit/projections/test_projection_hash.py` PASS. | PASS |
| AC3 | Changed canonical payload changes the hash. | Same canonical SHA-256 helper. | `tests/unit/projections/test_projection_hash.py` PASS. | PASS |
| AC4 | Source versions are retained. | `PersistedProjectionModel.source_versions`; repository/service create path. | `tests/unit/projections/test_projection_persistence.py` PASS. | PASS |
| AC5 | Access reads require scoped filters. | `ProjectionRepository.get_latest_for_scope`; `get_by_hash_for_scope`; `ProjectionAccessScope`. | `tests/unit/projections/test_projection_access.py` PASS. | PASS |
| AC6 | Builder absence blocks persistence. | `ProjectionBuilderUnavailableError`; no fallback branch in service. | `tests/unit/projections/test_projection_builder_gate.py` PASS; negative scan for fake/synthetic/fallback projection returned no matches. | PASS |
| AC7 | Narrative audit linkage is explicit. | `AINarrativePersistedProjectionIdentity` links `projection_type`, `projection_version`, `projection_hash` to narrative input links. | `tests/unit/domain/astrology/interpretation/test_ai_narrative_input_contract.py` PASS; `rg` found `narrative_answer_audit_v1` and `projection_hash` linkage. | PASS |
| AC8 | DB migration exposes the required schema. | `backend/migrations/versions/20260524_0138_create_persisted_projections.py`; model registered in `models/__init__.py`. | `tests/integration/test_projection_persistence_schema.py` PASS; `alembic heads` returns `20260524_0138`. | PASS |
| AC9 | Public API runtime surface stays unchanged. | No API router or frontend file added. | Runtime `app.routes`/`app.openapi()` check PASS; route scan returned no projection persistence route matches. | PASS |
| AC10 | Evidence artifacts are persisted. | `_condamad/stories/CS-264-projection-persistence-projection-hash/evidence/`; generated evidence files updated. | `condamad_validate.py` PASS before implementation; evidence files present after implementation. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
