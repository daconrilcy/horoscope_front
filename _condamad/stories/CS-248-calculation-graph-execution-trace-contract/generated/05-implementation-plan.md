# Implementation Plan

## Initial repository findings

- `CalculationGraphRunner` already exposes node results, execution order, cache hits and provenance.
- Runner provenance includes raw output values, so it cannot be used directly as a redacted trace contract.
- Public API neutrality already has architecture tests for CS-225 through CS-247.

## Proposed changes

- Add one canonical runtime module for the trace contract.
- Attach `execution_trace` to `CalculationGraphExecutionResult`.
- Record per-node duration, cache status, input keys, output keys, error kind and provenance refs.
- Add targeted unit tests plus API neutrality guard.

## Files to modify

- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Files to delete

- None.

## Tests to add or update

- Add trace contract unit tests.
- Extend runner test to assert trace attachment.
- Extend API neutrality tests for the trace contract.

## Risk assessment

- Main risk is accidentally treating provenance as trace and leaking raw outputs; tests assert redaction.
- Existing unrelated LLM replay/admin prompt surfaces remain outside CS-248.

## Rollback strategy

- Remove the trace module, `execution_trace` runner hook and CS-248 tests/evidence.
