<!-- Conseils operationnels pour exploiter les modeles Codex modernes en revue redactionnelle. -->

# Codex Modern Review Guidance

## Why This Skill Differs From BMAD

BMAD's original code-review flow assumes implementation diffs and mandatory
step checkpoints. This CONDAMAD skill is narrower: it reviews the drafted story
contract before implementation. Modern Codex-class models can keep the story,
brief, tracker row, validation output, and scoped guardrails in context without
loading broad implementation doctrine.

## Operating Pattern

1. Build the review target from the story file, tracker row, and source brief.
2. Read only story/capsule artifacts and scoped guardrail IDs.
3. Run adversarial passes as separate mental layers:
   - source alignment;
   - acceptance auditor;
   - validation skeptic;
   - No Legacy / DRY story guard;
   - review artifact path check.
4. Merge and triage findings.
5. Present findings first.

## Subagent Policy

Use subagents only when the current user explicitly asks for sub-agents,
delegation, or parallel agent work. If that authorization is absent, perform the
layers in the main Codex session.

If subagents are authorized:

- make them read-only;
- give each a bounded story-review layer;
- do not let them edit files;
- keep final severity, deduplication, and verdict decisions in the main session.

## Codex Self-Review Loop

Before finalizing, run this internal challenge:

- Could an AC be implemented in two incompatible ways?
- Does any AC lack validator-recognized evidence?
- Does the validation plan prove runtime behavior where the story claims it?
- Is the review artifact path canonical and separate?
- Are non-goals and forbidden paths explicit enough?
- Would a dev agent know exactly what to inspect and modify?

If the answer reveals uncertainty, inspect the story contract again before
reporting.

## Self-Validation Commands For This Skill

Use `python -B` so Python does not generate `__pycache__` files that the package
validator intentionally rejects.

From `.agents/skills/condamad-story-draft-review`:

```bash
python -B scripts/condamad_review_validate.py .
```
