---
name: condamad-code-review
description: >
  Run an adversarial CONDAMAD code review after a story implementation. Use
  when the user asks to review a completed story, a CONDAMAD story capsule, a
  BMAD story in review, a branch diff, staged changes, or uncommitted changes
  with Codex-native review discipline. Optimized for modern Codex-class models
  and GPT-5.4/5.5: repository grounded, evidence-first, adversarial, and
  compatible with sessions where subagents are optional or unavailable.
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
- `references/review-doctrine.md`
- `references/finding-taxonomy.md`
- `references/codex-modern-review-guidance.md`

## Non-Negotiable Behavior

- Review only one target at a time.
- Do not edit implementation files unless the user explicitly asks for fixes.
- Writing `generated/11-code-review.md` is allowed only when a CONDAMAD capsule
  exists.
- Findings must be evidence-backed and include repository-relative file
  references when possible.
- Do not return `CLEAN` when required validation evidence is missing.
- Do not treat skipped commands as passed.
- Do not hide findings because the user asked for a "quick" review.
