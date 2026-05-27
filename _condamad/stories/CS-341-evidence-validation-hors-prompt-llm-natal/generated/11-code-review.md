# CS-341 - Implementation Review

<!-- Commentaire global: cet artefact consigne la revue d'implementation finale de la story CS-341. -->

## Verdict

CLEAN.

## Review Scope

- Story: `_condamad/stories/CS-341-evidence-validation-hors-prompt-llm-natal/00-story.md`.
- Source brief: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`.
- Tracker row: `_condamad/stories/story-status.md`, path and source brief matched.
- Scope reviewed: backend implementation, tests, evidence artifacts, guardrails, AC alignment, and validation output.

## Iterations

- Iteration 1: one actionable implementation issue found and fixed.
- Iteration 2: fresh implementation review found no remaining actionable issue.

## Finding Fixed

- AC7/AC8 validation weakness: unsupported claims and ignored critical limits were only proven through `unsupported_claims` and
  `ignored_critical_limits` fields supplied by the generated payload. Existing Astro response schemas forbid extra fields, so this did not prove a
  backend-side validation against internal facts and limits.

## Fix Evidence

- `backend/app/services/llm_generation/natal/interpretation_service.py` now passes `llm_astrology_input_v1` into the rejection workflow.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` now checks generated narrative text against internal `facts`,
  `signals`, and `limits` when the internal contract is available.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` now includes backend-driven negative tests that do not depend on LLM marker fields.

## AC Alignment

- AC1-AC3: prompt-visible roles and provider payload exclude `evidence`; empty prompt evidence expectations remain absent.
- AC4-AC5: full internal contract and persistent audit keep evidence refs, grounding status, projection hash, and LLM input hash.
- AC6: grounded evidence refs remain accepted.
- AC7-AC8: unsupported generated content and ignored unavailable surfaces are rejected by backend validation.
- AC9-AC10: CS-339/CS-340 audit-only guards and CS-336/CS-338 legacy prompt carrier guards remain active.
- AC11: story evidence and review artifacts are persisted.

## Validation Results

- `ruff check .`: PASS.
- `pytest -q <CS-341 targeted tests> --tb=short`: PASS, 33 passed, 9 deselected.
- `pytest -q tests --tb=short`: PASS, 1215 passed, 221 deselected.
- `rg -n -F 'prompt_payload["evidence"] == {}' backend\app backend\tests`: PASS, no matches.
- `rg -n -F 'assert "evidence" in prompt_payload' backend\app backend\tests`: PASS, no matches.
- Python commands were run after `.\.venv\Scripts\Activate.ps1`.

## Propagation

No propagation. The correction is local to this story and does not reveal a reusable AGENTS.md, guardrail, or skill update.

## Residual Risk

The backend textual validation is conservative and rule-based; it is not a general semantic verifier for every possible free-text astrology claim.
