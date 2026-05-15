# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Immutable runtime dataclasses. | `backend/app/domain/astrology/runtime/runtime_reference.py` defines frozen dataclass contracts and tuple-backed reference sets. | `pytest -q tests/unit/domain/astrology/test_runtime_ref.py` PASS. | PASS |
| AC2 | Infra repository loads DB runtime refs. | `AstrologyRuntimeReferenceRepository` and mapper load DB/JSON-backed rows into immutable contracts; review fix added `load()` coverage against a seeded SQLAlchemy DB. | `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py` PASS. | PASS |
| AC3 | Runtime integrity is blocking. | Repository validation raises `AstrologyRuntimeReferenceError` for missing required runtime data, orphan references and `unknown` sentinels. | Repository tests and natal service tests PASS. | PASS |
| AC4 | Public domain functions accept no business `dict`. | `build_natal_result` consumes `AstrologyRuntimeReference`; tests migrated to typed factory. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py` PASS. | PASS |
| AC5 | Domain returns typed natal result contracts. | `NatalResult`, `PlanetPosition`, `HouseRuntimeData`, and aspect runtime contracts remain typed. | `pytest -q tests/unit/domain/astrology/test_natal_result_contract.py` PASS. | PASS |
| AC6 | Natal service uses runtime ref. | `NatalCalculationService` loads `AstrologyRuntimeReferenceRepository` and no longer calls `ReferenceDataService.get_active_reference_data`. | `pytest -q app/tests/unit/test_natal_calculation_service.py` PASS + negative scan zero-hit. | PASS |
| AC7 | Implicit engine fallback is removed. | `_resolve_engine` raises when requested/default SwissEph is unavailable; simplified is explicit test configuration only. | `pytest -q app/tests/unit/test_natal_calculation_service.py` PASS + fallback scan zero-hit. | PASS |
| AC8 | DB-backed constants leave runtime. | Natal runtime uses DB-backed reference contracts; forbidden constants removed from touched runtime path. | Negative scans for forbidden constants zero-hit on `domain/astrology` + `services/natal`. | PASS |
| AC9 | Legacy partial fixtures are migrated or deleted. | Tests use `tests.factories.astrology_runtime_reference_factory` instead of passing business dicts to domain functions. | Targeted domain astrology tests PASS. | PASS |
| AC10 | LLM preparation stays outside astrology domain. | Guard scans astrology domain for prediction/LLM imports and direct provider symbols. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py` PASS + scan zero-hit. | PASS |
| AC11 | Evidence files are persisted. | Evidence directory, removal audit, OpenAPI impact, guard output, and final evidence are persisted. | Capsule file review + final evidence. | PASS |
| AC12 | Big bang only: no migration flag. | No feature flag, shim, alias, dual run, or compatibility route added. | Guard tests, negative scans, and diff review PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
