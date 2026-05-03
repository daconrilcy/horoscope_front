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
- Every new story must receive the next sequential `CS-###` story number.
- Every new story must update `_condamad/stories/story-status.md`.
- The story must consult `_condamad/stories/regression-guardrails.md`,
  create it from the `condamad-regression-guardrails` template if missing, and
  include a `Regression Guardrails` section mapping applicable invariants to
  evidence.
- Do not invent repo facts. Mark assumptions explicitly.
- Do not create compatibility shims, aliases, fallbacks, or legacy paths as acceptable implementation routes.
- Do not mark a story `ready-to-dev` unless it passes the story validation contract.
- Do not mark a story `ready-to-review` unless implementation evidence exists.
- Do not mark a story `done` unless review evidence exists.

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
- `references/story-archetypes.md`
- `references/acceptance-criteria-contract.md`
- `references/no-legacy-dry-contract.md`
- `references/codex-story-optimization.md`
- `references/evidence-and-validation-contract.md`
- `references/evidence-profiles.md`
- `references/runtime-source-of-truth-contract.md`
- `references/baseline-snapshot-contract.md`
- `references/ownership-routing-contract.md`
- `references/allowlist-exception-contract.md`
- `references/contract-shape-contract.md`
- `references/batch-migration-contract.md`
- `references/reintroduction-guard-contract.md`
- `references/persistent-evidence-contract.md`
- `../condamad-regression-guardrails/SKILL.md`

When the selected archetype or operation is removal-related, also read:

- `references/removal-story-contract.md`

## Output

Write one story markdown file using `templates/story-template.md`.
For conditional transverse sections, choose exactly one active or
not-applicable snippet from `templates/snippets/` and inline its content into
the final story.

Before writing the story, assign a stable story number:

- use the next available `CS-###` number, zero-padded to three digits;
- determine the next number from `_condamad/stories/story-status.md` when it
  exists;
- if the tracking document is missing, create it and seed it from existing
  `_condamad/stories/*/00-story.md` files when practical;
- if seeding is not practical, start at `CS-001` and record the assumption in
  the tracking document;
- never reuse a number, even when a story is renamed or marked `done`;
- include the story number in the story title line and in the tracking row.

Story statuses are limited to:

- `ready-to-dev`: story contract is validated and ready for implementation;
- `ready-to-review`: implementation is complete and ready for code review;
- `done`: code review and required validation evidence are complete.

Update `_condamad/stories/story-status.md` whenever a story is created or its
status changes. The tracking document must be the single registry for story
number, story key, title, status, path, source, and last update date.

Before writing the story, apply `condamad-regression-guardrails`:

- ensure `_condamad/stories/regression-guardrails.md` exists;
- read it and classify applicable invariants;
- add the required `Regression Guardrails` section;
- add current-state evidence proving the registry was consulted;
- add or update registry rows when the new story establishes a durable
  invariant.

Contract headings and required markers must remain in English. Business content,
evidence descriptions, and implementation notes may be written in French when
that matches the project context.

When the output path is not provided, write to:

`_condamad/stories/<CS-###>-<story-key>/00-story.md`

Also use the input templates when helpful:

- `templates/story-brief-template.md` for a brief that needs clarification.
- `templates/story-audit-input-template.md` for audit or review findings.

## Self-validation

From the skill directory:

```bash
python -B scripts/condamad_story_validate.py <story_path>
python -B scripts/condamad_story_validate.py --explain-contracts <story_path>
python -B scripts/condamad_story_lint.py <story_path>
python -B scripts/condamad_story_lint.py --strict <story_path>
```

From the repository root:

```bash
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py <story_path>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts <story_path>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py <story_path>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict <story_path>
```

Fix the story until all validation commands pass.

## Skill self-test

Run the skill self-tests without loading site packages and without writing
Python bytecode:

```bash
python -S -B -m unittest discover -s .agents/skills/condamad-story-writer/scripts/self_tests -p "*selftest.py" -v
```

If repository commands are required by the project, run them according to the
local `AGENTS.md`. For Python commands in this repository, activate the venv
first.

Before packaging or zipping this skill, remove generated Python artifacts. The
skill package must not contain `__pycache__`, `.pyc`, or `.pyo` files.
