# Implementation Review - CS-405 cloture-qa-live-lecture-natale

Verdict: BLOCKED

## Review Scope

- Story: `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/00-story.md`
- Source brief: `_story_briefs/cs-400-cloturer-qa-live-richesse-et-non-regression-lecture-natale.md`
- Tracker row: `_condamad/stories/story-status.md` row `CS-405`
- Guardrails: `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-129`, `RG-149` to `RG-158`
- Implementation evidence: generated final evidence, closure report, backend/frontend validations, browser QA artifacts and runtime assembly configuration.

## Findings

### F-001 - Basic live runtime resolved the Free/V1 assembly

Status: FIXED

The previous CS-405 evidence showed Basic `complete` returning `schema_version = "v2"` without
`narrative_natal_reading_v1`. The local runtime had no published `natal/interpretation/basic`
assembly, so Basic could fall through to the Free assembly instead of the complete V3 contract.

Fix:

- Added `natal/interpretation/basic -> natal_interpretation` to
  `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`.
- Added regression coverage in `backend/tests/llm_orchestration/test_runtime_convergence.py`.
- Applied the seed locally; the active SQLite DB now reports:
  - `basic published natal_interpretation AstroResponse_v3 3`
  - `free published natal_interpretation_short AstroResponse_v1 1`
  - `premium published natal_interpretation AstroResponse_v3 3`

Validation:

- `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; ...` -> PASS.
- `python -B -m pytest -q tests/llm_orchestration/test_runtime_convergence.py` -> PASS, 5 passed.
- `python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or quota or theme_astral)"` -> PASS, 30 passed.
- `python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py app/tests/integration/test_natal_interpretation_endpoint.py --tb=short` -> PASS, 24 passed.

### F-002 - Closure evidence is still not clean after the config fix

Status: BLOCKED

The story requires live QA closure for Free, Basic and Premium, desktop/mobile screenshots and a
positive CS-400 report. Current persisted evidence still contains the earlier blocked browser/API
run: Basic screenshots have `accordionCount = 0`, Free/Premium live QA are absent, and the report is
intentionally `BLOCKED`.

Fresh Basic API replay on 2026-05-31 after the Basic assembly correction still returns:

- `schema = "v2"`
- `validation_status = "rejected"`
- `narrative_natal_reading_v1 = false`
- `chapter_count = 0`
- `sources_count = 0`
- `remaining = 1`

Required next proof before `done`:

- Restart local backend/frontend after the Basic assembly correction.
- Re-run authenticated Free, Basic and Premium QA.
- Regenerate screenshots under `output/playwright/`.
- Replace the blocked API/browser evidence with passing evidence showing Basic V3 narrative
  accordions, five chapters and non-empty sources.
- Update `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md` only after the live proof is
  clean.

## Validation Summary

- Backend lint: PASS.
- Backend targeted natal regression tests: PASS.
- Backend long entitlement/endpoint tests: PASS.
- Frontend targeted tests: PASS, 90 passed.
- Frontend lint: PASS.
- Frontend build: PASS.
- Fresh Basic API live QA after the seed correction: FAIL product assertion, still `v2`/`rejected`
  without `narrative_natal_reading_v1`.
- Fresh browser live QA and Free/Premium replay after the seed correction: NOT RUN because the
  Basic API runtime path remains blocked, so AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC11 and AC13
  cannot be marked clean.

## Tracker Decision

`_condamad/stories/story-status.md` remains `ready-to-dev` because the CONDAMAD tracker only accepts
`ready-to-dev`, `ready-to-review` and `done`; this fresh implementation review is not clean enough
for `done`.

## Propagation Decision

No-propagation. The reusable guard is local to the seed and covered by the new regression test; no
new registry invariant is needed.
