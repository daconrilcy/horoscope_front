# Execution Brief

## Story

- Story key: `CS-200-hellenistic-medieval-golden-cases`
- Source: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md`
- Status at start: `ready-to-dev`

## Objective

Implement a backend-only golden regression suite for traditional Hellenistic /
medieval astrology contracts delivered by CS-197, CS-198 and CS-199.

## Boundaries

- Modify tests and persistent story evidence only.
- Do not modify production astrology doctrine unless a blocking bug is proven.
- Do not modify frontend, API routes, migrations, seeds, dependencies or LLM code.
- Use runtime references and canonical domain services; do not create a second doctrine engine.

## Required Outputs

- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- Test-local fixture helpers when useful.
- Evidence files under `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/`.
- Completed final evidence and story status update.

## Completion Definition

- G1-G12 are covered by targeted assertions and curated snapshot evidence.
- Required pytest, ruff and scan commands are run after activating `.venv`.
- `generated/10-final-evidence.md` and `generated/11-code-review.md` are complete.
- `_condamad/stories/story-status.md` is synchronized.

## Halt Conditions

- A golden case requires changing doctrine or public contracts.
- Required validation repeatedly fails with no safe test-only correction.
- Implementing the story would require a forbidden path change.
