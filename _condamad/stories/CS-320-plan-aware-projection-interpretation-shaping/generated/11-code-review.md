# Editorial Review CS-320

Verdict: CLEAN

## Scope

- Story reviewed: `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/00-story.md`
- Source brief: `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- Tracker row: `_condamad/stories/story-status.md` entry for `CS-320`
- Review type: pre-implementation story-contract drafting review

## Review Summary

- The story preserves the source brief decision that all B2C plans execute full projection calculation.
- The story makes differentiation post-calculation through LLM input selection, editorial depth and frontend visibility rules.
- The contract explicitly names `free`, `basic`, `premium`, `LLMInputSelection`, `EditorialDepthProfile` and `FrontendVisibilityRules`.
- The brief-mandated prerequisite artifacts are now explicit in story routing, inspection targets and references.
- The implementation scope is now aligned with the brief: CS-320 defines the contract, owners and future validations without requiring
  immediate backend builder changes, frontend rendering changes, prompt implementation or provider integration.
- React is constrained to consume backend-shaped visibility metadata and must not own a local entitlement matrix.
- The validation plan covers backend runtime execution, builder shaping behavior, frontend rendering and route/OpenAPI neutrality.
- Selected guardrails `RG-002`, `RG-003`, `RG-022` and `RG-041` are scoped consistently with the story surface.

## Findings

No actionable drafting issue found.

## Issues Fixed

- Source alignment: corrected this review artifact to reference the CS-320 brief.
- Prerequisite routing: added the missing CS-315/CS-317 final evidence paths, public projection contract owner and natal feature page owner.
- Scope alignment: narrowed CS-320 from immediate backend/frontend implementation to contract definition, owner routing and future validation
  guardrails, matching the source brief's included scope and non-goals.

## Validation Evidence

- `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-320-plan-aware-projection-interpretation-shaping\00-story.md`: PASS
- Strict lint command: FAIL on line length only before final wrapping.
- Targeted post-fix line-length check: PASS.
- Both Python commands were run after activating `.\.venv\Scripts\Activate.ps1`.

## Produced Artifacts

- `_condamad/stories/CS-320-plan-aware-projection-interpretation-shaping/generated/11-code-review.md`

## Closure

- Propagation decision: no-propagation; the review produced only local CS-320 editorial evidence.
- Residual risk: implementation must still produce the required runtime, backend, frontend and evidence artifacts.
