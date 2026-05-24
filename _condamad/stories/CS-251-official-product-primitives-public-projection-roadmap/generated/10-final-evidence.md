# Final Evidence — cs-251-official-product-primitives-public-projection-roadmap

## Story status

- Validation outcome: PASS
- Implementation review outcome: CLEAN
- Final status: done
- Story key: CS-251-official-product-primitives-public-projection-roadmap
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/00-story.md`
- Source brief: `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md`
- `story-status.md` row: Path and source brief verified before implementation.
- Initial `git status --short`: dirty with pre-existing CS-246 through CS-250
  story/code artifacts plus `story-status.md`.
- AGENTS.md files considered: root `AGENTS.md`.
- Capsule generated/repaired: yes; required generated files were missing and
  were created with the helper.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Story contract preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Helper-generated and read. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated AC-by-AC. |
| `generated/04-target-files.md` | yes | yes | PASS | Updated with scoped files. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Updated with executed checks. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Read and applied. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `docs/architecture/official-product-primitives-public-projections.md`; `evidence/product-primitives.json` | roadmap `rg`; architecture test | PASS | Official primitives documented. |
| AC2 | Audience mapping table and JSON audiences | architecture test; full pytest | PASS | beginner, expert, astrologer, debug, AI, PDF, public-user covered. |
| AC3 | Non-public surface table; public contract guard | integration public contract test | PASS | Raw runtime surfaces rejected. |
| AC4 | `fixed_star_contacts` policy and CS-257 consequence | roadmap `rg`; architecture test | PASS | Policy is `needs-user-decision`. |
| AC5 | Roadmap table split by future layer | roadmap `rg` | PASS | API contract, frontend client, UI component separated. |
| AC6 | OpenAPI/route guard and `evidence/openapi-routes.md` | app `openapi()`/`routes` checks; TestClient tests | PASS | Public projection remains OpenAPI-neutral/ready. |
| AC7 | Expanded raw runtime non-exposure tests | `test_chart_runtime_surface_guardrails.py`; full pytest | PASS | Raw exposure guard remains active. |
| AC8 | `evidence/validation.txt`, `openapi-routes.md`, `product-primitives.json` | evidence path check; capsule validation | PASS | Evidence persisted. |

## Files changed

- `docs/architecture/official-product-primitives-public-projections.md`
- `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None in story scope.
- Cleanup: accidental duplicate helper-created capsule directory removed after
  verifying it resolved inside the workspace.

## Tests added or updated

- Updated public natal contract compatibility guard for additional forbidden raw
  runtime terms.
- Updated API contract neutrality guard for CS-251 roadmap/snapshot shape,
  OpenAPI schema neutrality and route neutrality.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ... --story-key CS-251-official-product-primitives-public-projection-roadmap --with-optional` | repo root | PASS | 0 | Capsule files generated. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-251-official-product-primitives-public-projection-roadmap` | repo root | PASS | 0 | Capsule validation passed. |
| `ruff format backend\tests\integration\astrology\test_natal_public_contract_compatibility.py backend\tests\architecture\test_api_contract_neutrality.py` | `backend` | PASS | 0 | Scoped Python formatting. |
| `ruff check backend` | repo root | PASS | 0 | Backend lint passed. |
| `python -B -m pytest -q backend\tests\integration\astrology\test_natal_public_contract_compatibility.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 0 | 17 passed, 3 deselected. |
| `rg -n "structured facts\|beginner summary\|expert technical projection\|fixed-star contacts\|LLM input" docs\architecture` | repo root | PASS | 0 | Required primitive names found. |
| `rg -n "API contract\|frontend client\|UI component\|needs-user-decision" docs\architecture\official-product-primitives-public-projections.md` | repo root | PASS | 0 | Required roadmap layers and blocker found. |
| `python -B -c app.openapi() forbidden-term assertions` | repo root | PASS | 0 | `chart_objects`, `ChartObjectRuntimeData`, `interpretation_input` absent. |
| `python -B -c app.routes forbidden-term assertions` | repo root | PASS | 0 | Route paths do not expose forbidden raw terms. |
| `python -B -c evidence path exists` | repo root | PASS | 0 | Product primitive snapshot exists. |
| `python -B -m pytest -q` | repo root | PASS | 0 | 3159 passed, 1 skipped, 1182 deselected. |
| `git diff --check -- <CS-251 paths>` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |

## Commands skipped or blocked

- Frontend tests: skipped as not applicable; story explicitly excludes frontend
  implementation and no frontend file changed.
- Browser validation: skipped as not applicable; no UI route/component/style
  changed.

## DRY / No Legacy evidence

- One canonical roadmap owner:
  `docs/architecture/official-product-primitives-public-projections.md`.
- No route, serializer, frontend, DB, auth, migration, temporal calculator or
  LLM narration change.
- No shim, alias, fallback, duplicate primitive registry or compatibility route
  was introduced.
- Raw runtime names appear only in forbidden-surface governance, negative scans
  and guard evidence.
- Fixed-star contacts are blocked as `needs-user-decision`, not silently exposed.
- Feedback loop routing: `no-propagation`; no accepted review/user correction or
  reusable guardrail update was required.

## Diff review

- `git diff --stat`: reviewed for CS-251 paths.
- `git diff --check`: PASS with CRLF working-copy warnings only.

## Final worktree status

- Final `git status --short`: dirty. CS-251 adds/updates the files listed
  above; pre-existing CS-246 through CS-250 artifacts remain dirty and were not
  reverted.

## Remaining risks

- Fixed-star public versus gated exposure remains a product decision; CS-257 must
  stay blocked until that decision is made.

## Suggested reviewer focus

- Review the primitive naming and fixed-star `needs-user-decision` consequence
  before drafting CS-255/CS-256/CS-257 implementation contracts.
