# Implementation Review CS-412

Verdict: CLEAN

## Scope Reviewed

- Story: `_condamad/stories/CS-412-prioriser-faits-natals-basic-salience-calibree/00-story.md`
- Source brief: `_story_briefs/cs-412-prioriser-faits-natals-basic-salience-calibree.md`
- Tracker row: `_condamad/stories/story-status.md`
- Implementation:
  - `backend/app/domain/astrology/interpretation/natal_salience_model.py`
  - `backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`
  - `backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`
  - `backend/tests/fixtures/golden/basic_natal_salience_archetypes.json`
- Evidence:
  - `evidence/salience-before.json`
  - `evidence/salience-after.json`
  - `evidence/validation.txt`
  - `generated/03-acceptance-traceability.md`
  - `generated/10-final-evidence.md`
- Guardrails: `RG-144`, `RG-145`, `RG-147`, `RG-148`, `RG-151`, `RG-156`, `RG-160`, `RG-161`

## Iterations

- Iteration 1 verdict: CHANGES_REQUESTED.
  - Finding: repeated Fire/Water profiles were only declared in the archetype fixture; the model excluded all element balance facts as `single_weak_signal`, which contradicted the brief requirement to calibrate Fire/Water dominant profiles.
  - Fix: `_exclusion_reason` now allows repeated element, sign, modality and node facts while still excluding isolated weak signals.
  - Proof: added tests for Fire/Water repetition, dominant planet and strong constraint coverage.
- Iteration 2 verdict: CLEAN.
  - No remaining actionable implementation, evidence, AC, guardrail or validation issue found.
- Post-alignment verification verdict: CLEAN.
  - Evidence consistency fix: `generated/10-final-evidence.md` now says the implementation review became clean after
    iteration 2, matching this review artifact.
  - No code, AC, scope or source brief change was required.

## AC And Guardrail Result

- AC1-AC14: PASS.
- `RG-144`, `RG-145`, `RG-147`, `RG-148`, `RG-151`, `RG-160`: PASS by consuming `NatalFactGraph` runtime facts and avoiding recalculation.
- `RG-156`: PASS by fixture coverage for the required contrasted archetypes.
- `RG-161`: PASS by pillar-vs-minor tests and forbidden-signal scan.
- Public leakage guard: PASS on bounded public projection, LLM input and structured-facts surfaces.

## Validation Evidence

- PASS: `.\.venv\Scripts\Activate.ps1; ruff format backend\app\domain\astrology\interpretation\natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py`
- PASS: `.\.venv\Scripts\Activate.ps1; ruff check backend\app\domain\astrology\interpretation\natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py`
- PASS: `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py --tb=short` -> 13 passed.
- PASS: `.\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_fact_graph.py backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py backend\tests\unit\domain\astrology\test_basic_natal_salience_archetypes.py --tb=short` -> 18 passed.
- PASS: recalculation, public leak and forbidden-signal `rg` scans in `evidence/validation.txt`.
- PASS: post-alignment rerun on 2026-05-31 of scoped Ruff, targeted salience/fact-graph pytests, story validation,
  strict story lint and bounded scans.

## Closure

- Final status recommendation: `done`.
- Feedback propagation: no-propagation; the correction is local to this story implementation and covered by tests/evidence.
- Residual risk: none identified beyond the bounded public-leak scan noted in final evidence.
