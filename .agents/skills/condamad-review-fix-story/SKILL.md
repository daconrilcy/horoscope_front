---
name: condamad-review-fix-story
description: "Orchestrate a CONDAMAD story closure loop: run condamad-code-review on one implemented story, detect every review issue, fix all issues, validate, then repeat review until no issues remain. Use when the user asks to review and correct a CONDAMAD story, close a story after review, make a story done, or run an automated Review to Fix to Review cycle before commit and push."
---

# CONDAMAD Review Fix Story

## Objective

Close exactly one CONDAMAD story by looping through adversarial review and
implementation fixes until the review has no remaining issues.

This skill composes `../condamad-code-review/SKILL.md`; it does not replace its
review doctrine. Load and apply `condamad-code-review` at every review
iteration.
Also apply `../condamad-dev-story/references/condamad-principles.md` at every
fix iteration so accepted fixes satisfy SOLID, DRY, KISS, and YAGNI instead of
only silencing the immediate review finding.

For frontend fixes, also load and apply `../condamad-frontend-dev/SKILL.md`.
Any accepted review finding whose fix touches `frontend/**`, frontend tests,
frontend styles, frontend build tooling, React behavior, Tailwind/shadcn UI,
TanStack Query, Zustand, forms, routing, or Playwright flows must be fixed
through the `condamad-frontend-dev` contract.

## Required inputs

Accept one target:

- a CONDAMAD story capsule directory;
- a CONDAMAD story file such as
  `_condamad/stories/story-key/00-story.md`;
- the currently active story when the user context identifies exactly one.

If more than one plausible story target exists, stop and ask for the exact
story path. Do not review or fix multiple stories in one execution.

## Source of truth

Apply instructions in this order:

1. Current user request.
2. Repository `AGENTS.md` files for touched paths.
3. The target story `00-story.md` and generated capsule evidence.
4. `../condamad-code-review/SKILL.md` and its required references.
5. `../condamad-frontend-dev/SKILL.md` for frontend review fixes, frontend
   validation, and frontend static/regression guards.
6. Existing implementation patterns.

Do not weaken acceptance criteria or review findings to make the loop pass.

## Preflight

1. Locate the repository root.
2. Run `git status --short` and identify pre-existing dirty files.
3. Read applicable `AGENTS.md` files.
4. Resolve the target story and its capsule directory.
5. Ensure `_condamad/stories/regression-guardrails.md` exists and read it.
6. Read the story files needed to understand scope and prior evidence:
   `00-story.md`, `generated/10-final-evidence.md` when present,
   `generated/11-code-review.md` when present, and other generated files only
   when needed.
7. Resolve the implementation surface produced by the communicated story from
   capsule evidence, target-file lists, final evidence, review evidence,
   relevant git diff/history, and repository searches. The review target is the
   code implemented for that story, not the whole repository and not only the
   currently unstaged diff.
8. If the story came from an audit, read the source finding/candidate and
   latest same-domain audit or sibling stories when available.

Never overwrite unrelated user changes. If unrelated dirty files exist, leave
them untouched and commit only files that belong to this story closure.

## Story closure gate

Before the first review/fix loop, classify audit-sourced stories as
`full-closure`, `phased-with-map`, `blocked`, or `non-domain`.

If the story claims or implies full closure, do not accept residual in-domain
work, broad allowlists, wildcard exceptions, unclassified fallback,
compatibility, legacy, migration-only, shim, alias, TODO, or `PASS with
limitation` as a valid end state.

If the story is only a phase, require the remaining closure map and exact stop
condition in evidence. If neither is present, treat the story as under-scoped
and record a review finding before applying fixes.

## Review/fix loop

Repeat this loop until the review verdict is clean.

### 1. Review

Run a full `condamad-code-review` pass on the target story.

The review must use `../condamad-code-review/SKILL.md` to inspect the code
implemented for the communicated story, including repository evidence, story
capsule evidence, changed files, tests, guardrails, and the current diff when
present. Do not review only the story text. It must produce or update review
evidence, typically:

```text
_condamad/stories/story-key/generated/11-code-review.md
```

Treat the review as having issues when it reports any of the following:

- a finding of any severity;
- missing or failed validation evidence;
- missing regression-guardrail evidence;
- unresolved prior review finding;
- `BLOCKED`, `FAIL`, `CHANGES_REQUESTED`, or any non-clean verdict;
- a contradiction between story evidence and repository state.

Only consider the review clean when it explicitly reaches a no-issue verdict
such as `CLEAN`, `APPROVED`, or equivalent wording, and all required validation
evidence is present.

### 2. Decide

If there are no issues, exit the loop and proceed to closure.

If issues exist, convert every issue into a concrete fix task. Preserve the
review finding text or an accurate summary in the capsule evidence so the next
review can verify resolution.

### 3. Fix

Fix all issues found in the current iteration before starting the next review.

Rules:

- Route every accepted frontend finding through `condamad-frontend-dev` before
  editing frontend files.
- Apply the smallest coherent code or evidence patch that resolves the issue.
- Add or update tests/guards for behavioral, architecture, or regression risk.
- Update generated evidence files to record what was fixed and how it was
  validated.
- Do not mark a finding resolved without code/evidence and validation.
- Do not introduce compatibility shims, fallback behavior, aliases, or duplicate
  active paths unless the story explicitly requires them.
- For audit-source closure findings, fix the whole remaining in-domain surface
  covered by the story objective, not just the first failing example.

Frontend review-fix rules:

- A finding is a frontend finding when its fix touches `frontend/**`, frontend
  tests, frontend styles, frontend build tooling, React behavior,
  Tailwind/shadcn UI, TanStack Query, Zustand, forms, routing, or Playwright
  flows.
- Apply the full `condamad-frontend-dev` contract for every frontend fix:
  repository inspection, pattern reuse, ownership boundaries, naming, TanStack
  Query rules, error states, UI/logic separation, frontend regression
  guardrails, static guard checks, and validation evidence.
- When subagents are available and the current task permits implementation
  delegation, use `condamad-frontend-dev` as the frontend implementation
  subagent with ownership limited to `frontend/**` and explicit evidence files
  when needed.
- If no subagent is used, the main session must still apply every
  `condamad-frontend-dev` rule and record that the frontend contract was
  applied directly.
- Do not mark a frontend review finding resolved without frontend validation
  evidence or an explicit blocker.

### 4. Validate

Run the relevant validation after each fix batch:

- targeted tests for the changed area;
- required guardrail commands;
- lint/static checks required by the repo or story;
- broader test suites when the fix changes shared behavior.
- for frontend fixes, the relevant `condamad-frontend-dev` checks: package
  script discovery, `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm test:e2e`
  when required, frontend static guards, and applicable frontend `RG-XXX`
  evidence.

For Python commands in this repository, activate the venv first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Do not treat skipped commands as passed. Record skipped commands, reasons, and
risks in the capsule evidence.

### 5. Repeat

Start a new `condamad-code-review` pass. Do not stop after fixing an issue.
The loop only ends after a fresh review finds no issues.

There is no arbitrary iteration limit. Stop only for a real blocker: missing
story, unreadable required instructions, unsafe destructive change, unresolved
conflicting requirements, repeated validation failure with no safe fix, or a
user stop request.

## Closure

When a fresh review has no issues:

1. Update story evidence:
   - `generated/10-final-evidence.md` with final validation and remaining risk.
   - `generated/11-code-review.md` with the final clean review evidence.
   - frontend review-fix evidence when any frontend surface changed.
2. Update `_condamad/stories/story-status.md`:
   - locate the row by story ID, story key, or `00-story.md` path;
   - set `Status` to `done`;
   - update `Last update` to the current local date in `YYYY-MM-DD` format;
   - preserve story ID, key, title, path, source, and table shape.
3. Run final validation required by the story and repository.
4. Review `git diff --stat` and `git diff` to confirm scope.
5. Confirm audit-source closure status is closed, intentionally phased with
   remaining map, blocked by an explicit decision, or non-domain. Do not close a
   full-closure story with hidden residual in-domain work.
6. Commit only the story closure changes with a concise message, for example:

```text
chore(condamad): close CS-013 review
```

7. Push the current branch with a non-destructive push:

```powershell
git push
```

Do not amend, squash, rebase, reset, force-push, or include unrelated dirty
files.

## Final response

Respond in French. Include:

- story key and final status;
- number of review/fix iterations;
- issues fixed, summarized by category;
- files changed;
- validations run and result;
- commit hash and push result;
- remaining risks, or `Aucun risque restant identifie`.
