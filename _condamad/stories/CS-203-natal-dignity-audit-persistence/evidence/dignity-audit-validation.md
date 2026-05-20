<!-- Validation persistante CS-203. -->

# Dignity Audit Validation

## Repository And Service Validation

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_result_service.py`: PASS,
  12 tests passed.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_dignity_reference_seed.py`: PASS,
  2 tests passed.

The service tests prove audit row creation from precomputed `NatalResult.dignities`,
score and breakdown parity, chart sect persistence, planet `sect_condition`
persistence, no fabricated rows when `dignities` is empty, explicit
`ChartResultServiceError` failure classification and idempotent upsert for the
same chart result.

Concrete evidence command:

- `.\.venv\Scripts\Activate.ps1; <inline Python evidence probe>`: PASS.

Concrete representative output:

- `chart_id`: `4f7ba4ee-5226-4675-8b6c-253668ab4362`
- `chart_result_id`: `1`
- `dignity_count`: `1`
- `before_linked_audit_rows`: `0`
- `after_linked_audit_rows`: `1`
- `after_idempotence_rerun_rows`: `1`
- sample planet: `sun`
- score parity: essential `5.0`, accidental `3.0`, total `8.0`
- breakdown parity: essential count `1`, accidental count `1`
- forbidden birth keys in `calculation_context_json`: none

## Public Payload Unchanged

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py`: PASS,
  18 tests passed.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_result_service.py`: PASS,
  includes existing payload preservation assertions.

`chart_results.result_payload` remains the source of public restitution. No code
reads `astral_chart_planet_dignity_results` to build public JSON.

## Regression Guards

- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`: PASS.
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`: PASS.

## No Recalculation Scans

No audit persistence hits were found for:

- `SectCalculator|PlanetSectConditionCalculator|PlanetDignityScoringService`
- `EssentialDignityCalculator|AccidentalDignityCalculator|AdvancedConditionEngine`
- `PlanetConditionProfileService|PlanetConditionSignalBuilder`
- `PlanetDominanceEngine|InterpretationAdapterEngine`
- doctrine constants such as `DIURNAL_PLANETS`, `HAYZ_RULES` and joy constants.

Alias scan hits for `sect_code` and `chart_sect_code` are existing runtime
reference/dignity-domain facts in:

- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/infra/db/repositories/astrology_runtime_reference_*`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`

Classification: allowed canonical runtime reference/dignity-domain usage, not
audit persistence code and not a new legacy alias.

## Transaction Boundary And Failure Behavior

Audit rows are flushed in the same SQLAlchemy session after `chart_results`
creation and before `persist_trace` returns. `ValueError` and `SQLAlchemyError`
from the audit write are classified as `ChartResultServiceError` with code
`dignity_audit_persistence_failed`; no fallback continues after a failed audit
write.

## Forbidden Path Diff

Empty diffs were confirmed for:

- `frontend`
- `backend/app/api`
- `docs/db_seeder`
- `backend/migrations`
- sect calculators
- advanced conditions, condition profiles, dominance and interpretation adapter domains
- `backend/app/domain/prediction`

## No Migration Or Seed Change

No migration or seed change was made. The existing table, model and upsert were
sufficient for CS-203.
