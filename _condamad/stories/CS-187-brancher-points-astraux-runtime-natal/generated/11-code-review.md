# CONDAMAD Code Review — CS-187-brancher-points-astraux-runtime-natal

## Review target

- Story key: `CS-187-brancher-points-astraux-runtime-natal`
- Capsule: `_condamad/stories/CS-187-brancher-points-astraux-runtime-natal/`
- Closure class: full-closure backend runtime story.
- Frontend surface: non-applicable.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current tracked diff and untracked CS-187 files.
- Targeted validation commands and guard scans run on 2026-05-18.

## Diff summary

The implementation adds typed runtime contracts for astral points, maps the
`astral_point_*` DB rows into `AstrologyRuntimeReference`, resolves point
calculation instructions, exposes normalized `NatalResult.points[]`, adds an
explicit `include_points_in_aspects` option, records before/after evidence, and
adds backend tests/guards.

Unrelated dirty file left untouched: `docs/recherches astro/2026-05-18-calcul-theme-astrologique.md`.

## Review iteration 1 findings

### CR-1 Medium - Aspect orb rules did not validate targeted point codes

- Bucket: patch
- Location: `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- Source layer: acceptance / edge / regression guardrail
- Evidence: `aspect_orb_rules` validation rejected orphan `source_planet_code` and
  `target_planet_code`, but after CS-187 the runtime can also carry
  `source_point_code` and `target_point_code` without checking them against
  `reference.astral_points` or angle points.
- Impact: a DB-backed point-specific orb rule could reference a missing point and
  still enter the runtime, weakening `RG-115` and making point aspects silently
  fall back to less specific rules.
- Suggested fix: validate `source_point_code` and `target_point_code` against the
  runtime astral point and angle-point catalogs, and add a regression test.

### CR-2 Medium - Full backend guards were stale after CS-187 seed/API changes

- Bucket: patch
- Location: `backend/app/services/prediction/reference_seed_service.py`,
  `_condamad/stories/harden-api-adapter-boundary-guards/router-sql-allowlist.md`
- Source layer: validation / regression guardrail
- Evidence: full `pytest -q` initially failed because the prediction reference
  seed expected `astral_point_aliases == 15` while CS-187 adds two DB-backed
  SwissEph aliases, and the exact SQL boundary allowlist line numbers for
  `public/astrology_engine.py` were stale after the API request field addition.
- Impact: story-level targeted tests passed, but repository-level guards failed.
- Suggested fix: update the expected seed count to 17 and realign only the exact
  line-number metadata for the touched router allowlist rows.

## Fix evidence

- Added point-code validation in `AstrologyRuntimeReferenceRepository._validate()`.
- Added `test_repository_integrity_rejects_orphan_aspect_point_rule`.
- Updated `EXPECTED_COUNTS["astral_point_aliases"]` from 15 to 17.
- Realigned `router-sql-allowlist.md` line numbers for the touched astrology
  engine router without adding new SQL debt.
- Generated true `before` artifacts from a detached HEAD worktree at `989acc7a`:
  - `evidence/astral-points-runtime-before.json`
  - `evidence/natal-payload-before.json`
- Updated final evidence to remove the reconstructed-baseline limitation.

## Review iteration 2 findings

No actionable findings.

## Acceptance audit

- AC1-AC11: PASS.
- `AC11` is now backed by real before/after runtime artifacts:
  - before: detached HEAD worktree at `989acc7a`
  - after: current implementation runtime/service execution
- `RG-095`, `RG-107`, `RG-108`, `RG-111`, `RG-112`, `RG-113`, `RG-114`, `RG-115`: preserved.

## Validation audit

- `ruff check .` from `backend/`: PASS.
- `ruff format --check .` from `backend/`: PASS.
- Consolidated targeted story suite: PASS, 79 passed, 1 deselected.
- Full backend suite `pytest -q`: PASS, 2634 passed, 1 skipped, 1176 deselected.
- Story validate: PASS.
- Story lint strict: PASS.
- No-legacy scans for flat point fields, local point catalogs, and editorial contamination: zero hits.
- Runtime dict scan: only pre-existing non-point hits in aspect/house runtime helpers.
- `git diff --check`: PASS with line-ending warnings only.

## DRY / No Legacy audit

- No local `ASTRAL_POINTS`, `POINT_VARIANTS`, `NODE_VARIANTS`, or `LILITH_VARIANTS` catalogs found.
- No flat `NatalResult.true_node`, `NatalResult.mean_node`, or `NatalResult.lilith` fields found.
- Resolver requires DB-backed `engine_key` for direct variants and uses typed derived instructions for oppositions/perigee.
- No editorial keyword/profile model imported into raw natal calculation.

## Residual risks

- Backend startup checked on `http://127.0.0.1:8017/openapi.json`: PASS.
- Full `pytest -q` passed.

## Verdict

CLEAN.
