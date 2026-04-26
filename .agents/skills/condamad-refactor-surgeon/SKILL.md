---
name: condamad-refactor-surgeon
description: >
  Perform exactly one bounded, mono-domain, behavior-preserving refactor with
  explicit refactor type, behavior invariants, DRY / No Legacy constraints,
  validation evidence, negative legacy scans, and reviewer-ready diff evidence.
  Use only when the user explicitly invokes $condamad-refactor-surgeon or asks
  for this CONDAMAD refactor skill by name.
---

<!-- Skill CONDAMAD de refactorisation chirurgicale preservee par preuves. -->

# CONDAMAD Refactor Surgeon

CONDAMAD means **COdex Native Development Agent Method for Architecture Discipline**.

This skill performs one surgical refactor at a time. A refactor changes internal
structure, not external behavior. The refactor must be bounded,
mono-domain, behavior-preserving, DRY, No Legacy, and evidence-first.

## Purpose

Guide Codex through a safe refactor run that is scoped before edits, validated
after edits, and reviewable by `condamad-code-review`.

This skill complements:

- `condamad-story-writer`
- `condamad-dev-story`
- `condamad-code-review`

## Non-negotiable rules

- Accept exactly one primary refactor type from `references/refactor-taxonomy.md`.
- Accept exactly one primary domain per refactor run.
- Require a refactor plan before code edits.
- Require explicit behavior invariants before any transformation.
- Preserve external behavior: no new behavior, no product feature changes.
- Enforce DRY and No Legacy.
- Do not create compatibility wrappers, shims, aliases, re-exports, silent fallbacks, or legacy paths unless a separate story explicitly authorizes them.
- Stop on vague requests such as "refactor this" when type, scope, domain, or behavior invariants are missing.
- Do not run broad cleanup or unrelated formatting.
- Do not mutate application files outside the approved refactor plan.
- Do not claim completion without validation evidence, negative legacy scans, and diff review.

## Required references

Read:

- `workflow.md`
- `references/refactor-taxonomy.md`
- `references/refactor-contract.md`
- `references/behavior-preservation-contract.md`
- `references/no-legacy-dry-contract.md`
- `references/validation-contract.md`
- `references/diff-review-contract.md`

## Required artifacts

Use:

- `templates/refactor-plan.md`
- `templates/refactor-evidence.md`

The plan must be validated before edits when possible:

```bash
python -B scripts/condamad_refactor_validate.py --plan <refactor-plan.md>
```

The final skill package or refactor evidence may be validated with:

```bash
python -B scripts/condamad_refactor_validate.py --skill-root <skill-root>
python -B scripts/condamad_refactor_validate.py --evidence <refactor-evidence.md>
```

For Python commands in this repository, activate the venv first according to
the repository `AGENTS.md`.

## Output

Produce or update one `refactor-plan.md` before edits and one
`refactor-evidence.md` before completion. Evidence must include exact commands,
results, negative legacy scans, and diff review.
