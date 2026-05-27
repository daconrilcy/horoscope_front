# CS-341 - Editorial Story Review

<!-- Commentaire global: cet artefact consigne la revue de redaction pre-implementation de la story CS-341. -->

## Verdict

CLEAN.

## Review Scope

- Story: `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/00-story.md`.
- Source brief: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`.
- Tracker row: `_condamad/stories/story-status.md`, source column matching the source brief.
- Review mode: compact pre-implementation story-contract review.

## Alignment Checks

- The objective covers both sides of the brief: removing prompt-visible `evidence` and keeping backend validation/audit evidence.
- The target state names prompt-visible `facts`, `signals`, `limits`, and `shaping`, with `evidence` excluded from provider payloads.
- Backend-only material is explicit: `evidence`, `evidence_refs`, `grounding_status`, `validation_owner`, provenance, and hashes.
- Acceptance criteria cover empty evidence payload removal, audit persistence, positive validation, unsupported claims, ignored limits, CS-339/CS-340
  provenance/hash guards, and CS-336/CS-338 legacy prompt carrier guards.
- Implementation tasks and expected files route ownership to role mapping, gateway projection, post-generation validation, audit, and tests.
- The contract shape now names the minimal expected LLM output primitives needed by backend validation: identifiable sections or items, checkable claims,
  limit handling, absence of contradictions, and validation status or rejection evidence when supported by the existing schema.
- Non-goals preserve the brief exclusions: no frontend, public API, real provider call, hash semantic change, migration, or prompt rewrite.
- Regression guardrails record active backend guardrails and classify frontend-only guardrails as non-applicable.

## Findings

No actionable drafting issue found.

## Issues Fixed In This Pass

- Clarified the minimal expected LLM output contract required by the source brief.
- Split provenance/hash/audit-only guard coverage from legacy `chart_json` and `natal_data` carrier coverage in ACs and tasks.

## Produced Artifacts

- Updated this review artifact: `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/generated/11-code-review.md`.

## Validation Results

- `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-341-evidence-validation-hors-prompt-llm-natal\00-story.md`: PASS.
- `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-341-evidence-validation-hors-prompt-llm-natal\00-story.md`: PASS.
- Python commands were run after `.\.venv\Scripts\Activate.ps1`.

## Propagation

No propagation. The review produced only local story-review evidence and no reusable learning that requires guardrail, skill, or AGENTS.md updates.

## Residual Risk

Aucun risque restant identifie for story drafting. Implementation risk remains owned by the future development cycle and its runtime tests.
