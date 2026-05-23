---
name: condamad-code-review
version: 1
description: >
  Run an adversarial CONDAMAD code review after a story implementation. Use
  when the user asks to review a completed story, a CONDAMAD story capsule, a
  BMAD story in review, a branch diff, staged changes, or uncommitted changes
  with Codex-native review discipline. Optimized for modern Codex-class models
  and GPT-5.4/5.5: repository grounded, evidence-first, adversarial, and
  compatible with sessions where subagents are optional or unavailable. Invoke
  condamad-feedback-loop after the verdict when review evidence reveals
  reusable process learning, repeated mistakes, regression guardrail gaps, or a
  needed skill/AGENTS.md adjustment.
---

<!-- Skill CONDAMAD de revue adversariale post-story, concu pour Codex. -->

# CONDAMAD Code Review

CONDAMAD Code Review is the adversarial review companion to
`condamad-dev-story`. It intervenes after a story implementation and asks one
question: **is this story truly ready to merge, with evidence, without legacy by
inertia, and without hidden regression risk?**

Follow the instructions in `./workflow.md`.

## Required References

Before reviewing, load:

- `workflow.md`
- `../condamad-dev-story/references/condamad-principles.md`
- `references/review-doctrine.md`
- `references/finding-taxonomy.md`
- `references/codex-modern-review-guidance.md`
- `../condamad-regression-guardrails/SKILL.md`

## Non-Negotiable Behavior

- Review only one target at a time.
- Do not edit implementation files unless the user explicitly asks for fixes.
- Writing `generated/11-code-review.md` is allowed only when a CONDAMAD capsule
  exists.
- Findings must be evidence-backed and include repository-relative file
  references when possible.
- Treat SOLID, DRY, KISS, and YAGNI violations as review risks when they affect
  maintainability, responsibility boundaries, duplication, or unnecessary
  complexity.
- Do not return `CLEAN` when required validation evidence is missing.
- Do not treat skipped commands as passed.
- Do not hide findings because the user asked for a "quick" review.
- Ensure `_condamad/stories/regression-guardrails.md` exists, read it, and
  treat missing applicable guardrail evidence as a review finding.
- When reviewing a tracked CONDAMAD story, update
  `_condamad/stories/story-status.md` after the verdict using the same registry
  contract as `condamad-story-writer`.
- When review evidence reveals reusable process learning, repeated mistakes, or
  a needed skill/guardrail/AGENTS.md adjustment, invoke
  `$condamad-feedback-loop` after the review verdict and record whether the
  result was propagated or classified as no-propagation. If explicit skill
  invocation is unavailable, read `../condamad-feedback-loop/SKILL.md` and
  follow its workflow. Do not let the feedback loop hide or downgrade review
  findings.
