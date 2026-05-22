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
- The implementation validation commands remain for the future dev-story run.

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
