# Implementation Review - CS-285 structured-facts-v1-builder

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md`
- Source brief: `_story_briefs/cs-285-implement-structured-facts-v1-builder.md`
- Tracker row: `_condamad/stories/story-status.md` entry `CS-285`
- Implementation: `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- Tests and guards:
  - `backend/tests/unit/domain/astrology/test_structured_facts_v1_builder.py`
  - `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`
  - `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`

## Findings Fixed

| Finding | Fix | Validation |
|---|---|---|
| `excluded_surfaces` still emitted text-like forbidden labels. | Replaced labels with neutral category names and strengthened the unit assertion. | Targeted `rg` over builder, test and sample returned no matches; unit test PASS. |
| Full pytest failed because the new builder referenced sign profile data without doctrine-governance declaration. | Added `structured_facts_v1_builder.py` to governed astrology rule surfaces. | Architecture guard PASS; full pytest PASS. |

## Validation Results

- PASS: `ruff check .`
- PASS: `python -B -m pytest -q tests/unit/domain/astrology/test_structured_facts_v1_builder.py --tb=short` (7 passed)
- PASS: `python -B -m pytest -q tests/unit/domain/astrology/test_structured_facts_v1_builder.py tests/architecture/test_astrology_doctrine_governance_guardrails.py --tb=short` (9 passed)
- PASS: `python -B -m pytest -q --tb=short` (3322 passed, 1 skipped, 1204 deselected)
- PASS: public surface guards: no `structured_facts_v1` OpenAPI exposure and no `structured_facts` route path.
- PASS: CONDAMAD story validation, strict lint and capsule validation.

All Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Fresh Review Result

No remaining actionable issue found. AC1-AC8 are covered by implementation,
tests, architecture/public-surface guards and persisted evidence.

## Propagation

No reusable learning propagation required; the corrections are local to CS-285
implementation evidence and the existing doctrine-governance registry.

## Residual Risk

The next persistence or audit consumer should confirm the exact payload shape
before treating `hash_input` as a cross-feature contract.
