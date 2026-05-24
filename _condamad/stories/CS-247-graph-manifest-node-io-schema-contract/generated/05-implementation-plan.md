# Implementation Plan

## Architecture finding

- `CalculationGraphDefinition` already declares graph identity, version, inputs and nodes.
- CS-246 registry provides the canonical `natal_chart_v1` family metadata.
- No existing manifest or node IO schema contract existed before this story.

## Selected approach

- Add one internal manifest contract module under `backend/app/domain/astrology/runtime`.
- Add one dedicated manifest validator module under the same runtime ownership.
- Derive the natal manifest from `build_natal_calculation_graph_definition()` and the family registry.
- Pre-index node outputs before building input schemas so readable graph order does not need to be topological.
- Keep all models as internal dataclasses and avoid API, DB, frontend, migration or dependency changes.

## Files modified

- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`
- `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`

## Tests and guards

- Unit tests cover valid manifest, invalid schemas, duplicate outputs, unknown inputs and comparison deltas.
- Architecture test covers OpenAPI and route neutrality.
- Negative scan covers absence of manifest exposure in API and frontend.

## No Legacy stance

- No shim, alias, compatibility wrapper or fallback was added.
- Unknown required dependencies fail validation through explicit errors.
- There is one canonical manifest path and one canonical validator path.
