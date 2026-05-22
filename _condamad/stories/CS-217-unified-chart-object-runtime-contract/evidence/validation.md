<!-- Evidence initiale de redaction pour CS-217. -->

# CS-217 Validation Evidence

## Story Writing Baseline

- Skill used: `condamad-story-writer`.
- Story path:
  `_condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md`.
- Status target: `ready-to-dev`.
- Registry consulted: `_condamad/stories/story-status.md`.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`.

## Story Validation

Initial validation attempt:

- Result: FAIL before correction.
- Correction summary: switched primary archetype to `custom`, added explicit
  AST guard/runtime markers, added literal Contract Shape markers, and moved
  purity evidence to the architecture guard test.

Commands must be rerun after any story or tracker edit:

```powershell
.\.venv\Scripts\Activate.ps1
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md
python -B C:\dev\tools\rust_codex_orchestrator\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad/stories/CS-217-unified-chart-object-runtime-contract/00-story.md
```

Final story-validation run after corrections:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

Notes:

- All Python validation commands were run after activating `.venv`.
- Implementation validation completed on 2026-05-22 in the dev-story run.

## Editorial Review Cycle

Review on 2026-05-22:

- Structural review: issues found and corrected.
- Prose review: issues found and corrected.
- Correction summary:
  - clarified that the runtime source of truth is
    `build_chart_object_runtime_data`, not a non-required
    `ChartObjectRuntimeBuilder` class;
  - clarified the `supports_dignities` rule: the capability can be true only
    when `payloads.dignity` is present; otherwise the builder must keep the
    capability false and document the decision;
  - replaced ambiguous wording around special-case calculators and several
    English prose sentences where the French version improved comprehension;
  - restored Condamad-required literal markers in English after validation
    proved they are parser contracts.

Second review after correction:

- Structural review: no remaining substantive issue identified.
- Prose review: no remaining comprehension issue identified.
- Validation commands must remain PASS after any future story edit.

## Brief Alignment Review

Review on 2026-05-22 against the initial CS-217 brief:

- Alignment result before correction: mostly aligned, with three wording gaps.
- Corrections applied:
  - made noeuds and Lilith explicit as existing configured astral points;
  - added `fixed_stars` to the parallel-family risk statement while keeping
    advanced fixed-star work out of scope;
  - clarified that CS-217 represents houses through `HOUSE_CUSP` objects and
    does not create a distinct `HOUSE` runtime object without user decision.
- Alignment result after correction: aligned with the brief objective,
  architecture decision, central capability/payload rule, CS-217 scope,
  out-of-scope limits, acceptance criteria and progressive guardrail boundary.
- Validation after correction:
  - `condamad_story_validate.py`: PASS.
  - `condamad_story_validate.py --explain-contracts`: PASS.
  - `condamad_story_lint.py`: PASS.
  - `condamad_story_lint.py --strict`: PASS.

## Implementation Validation

All Python commands below were run from the repository root after activating
`.\.venv\Scripts\Activate.ps1`.

### Tests and Quality

- `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`:
  PASS, 9 tests passed before review fixes.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py backend/tests/unit/domain/astrology/test_natal_result_contract.py`:
  PASS, 8 tests passed before review fixes.
- `ruff format backend`: PASS.
- `ruff check backend`: initially failed on import ordering, then PASS after
  `ruff check backend --fix`.
- `pytest -q`: initially failed because the architecture test contained the
  literal deprecated namespace guard string; corrected without weakening the
  guard. Final rerun after review fixes: PASS, 2952 passed, 1 skipped, 1177
  deselected.
- Final targeted rerun after accepted review fixes:
  `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py backend/tests/unit/domain/astrology/test_natal_result_contains_configured_points.py backend/tests/unit/domain/astrology/test_natal_result_contract.py`:
  PASS, 18 tests passed.
- Local app import check:
  `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -B -c "from app.main import app; print(app.title)"`:
  PASS, printed `horoscope-backend`.
- Note: one attempted app import from `backend/` used the wrong relative venv
  activation path and printed a PowerShell activation error before the import.
  It is not counted as validation evidence; the command above is the corrected
  venv-activated run.

### Scans and Diff Evidence

- Forbidden dependencies in the new runtime/builder modules: zero hits.
- Forbidden public surfaces in the new runtime/builder modules: zero hits.
- `calculability` in scoped runtime/builder/tests: zero hits.
- Forbidden `object_type` branches in business calculators: zero hits.
- `chart_objects|ChartObjectRuntimeData` in API/infra/services/frontend:
  zero hits.
- `Select-String "RG-144" _condamad/stories/regression-guardrails.md`: PASS.
- Adjacent diff over planetary conditions, dignities, dominance, advanced
  conditions, interpretation, interpretation adapters, `json_builder.py`, API,
  infra, migrations and frontend: empty.

### Review/Fix Loop

- Independent review iteration 1 accepted two code findings:
  - `supports_house_position` required a typed payload. Fixed by adding and
    validating `ChartObjectHousePositionPayload`.
  - `supports_motion=True` advertised absent motion facts in the simplified
    engine. Fixed by making motion capability conditional and rejecting empty
    motion payloads.
- Evidence findings were resolved by updating generated traceability, final
  evidence and code-review evidence.
- Review closure on 2026-05-22 reran the targeted tests, Ruff, story
  validate/lint commands, full `pytest -q` and app import check after activating
  `.venv`; all passed. A stale evidence sentence saying no commit or push was
  requested was removed because the requested `condamad-review-fix-story`
  closure requires commit and push after a clean review.
- Feedback-loop routing: no propagation. Findings were local CS-217 contract
  corrections already covered by the new tests and `RG-144`.
