# Review CS-325 audit-pipeline-prompt-llm-natal

Verdict: CLEAN

## Iteration 1

Review scope:

- Story contract: `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md`
- Tracker row: `_condamad/stories/story-status.md`
- Source brief: `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`
- Guardrails checked by scoped IDs: RG-002, RG-022, RG-047, RG-052, RG-041

Finding:

- Validation plan drift: `VC9` used `ruff format .`, which can rewrite files in an audit-only story whose
  operation contract forbids application source and test changes. It must be a non-mutating check.

Fix applied:

- Replaced `VC9` with `ruff format --check .`.

Validation:

- `.venv` activated before Python commands.
- `condamad_story_validate.py`: PASS before fix.
- `condamad_story_lint.py --strict`: PASS before fix.

## Iteration 2

Verdict: CHANGES_REQUESTED

Finding:

- Brief primitive gap: the story did not explicitly require the audit to cover `free/basic/premium`
  alongside `free_short`, `short`, `complete` and thematic modules.
- Brief primitive gap: the legacy question from the brief named `/users`, simplified legacy payload,
  fallback and schema v1/v2/v3 compatibility, but those items were not explicit enough in the contract.

Fix applied:

- Added `free/basic/premium` to target state, domain scope, named primitives and implementation tasks.
- Added `/users`, simplified legacy payload, fallback and schema v1/v2/v3 compatibility to named
  primitives, no-legacy constraints and validation evidence.

Status:

- Requires fresh validation and a third editorial review after the fix.

## Iteration 3

Verdict: CLEAN

Review scope:

- Story contract and source alignment for CS-325.
- Tracker row with source brief and `ready-to-dev` status.
- Scoped guardrails: RG-002, RG-022, RG-047, RG-052, RG-041.

Clean review evidence:

- The story now names every required brief primitive, including runtime input fields, branch tiers,
  `chart_json_in_prompt`, `Technical Data`, `/users`, legacy payload, fallback and schema v1/v2/v3.
- The operation contract remains audit-only and forbids backend, frontend, prompt and test edits.
- Validation commands are non-mutating for story readiness; `ruff format --check .` replaces formatting writes.
- Tracker row already has the expected story path, source brief, `ready-to-dev` status and date `2026-05-26`.

Validation:

- `.venv` activated before Python commands.
- `condamad_story_validate.py`: PASS after fixes.
- `condamad_story_lint.py --strict`: PASS after fixes.
- Targeted story scan confirmed corrected branch, legacy and non-mutating validation primitives.

Propagation:

- no-propagation; findings were local story-contract corrections with no reusable guardrail or skill update.

Residual risk:

- None identified for story drafting. Implementation still must read the runtime sources and produce audit evidence.
