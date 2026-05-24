# Implementation Review CS-247 graph-manifest-node-io-schema-contract

Verdict: CLEAN

## Scope

- Reviewed story: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`.
- Source brief: `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md`.
- Tracker row: `_condamad/stories/story-status.md` entry `CS-247`.
- Implementation surface:
  - `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`;
  - `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`;
  - `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/*`.

## Iteration 1 Findings

### FIXED: Optional dependencies were not validated or compared

- Severity: medium.
- AC/brief impact: the brief requires optional dependencies to be inspectable and comparable.
- Evidence before fix:
  - `NodeIOSchema.optional_depends_on` was serialized by `manifest_to_dict`;
  - `validate_graph_manifest()` did not reject unknown optional dependencies;
  - `compare_graph_manifests()` ignored `optional_depends_on` deltas.
- Fix:
  - added `node_optional_input_added` and `node_optional_input_removed` comparison deltas;
  - added validation for unknown optional dependency keys;
  - added unit tests for optional dependency validation and comparison.
- Validation after fix:
  - targeted manifest/API tests: PASS, 21 passed;
  - full backend tests: PASS, 896 passed, 201 deselected;
  - `ruff check .`: PASS.

## Iteration 2 Findings

### FIXED: Requiredness descriptor changes were not compared

- Severity: medium.
- Brief impact: the brief requires manifest comparison for contract changes and stable type descriptors.
- Evidence before fix:
  - `GraphTypeDescriptor.required` was serialized into persisted manifest evidence;
  - `compare_graph_manifests()` compared descriptor keys and `value_type`, but ignored `required` changes.
- Fix:
  - added requiredness delta kinds for global inputs, node inputs and node outputs;
  - classified requiredness changes as breaking contract deltas;
  - added targeted unit coverage for requiredness comparison.
- Validation after fix:
  - targeted manifest/API tests: PASS, 22 passed;
  - full backend tests: PASS, 897 passed, 201 deselected;
  - `ruff check .`: PASS;
  - story validation, strict story lint and capsule validation: PASS.

## Fresh Review Result

- AC1: `natal_chart_v1` exposes a validated manifest derived from the graph definition and family registry. PASS.
- AC2: every node declares non-empty input schema descriptors. PASS.
- AC3: every node declares one output schema descriptor. PASS.
- AC4: duplicate output keys are rejected. PASS.
- AC5: unknown required inputs are rejected. PASS.
- AC6: missing node schemas are rejected. PASS.
- AC7: manifest comparison classifies version, input, output, type, requiredness and optional dependency deltas. PASS.
- AC8: public API routes and OpenAPI schemas do not expose manifest contracts. PASS.
- AC9: before/after manifest, comparison and validation evidence are persisted. PASS.

## Validation Evidence

Commands run from repository root with `.venv` activated:

- `ruff format` on changed manifest files and manifest tests: PASS.
- `pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py
  tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py
  tests\architecture\test_api_contract_neutrality.py`: PASS, 22 passed.
- `ruff check .`: PASS.
- `pytest -q tests`: PASS, 897 passed, 201 deselected.
- OpenAPI manifest absence smoke check: PASS.
- Route manifest absence smoke check: PASS.
- Negative API/frontend exposure scan: PASS, no matches.
- `git diff --check`: PASS, no whitespace errors.
- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
- `condamad_validate.py`: PASS.

## Guardrails

- `RG-002`: backend ownership remains under `backend/app/domain/astrology/runtime`; no API, DB or frontend owner drift.
- `RG-022`: backend lint, tests, story validation and persisted evidence were rerun after correction.
- no-propagation: the correction is local to this story and does not require guardrail, AGENTS.md or skill updates.

## Residual Risk

Aucun risque restant identifie.
