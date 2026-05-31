# Code Review - CS-411 natal-fact-graph-basic-tracable

Verdict: CLEAN

## Scope Reviewed

- Source brief: `_story_briefs/cs-406-construire-fact-graph-natal-basic-tracable.md`.
- Story contract: `_condamad/stories/CS-411-natal-fact-graph-basic-tracable/00-story.md`.
- Tracker row: `_condamad/stories/story-status.md` entry `CS-411`.
- Implementation files:
  - `backend/app/domain/astrology/interpretation/natal_fact_graph.py`
  - `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py`
  - `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph.py`
  - `backend/tests/unit/domain/astrology/test_basic_natal_fact_graph_date_only.py`
  - `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`
- Guardrails reviewed: `RG-144`, `RG-145`, `RG-146`, `RG-147`, `RG-148`, `RG-156`, `RG-160`.

## Review Cycle

- Iteration 1 verdict: CHANGES_REQUESTED.
- Finding F1: date-only charts still emitted a `sign_emphasis_fact` for `asc`, leaking angle-derived material under a non-time family.
- Fix: `natal_fact_graph_builder._object_facts` now suppresses all angle-derived object material when `EligibilityContext.can_use_angles`
  is false, and `test_basic_natal_fact_graph_date_only.py` asserts that `asc` is absent from emitted facts.
- Iteration 2 verdict: CLEAN.

## Acceptance Alignment

- AC1: all required families are covered by the rich fixture and graph contract.
- AC2/AC3: every fact has source paths and deterministic IDs.
- AC4/AC5: date-only gating now excludes angle-derived facts while keeping non-time families.
- AC6: aspect pair identity stays sorted and stable.
- AC7: builder consumes runtime projections and has no local recalculation calls.
- AC8/AC9: internal payload keeps `source_paths`; editorial candidates and public/API/frontend scans do not expose them.
- AC10: story evidence artifacts are present and validated.

## Validation Results

- PASS: `ruff check app\domain\astrology\interpretation\natal_fact_graph_builder.py tests\unit\domain\astrology\test_basic_natal_fact_graph.py tests\unit\domain\astrology\test_basic_natal_fact_graph_date_only.py tests\unit\domain\astrology\test_chart_object_runtime_architecture.py`
- PASS: `ruff check .` -> `All checks passed!`.
- PASS: `ruff format --check .` -> `1743 files already formatted`.
- PASS: `python -B -m pytest -q tests\unit\domain\astrology\test_basic_natal_fact_graph.py tests\unit\domain\astrology\test_basic_natal_fact_graph_date_only.py tests\unit\domain\astrology\test_chart_object_runtime_architecture.py --tb=short` -> `18 passed`.
- PASS: recalculation scan returned zero hits for the fact graph modules and tests.
- PASS: prose-generation scan returned zero hits for the fact graph modules and tests.
- PASS: public `source_paths` scan returned zero hits in `backend\app\api` and `frontend\src`.

## Propagation

- no-propagation: the accepted finding was local to this builder/test surface and is now covered by the date-only regression test.

## Residual Risk

- Aucun risque restant identifie.
