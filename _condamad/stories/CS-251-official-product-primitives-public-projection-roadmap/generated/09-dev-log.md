# Dev Log

## Preflight

- Initial `git status --short`: dirty before CS-251 with prior CS-246 through
  CS-250 story/code artifacts and `_condamad/stories/story-status.md` already
  modified.
- Current branch: not changed.
- Existing dirty files: treated as pre-existing; CS-251 edits were limited to
  the roadmap doc, two backend tests, CS-251 evidence/generated files and the
  CS-251 row in `story-status.md`.

## Search evidence

- `story-status.md` row verified CS-251 Path and source brief.
- RG-002 and RG-003 resolved through targeted `Select-String`.
- CS-238/CS-244 audit excerpts loaded for raw runtime bans, audience needs,
  CS-255/CS-256/CS-257 sequencing and fixed-star blocker.

## Implementation notes

- Added `docs/architecture/official-product-primitives-public-projections.md`.
- Added `evidence/product-primitives.json` as machine-readable primitive
  decision snapshot.
- Expanded public/OpenAPI guards in existing backend tests; no route, serializer,
  frontend, DB, auth, i18n, style, build, migration, temporal runtime or LLM
  narration code changed.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py ... --story-key CS-251-official-product-primitives-public-projection-roadmap --with-optional` | PASS | Filled required generated capsule files. |
| `condamad_validate.py _condamad/stories/CS-251-official-product-primitives-public-projection-roadmap` | PASS | Capsule structure valid. |
| `ruff format <2 modified python test files>` | PASS | Scoped formatting. |
| `ruff check backend` | PASS | Static check. |
| `python -B -m pytest -q <3 targeted test files>` | PASS | 17 passed, 3 deselected. |
| `rg` roadmap primitive/layer scans | PASS | Required names, layers and blocker found. |
| `python -B -c app.openapi()/app.routes checks` | PASS | Forbidden terms absent. |
| `python -B -m pytest -q` | PASS | 3159 passed, 1 skipped, 1182 deselected. |

## Issues encountered

- The first helper run without explicit `--story-key` created a duplicate
  derived capsule path. It was removed after path verification inside the
  workspace.

## Decisions made

- Fixed-star contacts remain `needs-user-decision` because no product decision
  selects public or gated exposure.
- `interpretation_input` is classified as LLM-only, not a public frontend/API
  payload.
- Roadmap uses CS-255, CS-256 and CS-257 as separated future API/client/UI
  layers instead of bundling implementation work.

## Final `git status --short`

- Recorded in `generated/10-final-evidence.md`.
