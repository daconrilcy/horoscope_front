# Final Evidence — CS-247 graph-manifest-node-io-schema-contract

## Story status

- Validation outcome: PASS after implementation review/fix iteration 2
- Ready for review: clean implementation review
- Story key: CS-247-graph-manifest-node-io-schema-contract
- Source story: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`
- Capsule path: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract`
- Story status: `done`
- Registry status: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: dirty worktree with unrelated CS-246, architecture and test changes already present.
- AGENTS.md considered: repo root `AGENTS.md`; no backend-local `AGENTS.md` found by scoped search.
- Story status registry verified: CS-247 row path and brief source matched the requested story and brief.
- Capsule validation: PASS after preparing missing generated files.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Updated for CS-247 target key. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Target and forbidden surfaces documented. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Applied validation commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | No Legacy checklist present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `build_natal_calculation_graph_manifest()` derives `natal_chart_v1` manifest from graph definition and family registry. | Targeted pytest; `manifest-after.json`. | PASS |
| AC2 | `NodeIOSchema.input_schema` is generated for each node dependency. | `test_each_natal_node_declares_input_and_output_schema`. | PASS |
| AC3 | `NodeIOSchema.output_schema` is generated for each node output key. | `test_each_natal_node_declares_input_and_output_schema`. | PASS |
| AC4 | `validate_graph_manifest()` rejects duplicate outputs. | `test_duplicate_output_key_is_rejected`. | PASS |
| AC5 | `validate_graph_manifest()` rejects unknown required dependencies. | `test_unknown_required_input_is_rejected`. | PASS |
| AC6 | `validate_graph_manifest()` rejects empty input schema and incomplete output schema. | Missing schema tests in `test_calculation_graph_manifest.py`. | PASS |
| AC7 | `compare_graph_manifests()` classifies version, input, output, requiredness, optional dependency and type deltas. | Comparison unit tests; `manifest-comparison.md`. | PASS |
| AC8 | API, OpenAPI and frontend surfaces unchanged. | API neutrality pytest, OpenAPI/route `python -B -c` checks, negative `rg` over `backend/app/api frontend`. | PASS |
| AC9 | Evidence artifacts persisted. | `manifest-before.json`, `manifest-after.json`, `manifest-comparison.md`, `validation.md`; Python path assertion. | PASS |

## Files changed

- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`
- `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/*.md`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/*`
- `_condamad/stories/story-status.md` row CS-247 only

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`.
- Added `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`.
- Updated `backend/tests/architecture/test_api_contract_neutrality.py`.

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-247-graph-manifest-node-io-schema-contract` | PASS | Capsule complete. |
| `ruff format <changed Python files>` | PASS | Scoped format. |
| `python -B -m pytest -q tests\unit\domain\astrology\test_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_manifest.py tests\unit\domain\astrology\test_natal_calculation_graph_definition.py tests\architecture\test_api_contract_neutrality.py` | PASS | 26 passed. |
| `python -B -m pytest -q tests` | PASS | 894 passed, 201 deselected. |
| `ruff check .` | PASS | All checks passed. |
| OpenAPI and route `python -B -c` checks | PASS | Manifest absent from public OpenAPI/routes. |
| Runtime/test positive `rg` scan | PASS | Manifest references restricted to runtime and unit tests. |
| API/frontend negative `rg` scan | PASS | Exit 1 = no matches. |
| `git diff --check` | PASS | No whitespace errors. |

## Review/fix iteration 1

- Finding fixed: optional node dependencies were serialized but were not validated or compared.
- Code proof:
  - `GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_ADDED`;
  - `GraphManifestDeltaKind.NODE_OPTIONAL_INPUT_REMOVED`;
  - `validate_graph_manifest()` rejects unknown optional dependency keys.
- Test proof:
  - `test_unknown_optional_input_is_rejected`;
  - `test_manifest_comparison_classifies_optional_dependency_deltas`.
- Fresh implementation review: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/11-code-review.md`
  verdict `CLEAN`.
- Propagation: no-propagation; the correction is local and fully covered by story tests and evidence.

## Status alignment

- Tracker row already matched the requested path, source brief, status `done` and local date `2026-05-23`.
- `00-story.md` status was aligned from `ready-to-review` to `done`.
- Story validation, strict story lint and capsule validation passed after the status alignment.

## Review/fix iteration 2

- Finding fixed: descriptor requiredness was serialized in manifest evidence but not compared.
- Code proof:
  - `GraphManifestDeltaKind.REQUIRED_INPUT_REQUIREDNESS_CHANGED`;
  - `GraphManifestDeltaKind.NODE_INPUT_REQUIREDNESS_CHANGED`;
  - `GraphManifestDeltaKind.NODE_OUTPUT_REQUIREDNESS_CHANGED`.
- Test proof:
  - `test_manifest_comparison_classifies_requiredness_deltas`.
- Validation proof:
  - targeted manifest/API tests: PASS, 22 passed;
  - full backend tests: PASS, 897 passed, 201 deselected;
  - `ruff check .`: PASS;
  - story validation, strict story lint and capsule validation: PASS.
- Fresh implementation review: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/11-code-review.md`
  verdict `CLEAN`.
- Propagation: no-propagation; the correction is local and fully covered by story tests and evidence.

## Commands skipped or blocked

- Frontend lint/tests: NOT RUN; story explicitly excludes frontend and no frontend file changed.
- `backend/alembic` negative scan: ADJUSTED; path does not exist, scan rerun over existing API/frontend roots.
- Persistent local server: NOT RUN; FastAPI app startup was covered by `TestClient` and OpenAPI smoke tests. Manual command: `.\.venv\Scripts\Activate.ps1; cd backend; uvicorn app.main:app --reload`.

## DRY / No Legacy evidence

- One canonical manifest module: `calculation_graph_manifest.py`.
- One canonical validator module: `calculation_graph_manifest_validator.py`.
- No shim, alias, compatibility wrapper or fallback added.
- Unknown required inputs fail validation explicitly.
- Manifest generated from existing graph definition, avoiding duplicated node lists.
- No API, frontend, DB or migration exposure detected.

## Diff review

- `git diff --stat`: reviewed; tracked diff includes pre-existing unrelated CS-246 and architecture files plus CS-247 touched tracked files.
- `git diff --check`: PASS.
- Untracked CS-247 files are new story implementation/evidence files.

## Final worktree status

- Dirty worktree remains because unrelated pre-existing CS-246/architecture changes are still present.
- CS-247 files are implementation-review clean and registry row is `done`.

## Remaining risks

- Existing untracked CS-246 registry implementation is a dependency of CS-247 and remains outside this story's ownership.

## Suggested reviewer focus

- Confirm output type descriptor policy (`<node_code>.output`) is acceptable as the stable internal schema choice.
- Confirm manifest comparison compatibility classifications match future CS-248 trace needs.
