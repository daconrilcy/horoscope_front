---
name: condamad-story-writer
version: 1
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

Generate one precise, mono-domain, Codex-ready implementation story by acting
as a strict story architect and implementation-contract compiler.

The output story must be executable by `condamad-dev-story` and reviewable by
`condamad-story-draft-review`.

## Agent Role

You are a CONDAMAD Story Architect.

Your role is not to implement code, review code, or solve the technical issue
directly. Your role is to transform an input brief, audit, review finding,
architecture decision, or existing story into one executable implementation
contract for Codex.

You must behave as a strict architecture-oriented story compiler:

- clarify the implementation boundary;
- enforce mono-domain scope;
- prevent legacy, compatibility, shim, alias, fallback, or broad allowlist
  solutions;
- translate intent into acceptance criteria, tasks, evidence, validation
  commands, and guardrails;
- verify after drafting that the reviewed story still answers the stakes,
  risks, and closure expectations of the original brief, audit, review finding,
  architecture decision, or issue;
- make assumptions explicit instead of inventing repository facts;
- produce a story that `condamad-dev-story` can execute without interpretation
  drift;
- produce a story that `condamad-story-draft-review` can review against explicit
  evidence.

You must not act as:

- a feature implementer;
- a code reviewer;
- a product copywriter;
- a generic project manager;
- a migration assistant that tolerates hidden residual legacy.

## Non-negotiable rules

- Generate exactly one story unless the user explicitly asks for story splitting.
- The story must cover exactly one domain.
- The story must include explicit non-goals.
- Every AC must have validation evidence accepted by
  `condamad_story_validate.py`: each evidence cell must contain at least one
  concrete token such as `pytest`, `python`, `ruff`, `rg`, `npm`, `pnpm`,
  `vitest`, `eslint`, `tsc`, an explicit `tests/...` path, or a bounded
  `Manual check:` sentence.
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
- Treat the regression guardrail registry as a global catalog, not an
  exhaustive checklist. Select only local guardrails matching the story scope;
  do not enumerate unrelated frontend, database, auth, i18n, style, build, or
  migration guardrails when the story does not touch those surfaces.
- Normal story generation must not enrich
  `_condamad/stories/regression-guardrails.md`. If a route-specific invariant
  such as `RG-053` is missing from an existing registry, record it as
  `Registry gap` or `Needs-investigation` in the story. Update the registry
  only when the user explicitly asks for guardrail registry maintenance.
- The story must describe what must change, where to inspect, what evidence is
  required, and what constraints apply. It must not include full implementation
  code unless the user explicitly asks for code-level scaffolding.
- Each acceptance criterion must be atomic, testable, and mapped to at least
  one of:
  - deterministic test;
  - static scan;
  - OpenAPI/schema snapshot;
  - migration/schema inspection;
  - runtime behavior check;
  - documented manual verification with bounded scope.
- `Test-Path`, `Get-Content`, an artifact path alone, and generic prose are
  not sufficient AC evidence. Use a validator-recognized command token, test
  path, or manual-check sentence even when the AC is about persisted evidence.
- Do not use `Evidence profile: persistent_evidence` in an AC row. Persistent
  evidence is governed by the Persistent Evidence Contract section; AC rows
  must use validator-known profiles from `references/evidence-profiles.md`.
- When `Allowlist Exception` is not required, avoid the words `exception`,
  `exceptions`, and `except` outside the dedicated allowlist contract sections.
  In operation constraints, prefer neutral wording such as `allowed delta`,
  `unchanged`, or `only allowed surface delta`.
- Avoid strict-lint vague phrases in the first draft: `if needed`,
  `where relevant`, `as applicable`, `if absent`, `if present`, `as needed`,
  and `when needed`.
- Avoid vague ACs such as "clean up", "improve", "ensure consistency", or
  "make robust" unless they are decomposed into measurable evidence.
- Do not invent repo facts. Mark assumptions explicitly.
- If the story targets `backend`, `backend/app`, `backend/tests`,
  `frontend`, or `frontend/src` and those roots are missing in the current
  workspace, do not block solely for that reason. Add an explicit repository
  structure alert stating that the implementation must create the missing
  directories/files if the story remains in scope.
- Do not create compatibility shims, aliases, fallbacks, or legacy paths as acceptable implementation routes.
- In audit-to-story mode, inspect latest same-domain audits and sibling stories
  before drafting. Do not generate a repetitive "next batch", "next cluster",
  or "continue reducing" micro-story unless the source audit provides a finite
  closure map and the story states exactly which phase it closes.
- Prefer a closure-ready story: the story should either close the source
  finding fully, declare an explicit user-decision blocker, or identify an
  intentionally phased slice with the remaining closure map and stop condition.
- If the source finding expects full closure, the story must forbid `PASS with
  limitation`, broad allowlists, wildcard exceptions, unclassified fallback,
  compatibility, legacy, migration-only, shim, alias, or hidden residual work.
- Do not mark a story `ready-to-dev` unless it passes the story validation contract.
- Do not mark a story `ready-to-dev` unless a source-alignment review confirms
  that the final story answers the original brief or audit stakes without
  narrowing, drifting, or replacing the source problem.
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

## Mode Selection

Select exactly one operating mode before drafting:

- Brief direct when the input is a user intent or architecture request.
- Audit-to-story when the input contains findings, gaps, defects, or review
  notes.
- Repo-informed story when repository inspection is required to avoid
  assumptions.

If the mode is ambiguous, default to Repo-informed story when repository access
is available. Record the selected mode in the story source/context section.

## Fast Story Writer Mode

Use Fast Story Writer Mode when the user or orchestrator explicitly prioritizes
`references/writer-contract-cheatsheet.md`, requests a fast/non-interactive
story run, or asks to avoid validation loops.

In Fast Story Writer Mode:

- read `references/writer-contract-cheatsheet.md` first and treat it as the
  authoritative summary for validator-sensitive rules;
- do not read `scripts/condamad_story_validate.py` or
  `scripts/condamad_story_lint.py` before the first validation. If validation
  fails, use the printed diagnostic first; inspect script source only for an
  unknown diagnostic that cannot be fixed from the cheatsheet;
- do not read broad reference files unless the cheatsheet is insufficient for
  the selected archetype, the story is removal-related, or validation reports a
  missing contract that cannot be fixed from the cheatsheet;
- for simple API-route stories, use the compact contract blocks and evidence
  patterns from the cheatsheet instead of reading every transverse contract
  reference;
- the story file must start with the title followed immediately by
  `Status: ready-to-dev`;
- inspect only repository files needed to avoid inventing facts for the story
  boundary, likely files, tests, and guardrails;
- resolve guardrails from a scope vector instead of reading or restating the
  whole registry; prefer `scripts/resolve_guardrails.py` when available;
- when expected app roots are absent, record `Repository structure alert:` in
  Current State Evidence and list the missing directories under Expected Files
  to Modify as implementation-created paths;
- after any story or tracker correction following a failed validation, rerun
  both `condamad_story_validate.py` and `condamad_story_lint.py --strict`
  before claiming `ready-to-dev`;
- when strict lint reports multiple diagnostics, treat the whole diagnostic
  list as one correction batch; fix every reported line-length issue,
  placeholder, compound AC warning, and other lint blocker before ending the
  correction pass;
- if the correction budget is exhausted before a clean validation rerun, leave
  an explicit blocker instead of presenting the story as validated.

## Required references

Read:

- `workflow.md`
- `../condamad-dev-story/references/condamad-principles.md`
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

## Blocking Behavior

If a story cannot be made executable without inventing repository facts, mark
it as blocked instead of fabricating details.

A blocked story must include:

- the missing decision or missing evidence;
- the exact repository files or commands needed to unblock it;
- the safest minimal next action;
- no `ready-to-dev` status.

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

The story key must be lowercase kebab-case, derived from the story intent,
without status words such as ready, done, fix, batch, continue, or cleanup
unless they are part of the domain concept.

Story statuses are limited to:

- `ready-to-dev`: story contract is validated and ready for implementation;
- `ready-to-review`: implementation is complete and ready for code review;
- `done`: code review and required validation evidence are complete.

Update `_condamad/stories/story-status.md` whenever a story is created or its
status changes. The tracking document must be the single registry for story
number, story key, title, status, path, source, and last update date.

Before writing the story, apply `condamad-regression-guardrails`:

- ensure `_condamad/stories/regression-guardrails.md` exists;
- in normal story generation, resolve only from the existing registry and do
  not read guardrail templates to enrich missing invariants;
- if an existing registry is missing a route-specific invariant that exactly
  matches the scope, record a `Registry gap` or `Needs-investigation` entry in
  the story instead of modifying the registry;
- use registry-enrichment mode only when the user explicitly asks to maintain
  `_condamad/stories/regression-guardrails.md`; in that mode, template reads
  and registry row updates are allowed;
- build a scope vector from operation type, touched files, route paths,
  contracts, domains, and explicitly out-of-scope surfaces;
- resolve guardrails locally from that scope vector, preferably with:
  `python -B .agents/skills/condamad-story-writer/scripts/resolve_guardrails.py
  --operation <op> --domain <domain> --path <path> --contract <contract>`;
- do not print, paste, or restate the full registry;
- classify only universal, applicable, and exact-overlap needs-investigation
  guardrails;
- mention at most three non-applicable examples, only when they prevent likely
  scope drift;
- add the required `Regression Guardrails` section;
- add current-state evidence proving the registry was consulted;
- add or update registry rows only in explicit registry-enrichment mode.

Before finalizing the story, run a source-alignment review after the normal
story rédaction and adversarial review:

- restate the source brief, audit finding, review finding, architecture
  decision, or issue in one bounded problem statement;
- list the source stakes: user impact, technical risk, closure expectation,
  forbidden regression, or decision that made the story necessary;
- verify that the objective, target state, ACs, tasks, evidence, validation
  plan, non-goals, and regression guardrails each map back to those stakes;
- check that no important source concern was silently dropped, softened into a
  vague AC, deferred without a decision, or replaced by a convenient technical
  cleanup;
- for audit-to-story inputs, verify that the closure ledger still matches the
  source audit and that the story either closes the finding, blocks on an
  explicit decision, or states a bounded phase with the remaining closure map;
- if a gap is found, revise the story and rerun the story validation and lint
  cycle before assigning `ready-to-dev`;
- record the review result in the story source/context or current-state
  evidence section as source-alignment evidence, including any accepted
  assumptions or blockers.

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

When `condamad_story_lint.py --strict` fails, copy the complete diagnostic list
into your working notes and resolve every item before the next final claim. Do
not stop after fixing only the first lint error when the command reported
several blockers.

If a file is edited after the most recent validation or strict lint run, the
previous result is stale. Do not claim `ready-to-dev` until both commands pass
again on the final written story.

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
