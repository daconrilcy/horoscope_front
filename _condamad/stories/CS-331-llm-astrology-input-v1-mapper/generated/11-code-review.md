# Review CS-331 - llm-astrology-input-v1-mapper

Verdict: CLEAN

## Review Scope

- Target story: `_condamad/stories/CS-331-llm-astrology-input-v1-mapper/00-story.md`.
- Source brief: `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`.
- Tracker row: `_condamad/stories/story-status.md`, status `done`, source brief aligned.
- Implementation owner: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`.
- Tests reviewed: `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` and
  `backend/tests/architecture/test_llm_astrology_input_boundary.py`.
- Evidence reviewed: `evidence/sample-payload.json`, `evidence/validation.txt`,
  `evidence/public-surface-guard.txt`, `evidence/architecture-guard.txt`,
  `generated/10-final-evidence.md`.

## Iteration 1 Finding

- AC5 evidence grounding: the mapper accepted empty `evidence_refs` and produced `grounding_status: not_checked`.
  That did not prove compact evidence refs tied to allowed sources.

## Corrections Applied

- The mapper now emits a compact `projection_version` evidence ref by default, tied to the
  `structured_facts_v1` projection hash.
- The LLM input evidence section now requires evidence validation and returns `grounding_status: grounded`.
- Unit assertions and the persisted sample payload were updated to prove the grounded evidence shape.

## Fresh Review

No actionable issue remains.

- AC1-AC4: mapper, facts, signals and limits align with the story and source brief.
- AC5: evidence refs are compact, hash-backed and validated by `evidence_refs_validation.py`.
- AC6-AC9: shaping and ownership remain separate; complete, missing-data and non-duplication cases are covered.
- AC10-AC11: raw carriers, runtime objects and public API exposure remain excluded.
- AC12: required evidence artifacts are present and updated after the correction.

## Validation Results

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` - PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\unit\domain\astrology\test_structured_facts_v1_builder.py tests\architecture\test_llm_astrology_input_boundary.py --tb=short` - PASS, 18 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q tests --tb=short` - PASS, 1172 passed, 215 deselected.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-331-llm-astrology-input-v1-mapper\00-story.md` - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-331-llm-astrology-input-v1-mapper\00-story.md` - PASS.

## Propagation

No propagation: the correction is local to the CS-331 mapper, tests and evidence.

## Residual Risk

Aucun risque restant identifie.
