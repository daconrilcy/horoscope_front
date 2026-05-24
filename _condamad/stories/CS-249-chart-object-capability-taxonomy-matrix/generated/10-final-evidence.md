# Final Evidence — CS-249-chart-object-capability-taxonomy-matrix

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-249-chart-object-capability-taxonomy-matrix
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: repository dirty before CS-249 with CS-246/CS-247/CS-248 artifacts and backend runtime/test files already modified or untracked.
- Pre-existing dirty files: unrelated CS-246/CS-247/CS-248 story artifacts, `_story_briefs/cs-246..cs-254`, `.agents/skills/condamad-product-architecture`, and existing backend graph runtime/test files.
- AGENTS.md files considered: repository root `AGENTS.md`; no scoped backend `AGENTS.md` found.
- Capsule generated: yes; generated files were copied from the derived prepare output into the target CS-249 capsule, then the derived capsule was removed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Human story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired into target capsule. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC9 classified. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present; story validation commands refined in `evidence/validation.md`. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `chart_object_capability_taxonomy.py` declares all mandatory families once. | Taxonomy unit tests PASS; `taxonomy-after.json`. | PASS | |
| AC2 | `ChartObjectCapabilityTaxonomyEntry` exposes required columns. | Taxonomy unit tests PASS. | PASS | |
| AC3 | Active families preserve current `ChartObjectCapabilities`; fixed stars remain documentary-only. | Capability preservation unit test PASS; before/after evidence. | PASS | |
| AC4 | Unknown family lookup raises explicit taxonomy error. | Unknown-family unit test PASS. | PASS | |
| AC5 | Lilith, apside, lot, asteroid, Chiron and midpoint are `needs-user-decision`. | Decision-status unit test PASS. | PASS | |
| AC6 | Architecture guard blocks unmanaged `object_type` branches and constrains taxonomy owner. | Architecture tests PASS; branch scan no matches. | PASS | |
| AC7 | No new family calculator class is present. | Calculator scan no matches; unresolved-family unit test PASS. | PASS | |
| AC8 | API neutrality test asserts no schema/route exposure and `TestClient` smoke. | API architecture tests PASS; OpenAPI route evidence. | PASS | |
| AC9 | Evidence files persisted under CS-249. | Capsule validation PASS. | PASS | |

## Files changed

- `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/**`
- `_condamad/stories/story-status.md`

## Files deleted

- Temporary derived capsule `_condamad/stories/story-cs-249-chart-object-capability-taxonomy-matrix-define-chart-object-capability-and-object-taxonomy-matrix` created by `condamad_prepare.py` and removed after target capsule repair.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`.
- Updated architecture guards for single runtime owner and API neutrality.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` | repo root | PASS_WITH_REPAIR | 0 | Generated missing capsule files in derived folder; copied to target. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-249-chart-object-capability-taxonomy-matrix` | repo root | PASS | 0 | Capsule valid. |
| `ruff format <changed CS-249 python files>` | repo root | PASS | 0 | Scoped format. |
| `ruff check <changed CS-249 python files>` | repo root | PASS | 0 | Clean after import fix. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_chart_object_capability_taxonomy.py backend\tests\architecture\test_chart_runtime_surface_guardrails.py backend\tests\architecture\test_api_contract_neutrality.py` | repo root | PASS | 0 | 21 passed. |
| `rg` unmanaged `object_type` branch scan | repo root | PASS | 1 | No matches. |
| `rg` forbidden calculator scan | repo root | PASS | 1 | No matches. |
| `rg` taxonomy ownership scan | repo root | PASS | 0 | Matches are canonical runtime/tests only. |
| `ruff check backend` | repo root | PASS | 0 | Backend lint clean. |
| `python -B -m pytest -q backend\tests` | repo root | PASS | 0 | 913 passed, 201 deselected. |
| OpenAPI absence and route absence `python -B -c` checks | repo root | PASS | 0 | Taxonomy not public. |
| `git diff --check` | repo root | PASS | 0 | CRLF warnings only. |

## Commands skipped or blocked

- Local dev server not started; no HTTP runtime behavior changed. `TestClient`, `app.routes`, `app.openapi()` and full backend tests provide app-start/import evidence.

## DRY / No Legacy evidence

- One canonical matrix owner: `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`.
- No compatibility shim, alias, fallback resolver or duplicate active matrix added.
- Unknown family lookup fails explicitly.
- Negative scans found no unmanaged object-type branch and no Lot/Asteroid/Chiron/Midpoint calculator classes.

## Diff review

- `git diff --stat`: reviewed; includes pre-existing unrelated CS-246/CS-247/CS-248 dirty files plus CS-249 changes.
- `git diff --check`: PASS with CRLF warnings only.

## Final worktree status

- Repository remains dirty due to pre-existing CS-246/CS-247/CS-248 changes and CS-249 implementation/evidence.

## Remaining risks

- The matrix is governance-only for CS-249; runtime builders are not migrated to consume it yet. That is intentional to avoid behavior changes.

## Suggested reviewer focus

- Review the family rows whose status is `needs-user-decision`, especially Lilith/apside versus currently projected astral-point behavior.

## Feedback loop routing

- No propagation: validations passed and no reusable guardrail/process correction beyond story-local evidence was identified.
