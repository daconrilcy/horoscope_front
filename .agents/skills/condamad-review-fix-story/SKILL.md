---
name: condamad-review-fix-story
description: "Orchestrate a CONDAMAD story drafting review loop: run condamad-story-draft-review as an editorial story-contract reviewer, detect every drafting issue, fix story artifacts, validate, then repeat until no story-contract issue remains. Use when the user asks to review and correct a CONDAMAD story draft or run an automated Review to Fix to Review cycle for story readiness. Invoke condamad-feedback-loop before closure when review findings, user corrections, failed validations, regressions, or repeated execution mistakes reveal reusable learning that should update evidence, tests, guardrails, AGENTS.md, or an owning skill."
---

# CONDAMAD Review Fix Story

## Objective

Close exactly one drafted CONDAMAD story contract by looping through
adversarial editorial review and story-artifact fixes until the review has no
remaining drafting issues.

This skill normally composes `../condamad-story-draft-review/SKILL.md`. Load
and apply `condamad-story-draft-review` for full editorial review iterations.
Exception: the compact pre-implementation path below may produce a clean review
artifact without loading the broader review skill when its exit criteria are
met.
Do not route findings to application implementation skills. This workflow fixes
story drafting artifacts only.

When review findings, user corrections, failed validations, regressions, or
repeated execution mistakes reveal reusable learning, invoke
`$condamad-feedback-loop` before closure and record the routing decision in the
review/fix evidence. Keep the loop scoped to the current story, apply only
accepted feedback, validate the resulting story evidence, guardrail, AGENTS.md,
or skill changes, and record any propagation. Do not invoke the loop for
one-off local edits that are fully resolved and have no reusable learning value.
If explicit skill invocation is unavailable, read
`../condamad-feedback-loop/SKILL.md` and follow its workflow.

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
4. `../condamad-story-draft-review/SKILL.md` and its required references.
5. Existing repository structure only when needed to avoid inventing story
   facts.

Do not weaken acceptance criteria or review findings to make the loop pass.

When the target is a pre-implementation story contract and it targets
`backend` or `frontend` paths that are absent from the current workspace, do
not convert `ready-to-dev` to `blocked` solely for that repository-shape
absence. Preserve or add `Repository structure alert:` stating that
implementation must create the missing directories/files if the scope remains
confirmed. Treat it as a blocker only when validation cannot pass without
inventing repository facts or the user explicitly asks to block external-repo
stories.

## Preflight

1. Locate the repository root.
2. Run `git status --short` only when `.git` exists; otherwise record
   `not a git repository` once and do not run additional git commands.
3. Read applicable `AGENTS.md` files.
4. Resolve the target story and its capsule directory.
5. Ensure `_condamad/stories/regression-guardrails.md` exists. Do not read or
   paste the full registry during normal review/fix work. Resolve only the
   guardrail IDs already named by the story/review evidence or use a scoped
   resolver/search for the target surface.
6. Read the story files needed to understand scope and prior evidence:
   `00-story.md` and `generated/11-code-review.md` when present. For compact
   pre-implementation review, do not read `generated/10-final-evidence.md`
   unless the story status is post-implementation or the story explicitly cites
   that artifact. Read other generated files only when needed.
7. Resolve the story contract surface from target-file lists, acceptance
   criteria, validation plan, review evidence, and scoped repository facts. The
   review target is the drafted story contract, not application code.
8. If the story came from an audit, read the source finding/candidate and
   latest same-domain audit or sibling stories when available.

Never overwrite unrelated user changes. If unrelated dirty files exist, leave
them untouched.

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

### Brief Alignment Fast Path

Use this fast path when the current user request asks for final alignment with
the source brief, not for a new full editorial review loop.

Read only with targeted extraction, not full-file dumps:

- the source brief;
- the matching `_condamad/stories/story-status.md` row;
- the target `00-story.md` headings plus sections needed for objective,
  domain, ACs, validations, non-goals, risks, and review artifact path;
- `generated/11-code-review.md` verdict, findings summary, and validation
  summary when it exists.

If `generated/11-code-review.md` already contains `CLEAN`, the target story
already covers the brief objective, scope, ACs, non-goals, risks, validations,
and separate review artifact, and both story validation commands pass, then:

- do not load broad story-draft-review references;
- do not rewrite the review artifact just to record the alignment pass;
- do not edit the tracker unless the status or date is wrong;
- report the clean reuse, validations, and any residual risk.

Escalate back to the full review/fix loop only when the alignment pass finds a
material brief/story gap, failed validation, stale review evidence, missing
required review artifact, or contradictory status.

For pre-implementation story-contract review, keep the loop compact:

- if the story already passed `condamad_story_validate.py` and
  `condamad_story_lint.py --strict` in the immediately preceding writer log,
  start with a compact review of only the story, tracker row, source brief, and
  scoped `RG-XXX` IDs. Do not load `condamad-story-draft-review/SKILL.md` or
  `condamad-story-draft-review/workflow.md` before the compact review has found
  a concrete issue or the current request explicitly requires the full
  editorial workflow;
- before returning `CLEAN`, extract the source brief's named work items from
  objective, numbered work lists, expected files/tests, and out-of-scope lists.
  Verify that every in-scope primitive named by the brief is explicit in the
  story's target state or domain boundary, tasks, expected files or ownership,
  and validation evidence. Treat hidden primitives as review findings. Example:
  if the brief says "factories/runtime de resolution", the story must name
  factory helpers, runtime resolution, and resolver behavior explicitly;
- when the compact review finds no issue, write or refresh
  `generated/11-code-review.md` directly with a concise `CLEAN` verdict,
  validation results, artifact path, and residual risk. If no story or tracker
  text changed after the validations that proved the compact review clean, do
  not rerun story validation only because the review artifact was created.
  Check only that the artifact exists and is concise, then exit. This compact
  artifact-only case overrides the closure step that normally reruns final
  story validation. Do not check the tracker again unless the tracker was
  edited. Do not escalate to the full review workflow just to produce the
  standard artifact;
- do not report missing `generated/11-code-review.md` as a story drafting
  finding during the first review pass. Creating or replacing that file is the
  normal output of this review phase. Treat it as a finding only when the story
  points to a different review path or a later clean review still lacks the
  generated artifact;
- in the final review artifact, record first-pass creation of
  `generated/11-code-review.md` under produced artifacts or review output, not
  under issues fixed. It is only an issue when the story contract names the
  wrong path or a clean review leaves the artifact absent;
- if `generated/11-code-review.md` already exists with `CLEAN` and the story
  still passes `condamad_story_validate.py` and strict lint, do not rewrite the
  review artifact just to record another pass;
- fix every discovered story-text issue in one batch before rerunning
  validation;
- keep edited Markdown lines under 160 characters in tables and under 180
  characters elsewhere before running strict lint;
- do not inspect validator or linter source code unless an unknown diagnostic
  cannot be understood from the command output.
- for ad hoc PowerShell audit helpers, avoid interpolated strings such as
  `"$p:$i"`; use the `-f` format operator or `${p}`/`${i}` delimiters so the
  helper itself does not burn a retry budget on parser errors.

### 1. Review

Run a full `condamad-story-draft-review` editorial pass on the target story.

The review must use `../condamad-story-draft-review/SKILL.md` to inspect the drafted
story contract, including story capsule evidence, acceptance criteria,
validation plan, guardrails, non-goals, and review artifact paths. It must not
inspect application implementation code. It must produce or update editorial
review evidence, typically:

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

### 3. Fix Story Artifacts

Fix all issues found in the current iteration before starting the next review.

Rules:

- Apply the smallest coherent story/evidence patch that resolves the issue.
- Add or update expected tests/guards in the story when the finding exposes
  behavioral, architecture, or regression risk.
- Update generated evidence files to record what was fixed and how it was
  validated.
- Do not mark a finding resolved without story evidence and validation.
- Do not introduce compatibility shims, fallback behavior, aliases, or duplicate
  active paths unless the story explicitly requires them.
- For audit-source closure findings, fix the whole remaining in-domain surface
  covered by the story objective, not just the first failing example.

### 4. Validate

Run the relevant story validation after each fix batch:

- `condamad_story_validate.py`;
- `condamad_story_lint.py --strict`;
- targeted scans over story/capsule artifacts when checking path drift;
- guardrail resolver/search only for scoped `RG-XXX` evidence.

For Python commands in this repository, activate the venv first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Only attempt that activation after `Test-Path .venv\Scripts\Activate.ps1`
returns `True`. If `.venv` is absent, run the repository `python` command
directly and record that fallback once. Do not emit activation errors in clean
review or alignment logs.

Do not treat skipped commands as passed. Record skipped commands, reasons, and
risks in the capsule evidence.

### 5. Repeat

Start a new `condamad-story-draft-review` editorial pass. Do not stop after fixing an issue.
The loop only ends after a fresh review finds no issues.

There is no arbitrary iteration limit. Stop only for a real blocker: missing
story, unreadable required instructions, unsafe destructive change, unresolved
conflicting requirements, repeated validation failure with no safe fix, or a
user stop request.

## Closure

When a fresh review has no issues:

1. Update story review evidence:
   - `generated/11-code-review.md` with the final clean editorial review
     evidence.
2. Check whether the loop produced reusable learning:
   - invoke `condamad-feedback-loop` for accepted reusable feedback;
   - record `no-propagation` when every correction was local and fully
     contained.
3. Update `_condamad/stories/story-status.md`:
   - locate the row by story ID, story key, or `00-story.md` path;
   - preserve or set the drafting status required by the story workflow;
   - update `Last update` to the current local date in `YYYY-MM-DD` format;
   - preserve story ID, key, title, path, source, and table shape.
4. Run final story validation and strict lint, except for the compact
   pre-implementation artifact-only case described above where validation
   already passed and only `generated/11-code-review.md` changed.
5. Summarize modified CONDAMAD story/review paths from the known edits.
6. Confirm audit-source closure status is closed, intentionally phased with
   remaining map, blocked by an explicit decision, or non-domain. Do not close a
   full-closure story with hidden residual in-domain work.
Do not commit or push. Repository publication is owned by the orchestrator.

## Final response

Respond in French. Include:

- story key and final status;
- number of review/fix iterations;
- issues fixed, summarized by category;
- files changed;
- validations run and result;
- repository publication status only when the orchestrator reports it;
- remaining risks, or `Aucun risque restant identifie`.
