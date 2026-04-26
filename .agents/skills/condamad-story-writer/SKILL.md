---
name: condamad-story-writer
description: >
  Create a Codex-optimized CONDAMAD implementation story from a brief, code
  audit, review finding, architecture decision, issue, or existing BMAD story.
  Use when the user asks to write, generate, refine, or convert a story for
  Codex dev-story execution with strict DRY, No Legacy, mono-domain scope,
  acceptance evidence, validation plan, and anti-drift implementation guardrails.
---

<!-- Skill CONDAMAD de compilation de brief en contrat d'implementation Codex. -->

# CONDAMAD Story Writer

CONDAMAD means **COdex Native Development Agent Method for Architecture Discipline**.

## Purpose

Generate one precise, mono-domain, Codex-ready implementation story.

The output story must be executable by `condamad-dev-story` and reviewable by
`condamad-code-review`.

## Non-negotiable rules

- Generate exactly one story unless the user explicitly asks for story splitting.
- The story must cover exactly one domain.
- The story must include explicit non-goals.
- Every AC must have validation evidence.
- Every task must reference at least one AC.
- The story must include DRY and No Legacy constraints.
- The story must include files to inspect before edit.
- The story must include likely files to modify and likely tests.
- Do not invent repo facts. Mark assumptions explicitly.
- Do not create compatibility shims, aliases, fallbacks, or legacy paths as acceptable implementation routes.
- Do not mark a story `ready-for-dev` unless it passes the story validation contract.

## Inputs

Accepted inputs:

- free-form brief;
- code audit;
- code review findings;
- existing BMAD story;
- architecture note;
- repo-informed request.

Supported modes:

- **Brief direct**: compile the user brief into one implementation contract.
- **Audit-to-story**: convert review findings or audit gaps into one bounded story.
- **Repo-informed story**: inspect the repository before writing the story, then cite evidence and assumptions.

## Required references

Read:

- `workflow.md`
- `references/story-authoring-principles.md`
- `references/story-output-contract.md`
- `references/acceptance-criteria-contract.md`
- `references/no-legacy-dry-contract.md`
- `references/codex-story-optimization.md`
- `references/evidence-and-validation-contract.md`

## Output

Write one story markdown file using `templates/story-template.md`.

Contract headings and required markers must remain in English. Business content,
evidence descriptions, and implementation notes may be written in French when
that matches the project context.

When the output path is not provided, write to:

`_condamad/stories/<story-key>/00-story.md`

Also use the input templates when helpful:

- `templates/story-brief-template.md` for a brief that needs clarification.
- `templates/story-audit-input-template.md` for audit or review findings.

## Self-validation

Run:

```bash
python -B scripts/condamad_story_validate.py <story_path>
python -B scripts/condamad_story_lint.py <story_path>
```

Fix the story until both commands pass.

If repository commands are required by the project, run them according to the
local `AGENTS.md`. For Python commands in this repository, activate the venv
first.
