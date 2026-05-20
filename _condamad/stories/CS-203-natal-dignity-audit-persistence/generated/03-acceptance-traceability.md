<!-- Matrice de tracabilite des criteres d'acceptation CS-203. -->

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Audit table/model/repository are documented. | Evidence files document schema and upsert. | Evidence files + model/repository inspection. | PASS |
| AC2 | Successful chart persistence writes one audit row per planet. | `ChartResultService.persist_trace` calls dignity audit upsert. | `pytest -q backend/app/tests/unit/test_chart_result_service.py`. | PASS |
| AC3 | Audit row scores match `NatalResult.dignities[*]`. | Mapper persists precomputed score fields. | Service pytest comparing rows. | PASS |
| AC4 | Chart-level sect is persisted. | Mapper writes `chart_sect` in condition summary. | Service pytest. | PASS |
| AC5 | Planet sect condition is persisted. | Mapper writes `sect_condition` in condition summary. | Service pytest. | PASS |
| AC6 | Audit write is idempotent for same chart result. | Reuse repository functional upsert key. | Repository/service idempotence checks. | PASS |
| AC7 | Audit persistence does not recalculate dignities or sect. | Mapper imports contracts and DTO only. | Forbidden calculator scans. | PASS |
| AC8 | Public chart JSON remains unchanged. | No changes to public builder. | `test_chart_json_builder.py` and payload comparison. | PASS |
| AC9 | Audit write failure behavior is explicit. | No silent `try/except`; failures propagate. | Failure-path pytest and transaction note. | PASS |
| AC10 | Forbidden paths unchanged. | No frontend/API/domain/migration/seed edits. | Forbidden path `git diff` checks. | PASS |
| AC11 | Golden cases still pass. | No scoring behavior change. | `test_traditional_golden_cases.py`. | PASS |
| AC12 | Persistent evidence artifacts exist with required keywords. | Before/after/validation evidence created. | `Test-Path` and `rg` evidence checks. | PASS |
