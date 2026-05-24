# Implementation Plan

## Architecture finding

- `natal_chart_v1` is already defined in `backend/app/domain/astrology/runtime/natal_calculation_graph.py` as a pure `CalculationGraphDefinition`.
- The new graph-family registry must remain inside `backend/app/domain/astrology/runtime` and must not be exposed through API, DB, frontend, or migrations.
- The applicable story guardrails are RG-002, RG-003, and RG-022.

## Selected approach

- Add one canonical typed dataclass/enum registry module at `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- Store the eleven mandatory family declarations in a single tuple and build a validated mapping from that tuple.
- Reject duplicate declarations during registry construction and reject unknown lookup codes with an explicit error.
- Link `natal_chart_v1` to `build_natal_calculation_graph_definition()` through a dedicated resolver without changing public behavior.

## Files to modify

- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- CS-246 evidence files under `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/`
- `_condamad/stories/story-status.md`

## Tests and guards

- Unit tests prove mandatory family coverage, metadata fields, blocker filtering, duplicate rejection, unknown rejection, and natal graph linkage.
- Architecture tests prove OpenAPI/routes do not expose the internal registry.
- Targeted scans prove no API/frontend/alembic registry drift.

## No Legacy stance

- No shim, alias, fallback, re-export, or second registry is introduced.
- Unknown codes fail deterministically instead of mapping to a default family.

## Rollback strategy

- Remove the single registry module and its dedicated tests/evidence if review rejects the contract.
