# Final Evidence — CS-246 Canonical Astrology Graph Family Registry

## Story status

- Status: done.
- Story path: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- Source brief: `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`.
- Source finding closure: `full-closure` for SC-ARCH-001 registry definition scope. Future implementation stories remain out of scope for graph manifest, execution trace, temporal technique choice, and public product primitives.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- `.git` exists; `git status --short` was run before editing.
- Pre-existing dirty/untracked context was preserved: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`, `.agents/skills/condamad-product-architecture/`, and untracked `_story_briefs/cs-246..cs-254` files.
- Applicable root instructions: `AGENTS.md` read before editing.
- Story status registry row matched story ID, path, and source brief before implementation.
- Regression guardrails applied from story scope: RG-002, RG-003, RG-022.

## Capsule validation

- Initial target capsule was incomplete; required generated files were absent.
- `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py _condamad\stories\CS-246-canonical-astrology-graph-family-registry\00-story.md --root C:\dev\horoscope_front` generated a parallel title-derived capsule.
- Required generated files were copied into the target CS-246 capsule; the parallel capsule was removed after path verification.
- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-246-canonical-astrology-graph-family-registry` passed before implementation.

## Implementation summary

- Added one canonical typed backend-domain registry at `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- Declared the eleven mandatory family codes with required metadata: status, owner, inputs, graph type, objects, public/internal surfaces, trace/replay needs, cache boundary, blockers, and user decisions.
- Linked `natal_chart_v1` to `build_natal_calculation_graph_definition()` without modifying the natal graph definition or public API.
- Added deterministic duplicate declaration and unknown-code rejection.
- Added targeted unit tests and API neutrality tests.
- Added a scoped permanent architecture allowlist for the required code `narrative_generation_v1`; no public API exposure was added.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 mandatory family codes | `MANDATORY_ASTROLOGY_GRAPH_FAMILY_CODES`; `ASTROLOGY_GRAPH_FAMILY_DECLARATIONS`. | Registry pytest and full backend pytest. | PASS |
| AC2 required metadata | `AstrologyGraphFamilyMetadata` dataclass with all required fields and explicit cache blocker on blocked families. | Registry pytest and full backend pytest. | PASS |
| AC3 natal graph linkage | `resolve_astrology_graph_definition("natal_chart_v1")` maps to existing natal graph builder. | Registry pytest, natal graph pytest, full backend pytest. | PASS |
| AC4 temporal astronomical blockers | Temporal families, including `profection_v1`, use `BLOCKED_BY_ASTRONOMICAL_PROOF` and `ASTRONOMICAL_PROOF_BLOCKER`. | `test_temporal_families_are_blocked_by_astronomical_proof`. | PASS |
| AC5 duplicate rejection | `_build_registry()` and `build_astrology_graph_family_registry()`. | `test_duplicate_family_codes_are_rejected`. | PASS |
| AC6 unknown rejection | `get_astrology_graph_family()` raises explicit registry error. | `test_unknown_family_code_is_rejected_without_fallback`. | PASS |
| AC7 public API unchanged | No route/API file modified; API neutrality test added. | API neutrality pytest, `app.openapi()`, `app.routes`, and negative scans. | PASS |
| AC8 persisted evidence | `evidence/validation.md`, `evidence/openapi-routes.md`, `evidence/family-registry.md`. | Evidence files exist and capsule validation rerun. | PASS |

## Files changed

- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `backend/tests/architecture/test_astrology_runtime_boundary.py`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/01-execution-brief.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/04-target-files.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/05-implementation-plan.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/06-validation-plan.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/09-dev-log.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/validation.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/openapi-routes.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/family-registry.md`
- `_condamad/stories/story-status.md`

## Files deleted

- None from the product source tree.
- A mistakenly generated parallel CONDAMAD capsule was removed after copying required generated files into the target CS-246 capsule.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`.
- Updated `backend/tests/architecture/test_api_contract_neutrality.py`.
- Updated `backend/tests/architecture/test_astrology_runtime_boundary.py` for the required CS-246 `narrative_generation_v1` code exception.

## Commands run

- `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-246-canonical-astrology-graph-family-registry` - PASS before implementation after capsule repair.
- `ruff format backend\app\domain\astrology\runtime\astrology_graph_family_registry.py backend\tests\unit\domain\astrology\test_astrology_graph_family_registry.py backend\tests\architecture\test_api_contract_neutrality.py backend\tests\architecture\test_astrology_runtime_boundary.py` - PASS.
- `ruff check backend\tests\unit\domain\astrology\test_astrology_graph_family_registry.py --fix` - PASS.
- `ruff check backend` - PASS.
- Targeted registry, natal graph, API neutrality and runtime boundary pytest - PASS, 23 passed.
- `python -B -m pytest -q backend\tests` - PASS, 881 passed, 201 deselected.
- `python -B -c "from app.main import app; assert 'AstrologyGraphFamily' not in str(app.openapi())"` - PASS.
- `python -B -c "from app.main import app; assert not any('graph-family' in getattr(r, 'path', '') or 'graph_family' in getattr(r, 'path', '') for r in app.routes)"` - PASS.
- Runtime registry family-code scan - PASS, expected scoped matches.
- Public API, frontend and migration registry-exposure scan - PASS, no matches; exit code 1 interpreted as no matches.
- `rg -n "astrology_graph_family_registry|ASTROLOGY_GRAPH_FAMILY_REGISTRY" backend\app backend\tests -g "*.py"` - PASS, canonical module and targeted tests only.
- `git diff --check` - PASS.
- Cache cleanup scan for `__pycache__`, `.pytest_cache`, and `.ruff_cache` under touched backend astrology/runtime and test roots - PASS, no matches after cleanup.

## Commands skipped or blocked

- `rg ... backend\alembic ...` - not applicable because `backend\alembic` does not exist; rerun against `backend\migrations`.
- Frontend validations - not run because the story explicitly forbids frontend changes and no frontend files changed.
- Local app server startup - not run; this story is an internal backend-domain registry with no runtime route or UI behavior change. API neutrality is covered by `TestClient`, `app.routes`, and `app.openapi()`.

## DRY / No Legacy evidence

- One canonical registry module owns family metadata.
- No compatibility shim, alias, re-export, duplicate registry, or silent fallback was added.
- Duplicate family codes and unknown lookup codes fail explicitly.
- API/frontend/migration scan for registry exposure returned no matches.
- Existing dirty files unrelated to CS-246 were preserved and not reverted.

## Diff review

- Reviewed scoped diff for runtime registry and updated tests.
- New files are limited to the canonical registry, registry tests, and CS-246 evidence.
- Public API route files, frontend files, DB models, and migrations were not modified.
- `git diff --stat` was run; untracked files are not represented in git stat output.

## Final worktree status

- Final `git status --short --untracked-files=all` shows CS-246 changes plus preserved pre-existing context.
- CS-246 tracked changes: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`, `_condamad/stories/story-status.md`, `backend/tests/architecture/test_api_contract_neutrality.py`, `backend/tests/architecture/test_astrology_runtime_boundary.py`.
- CS-246 untracked additions: registry module, registry test, generated capsule files, and evidence files listed above.
- Preserved pre-existing context still dirty/untracked: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`, `.agents/skills/condamad-product-architecture/**`, and `_story_briefs/cs-246..cs-254`.

## Remaining risks

- Future stories must decide detailed trace/cache contracts for non-natal families before execution is enabled.
- The required `narrative_generation_v1` family code needs the existing structural-runtime allowlist to coexist with the current architecture token guard; this is documented and tested.

## Suggested reviewer focus

- Confirm the registry metadata is specific enough for CS-247/CS-248 without over-specifying future temporal implementations.
- Confirm the scoped architecture allowlist for `narrative_generation_v1` is acceptable and does not dilute the runtime boundary guard.
