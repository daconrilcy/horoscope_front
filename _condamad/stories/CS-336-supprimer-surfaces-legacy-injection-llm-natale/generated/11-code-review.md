# Editorial Review - CS-336 supprimer-surfaces-legacy-injection-llm-natale

Verdict: CLEAN

## Scope Reviewed

- Story: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/00-story.md`.
- Source brief: `_story_briefs/cs-336-supprimer-surfaces-legacy-injection-llm-natale.md`.
- Tracker row: `_condamad/stories/story-status.md`, story `CS-336`, status `ready-to-dev`.
- Scoped guardrails: `RG-002`, `RG-022`; non-applicable examples were not treated as active blockers.

## Brief Alignment

- The story preserves the brief objective: extinguish legacy natal LLM injection surfaces so `llm_astrology_input_v1` is the only active
  astrology payload carrier.
- The target state, domain boundary, acceptance criteria and tasks explicitly name the brief primitives:
  `chart_json`, `natal_data`, chart-derived `evidence_catalog`, prompt placeholders, input schemas, fallbacks, transition branches,
  adapters, documentation and absence guards.
- The story keeps the brief's non-goals: no frontend work, no public endpoint change, no provider/retry/workflow change outside
  legacy-carrier removal, and no fine editorial prompt rewrite.
- The validation plan includes runtime payload proof, schema/config proof, AST or targeted scan proof, residual occurrence
  classification, OpenAPI neutrality and persisted before/after evidence.

## Findings

No actionable drafting issue found.

## Validation Evidence

- `.\.venv\Scripts\Activate.ps1`
- `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py`
- `_condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale\00-story.md`
  - Result: PASS.
- `.\.venv\Scripts\Activate.ps1`
- `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict`
- `_condamad\stories\CS-336-supprimer-surfaces-legacy-injection-llm-natale\00-story.md`
  - Result: PASS.

## Review Output

- Produced artifact: `_condamad/stories/CS-336-supprimer-surfaces-legacy-injection-llm-natale/generated/11-code-review.md`.
- Issues fixed in this review loop: none; artifact creation is normal review output.
- Propagation decision: no-propagation; no reusable learning beyond this story contract was identified.

## Residual Risk

Aucun risque restant identifie for story drafting. Implementation risk remains covered by the story's required runtime, AST,
OpenAPI and residual-scan evidence.
