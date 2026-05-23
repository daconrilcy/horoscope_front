---
name: condamad-story-draft-review
version: 1
description: >
  Run an adversarial CONDAMAD editorial review of a drafted story contract.
  This skill is not an application-code
  review skill: it reviews story wording, acceptance criteria, validation
  evidence, guardrail mapping, scope, non-goals, and review artifact paths.
  Use when the user asks to review a generated CONDAMAD story, story capsule,
  BMAD story draft, or story contract with Codex-native review discipline.
  Invoke condamad-feedback-loop after the verdict when review evidence reveals
  reusable process learning, repeated mistakes, regression guardrail gaps, or a
  needed skill/AGENTS.md adjustment.
---

<!-- Skill CONDAMAD de revue redactionnelle de story, concu pour Codex. -->

# CONDAMAD Story Draft Review

CONDAMAD Story Draft Review is the adversarial review companion to
`condamad-story-writer`. It intervenes after story drafting and asks one
question: **is this story contract ready for implementation, with clear scope,
atomic acceptance criteria, validation evidence, and regression guardrails?**

Do not interpret the review artifact name as permission to review or edit
application code in this workflow.

Follow the instructions in `./workflow.md`.

## Required References

For story-contract review, load:

- `workflow.md`
- `references/review-doctrine.md`
- `references/finding-taxonomy.md`
- `references/codex-modern-review-guidance.md`
- `../condamad-regression-guardrails/SKILL.md`

In fast/non-interactive review, load only `workflow.md` first. Read the broader
references above only when a concrete story-contract finding requires their
doctrine. Do not load `../condamad-regression-guardrails/SKILL.md` when the
registry already exists and the story already lists scoped `RG-XXX` IDs.

## Non-Negotiable Behavior

- Review only one target at a time.
- Do not review or edit application implementation files. This skill reviews
  story drafting artifacts only.
- Writing `generated/11-code-review.md` is allowed only when a CONDAMAD capsule
  exists.
- Findings must be evidence-backed and include story/capsule file references
  when possible.
- Treat unclear scope, compound ACs, weak evidence, missing non-goals,
  mismatched review artifact paths, and guardrail drift as review risks.
- Do not return `CLEAN` when required validation evidence is missing.
- Do not treat skipped commands as passed.
- Do not hide findings because the user asked for a "quick" review.
- Ensure `_condamad/stories/regression-guardrails.md` exists. Do not read or
  paste the full registry in normal review work; resolve only IDs already
  named by the story/capsule or use a scoped resolver/search for the reviewed
  paths, routes, operations, and contracts. Treat missing applicable guardrail
  evidence as a review finding.
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
