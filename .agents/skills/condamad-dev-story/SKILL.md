---
name: condamad-dev-story
description: >
  Implement exactly one development story using CONDAMAD, a Codex-native story
  execution method. Use when the user asks to implement, develop, continue, or
  fix a single story with CONDAMAD; when converting a BMAD story into a Codex
  execution capsule; or when implementing architecture/refactor stories that
  require DRY, No Legacy, tests, validation, and final evidence. Do not use for
  pure story writing, roadmap planning, review-only analysis, or broad multi-story epics.
---

# CONDAMAD Dev Story

CONDAMAD means **COdex Native Development Agent Method for Architecture Discipline**.

This skill implements one story as a controlled, evidence-driven Codex task. It is optimized for repository work where Codex must inspect the real code, make scoped changes, run validations, prove acceptance criteria, and avoid legacy-by-inertia.

## 1. Primary objective

Implement exactly one story from either:

- an existing CONDAMAD story capsule; or
- a single story markdown file, including a legacy BMAD story file, from which Codex must generate a CONDAMAD capsule before implementation; or
- a story body provided directly in the prompt, from which Codex must persist a CONDAMAD capsule before implementation.

A successful execution produces:

- scoped code changes;
- tests or architecture guards proving the change;
- traceability from every Acceptance Criterion to code and validation evidence;
- a completed final evidence report;
- no compatibility shim, alias, fallback, duplicate active path, or transitional legacy unless explicitly required by the story.

## 2. Reference loading policy

Before implementing a story, read these references from this skill:

- `references/condamad-principles.md`
- `references/story-capsule-contract.md`
- `references/validation-contract.md`
- `references/no-legacy-contract.md`
- `../condamad-regression-guardrails/SKILL.md`

These references are normative for CONDAMAD execution. If they conflict with this `SKILL.md`, apply this rule:

- `SKILL.md` wins for skill activation and top-level workflow routing.
- `story-capsule-contract.md` wins for capsule structure.
- `validation-contract.md` wins for validation and evidence classification.
- `no-legacy-contract.md` wins for No Legacy interpretation.
- `condamad-regression-guardrails` wins for the shared inter-story invariant
  registry workflow.
- Explicit user instruction in the current task wins unless it conflicts with repository safety, destructive changes, or higher-priority instructions.

## 3. Expected inputs

The user may provide either:

1. A path to a single story markdown file.
2. A path to an existing CONDAMAD story capsule directory.
3. A story body directly in the prompt, when no file path is available.

If only a story markdown file is provided, Codex must generate a CONDAMAD capsule before implementation.

The user must not be asked to manually create generated capsule files unless story content or filesystem access is missing.

Do not use an in-memory capsule for implementation. CONDAMAD requires persistent evidence files.

## 4. Canonical capsule structure

The canonical capsule structure is:

```text
_condamad/stories/<story-key>/
  00-story.md
  generated/
    01-execution-brief.md
    03-acceptance-traceability.md
    04-target-files.md
    06-validation-plan.md
    07-no-legacy-dry-guardrails.md
    10-final-evidence.md
```

Optional generated files may be added when useful:

```text
_condamad/stories/<story-key>/
  generated/
    02-context-map.md
    05-implementation-plan.md
    08-subagent-briefs.md
    09-dev-log.md
```

When a capsule does not exist:

1. Create `_condamad/stories/<story-key>/`.
2. Copy or persist the source story as `00-story.md`.
3. Generate all required files under `generated/`.
4. Continue implementation only after the capsule is complete and readable.

The helper script `scripts/condamad_prepare.py` may be used to generate the capsule structure from a story markdown file.

## 5. Source-of-truth precedence

When instructions conflict, apply this order:

1. Explicit user instruction in the current task.
2. The story’s Acceptance Criteria and explicit non-goals.
3. CONDAMAD capsule files.
4. Repository `AGENTS.md` files that apply to touched paths.
5. Project context, architecture docs, and existing test conventions.
6. Existing implementation patterns in the repository.

Never ignore repository-local `AGENTS.md` instructions. Read every applicable `AGENTS.md` before editing files in its scope.

## 6. Non-negotiable execution rules

### Workspace safety

- Locate the repository root before editing.
- Run `git status --short` before editing.
- Ensure `_condamad/stories/regression-guardrails.md` exists before editing;
  create it from the `condamad-regression-guardrails` template if missing.
- Read `_condamad/stories/regression-guardrails.md` and record applicable
  invariants in the capsule validation / No Legacy evidence.
- Record dirty files in `generated/09-dev-log.md` or `generated/10-final-evidence.md`.
- Do not overwrite unrelated user changes.
- Do not run destructive git commands unless the user explicitly requests them.
- Do not amend, squash, reset, rebase, or force-push.
- Do not delete files unless the story or implementation plan justifies the deletion.
- Before final response, run `git status --short` again and report the result.

### Scope control

- Implement only the current story.
- Do not opportunistically refactor unrelated areas.
- Do not add new dependencies unless explicitly allowed by the story or approved by the user.
- Do not change public behavior unless the story requires it.
- Do not change Acceptance Criteria during implementation.
- Do not modify architectural doctrine to fit the implementation; change implementation to fit doctrine.

### DRY / No Legacy

Forbidden unless explicitly required by the story:

- compatibility wrappers;
- transitional aliases;
- legacy import paths;
- duplicate active implementations;
- re-export modules preserving old imports;
- silent fallback behavior;
- root-level service files when a canonical namespace exists;
- tests that preserve legacy paths as nominal behavior;
- “temporary” shims without a removal mechanism and explicit approval.

Required when relevant:

- one canonical path per responsibility;
- negative search evidence for removed symbols or imports;
- tests or architecture guards that fail if the legacy path is reintroduced;
- explicit error behavior instead of silent fallback for missing canonical config;
- deletion of obsolete code when safe and in scope.

## 7. Capsule file responsibilities

### `00-story.md`

The human-owned story source inside the capsule. It must contain the original story content or a faithful copy of the original story file.

Do not rewrite business intent, acceptance criteria, or scope in this file unless the user explicitly asks for story editing.

### `generated/01-execution-brief.md`

The concise instruction file for this story. It must define the primary objective, boundaries, non-goals, preflight checks, write rules, done conditions, and halt conditions.

### `generated/03-acceptance-traceability.md`

The AC-to-evidence matrix. Before final completion, every AC must have code evidence, validation evidence, and status set to `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, or `BLOCKED`.

### `generated/04-target-files.md`

The initial file and search map. Treat it as a starting hypothesis, then confirm with repository search before editing.

### `generated/06-validation-plan.md`

The validation contract for the story. It must list targeted tests, architecture checks, lint/static checks, broader regression checks, and any project quality gate.

If a command cannot be run, record the exact command, why it was not run, and the risk created by not running it.

### `generated/07-no-legacy-dry-guardrails.md`

The mandatory DRY / No Legacy review checklist. Use it for architecture, refactor, service, runtime, namespace, import, and migration stories.

When relevant, run searches similar to:

```bash
rg "legacy|compat|shim|fallback|deprecated|alias" .
rg "from app\.services|import app\.services" backend tests
```

Adapt paths and patterns to the repository.

### `generated/10-final-evidence.md`

The final reviewer-facing proof file. Do not mark a story ready for review unless this file is complete and honest.

It must include:

- story status;
- AC-by-AC validation;
- files changed;
- files deleted;
- tests added or updated;
- commands run successfully;
- commands not run with reasons;
- Legacy / DRY evidence;
- remaining risks;
- suggested reviewer focus.

## 8. Execution workflow

### Step 0 — Preflight

1. Locate the repository root.
2. Run `git status --short`.
3. Record dirty files.
4. Read applicable `AGENTS.md` files.
5. Apply `condamad-regression-guardrails`: create the registry if missing, read
   it, and classify applicable invariants for the story surface.
6. Identify the story capsule path or story file path.
7. If no story can be found, stop with a precise blocker.

### Step 1 — Generate or validate the capsule

If the input is a story markdown file or prompt body:

1. Infer a stable story key.
2. Create `_condamad/stories/<story-key>/`.
3. Persist the source story as `00-story.md`.
4. Generate required files under `generated/`.
5. Validate the capsule structure before editing code.

If the input is already a capsule directory:

1. Confirm `00-story.md` exists.
2. Confirm required `generated/` files exist.
3. Regenerate missing generated files only if doing so does not overwrite user-authored evidence.

Use `scripts/condamad_prepare.py` and `scripts/condamad_validate.py` when available and appropriate.

### Step 2 — Load story context

Read, in order:

1. `00-story.md`;
2. `generated/01-execution-brief.md`;
3. `generated/03-acceptance-traceability.md`;
4. `generated/04-target-files.md`;
5. `generated/06-validation-plan.md`;
6. `generated/07-no-legacy-dry-guardrails.md`;
7. `_condamad/stories/regression-guardrails.md`;
8. optional generated context files if present.

Extract:

- story key;
- goal;
- ACs;
- non-goals;
- changed-area constraints;
- validation expectations;
- forbidden legacy patterns.
- applicable regression guardrail IDs and evidence requirements.

### Step 3 — Inspect repository before editing

Use `rg` and targeted file reads before implementing.

Required searches when relevant:

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
rg "from app\.services|import app\.services" backend tests
```

Adapt searches to the story. Avoid broad, noisy commands when a narrower query exists.

### Step 4 — Build or update the implementation plan

Before modifying code, create or update `generated/05-implementation-plan.md` when useful.

Include:

- current architecture finding;
- selected target approach;
- files to modify;
- tests to add or update;
- deletion candidates;
- explicit No Legacy stance;
- rollback strategy.

The plan is not a request for user approval unless a HALT condition is met.

### Step 5 — Implement in small patches

Implementation rules:

- Make the smallest coherent patch that satisfies the next AC group.
- Prefer focused edits.
- Reuse existing abstractions before creating new ones.
- Delete obsolete paths when the story requires zero legacy.
- Update imports to canonical paths.
- Do not leave compatibility re-exports.
- Do not hide breakages behind fallbacks.
- For each AC, add or update tests/guards before considering it complete.

### Step 6 — Validate locally

Run the validation plan in this order when possible:

1. targeted tests;
2. relevant architecture/negative scans;
3. lint/static checks;
4. broader regression suite;
5. project quality gate.

Also run or record the guard commands required by applicable rows in
`_condamad/stories/regression-guardrails.md`.

Typical Python backend commands:

```bash
ruff format .
ruff check .
pytest -q
```

Typical Windows quality gate, if present:

```powershell
./scripts/quality-gate.ps1
```

If the repository defines different commands in `AGENTS.md`, package config, CI config, or `generated/06-validation-plan.md`, prefer those.

### Step 7 — Review diff before completion

Before marking the story complete, review:

```bash
git diff --stat
git diff
```

Check:

- no unrelated file was changed;
- no forbidden legacy pattern was introduced;
- story/capsule files changed only where allowed;
- deleted files are intentional;
- tests prove the ACs;
- formatting-only churn is justified.

### Step 8 — Complete evidence

Update:

- `generated/03-acceptance-traceability.md`;
- `generated/09-dev-log.md` when present or useful;
- `generated/10-final-evidence.md`.
- `_condamad/stories/regression-guardrails.md` when this implementation creates
  a new durable invariant or changes an existing guard.

Record:

- commands run;
- pass/fail result;
- skipped commands and reason;
- changed files;
- deleted files;
- AC-by-AC evidence;
- remaining risks.

### Step 9 — Final response

Respond in the user’s language.

The final response must include:

- story key and final status;
- concise implementation summary;
- files changed;
- tests/checks run and result;
- skipped checks, if any;
- remaining risks, if any;
- suggested reviewer focus.

Do not paste large diffs into the final response unless requested.

## 9. HALT conditions

Stop and report a precise blocker only when one of these occurs:

- story file or capsule is inaccessible;
- required repository instructions cannot be read;
- required secret/config/dependency is missing and cannot be inferred safely;
- implementation requires a new dependency not approved by the story;
- validation fails repeatedly and a safe fix is not clear;
- requested change would be destructive or outside story scope;
- ACs require mutually contradictory behavior;
- user explicitly asks to stop.

Do not stop merely because the story is large or because a milestone was reached.

## 10. Review continuation mode

If the story has prior review findings:

1. Read all review comments/findings.
2. Convert each unresolved finding into traceability entries.
3. Prioritize high-severity findings.
4. Fix findings before unrelated cleanup.
5. Record each resolved finding in `generated/09-dev-log.md` and `generated/10-final-evidence.md`.

Do not mark a review finding resolved without code evidence or validation evidence.

## 11. Status conventions

For CONDAMAD capsules, use `generated/10-final-evidence.md` as the final status source.

Recommended status values:

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `DONE`

For legacy BMAD stories, preserve the original story contract. Only modify sections the BMAD story allows, typically:

- Tasks/Subtasks checkboxes;
- Dev Agent Record;
- File List;
- Change Log;
- Status.

Do not edit Acceptance Criteria, Story, or Dev Notes during implementation unless the user explicitly requests story rewriting.

## 12. Quality bar

A CONDAMAD story is complete only when all of the following are true:

- every AC has implementation evidence;
- every AC has validation evidence or a documented blocker;
- relevant tests or architecture guards exist;
- relevant tests/checks pass, or limitations are explicitly classified;
- no unrelated files changed;
- no forbidden legacy path remains unclassified;
- final evidence is complete;
- final `git status --short` is reported.

## 13. Helper scripts

This skill may include helper scripts under `scripts/`.

- `condamad_prepare.py`: generate a capsule from a story markdown file.
- `condamad_validate.py`: validate capsule structure and evidence readiness.
- `condamad_legacy_scan.py`: scan selected paths for legacy/compatibility patterns.
- `condamad_collect_evidence.py`: capture git status and diff-stat evidence.

Scripts are helpers, not a substitute for agent judgment. If a script result conflicts with repository evidence, investigate and document the reason.

## 14. Final response template

Use this structure:

```md
Story `<story-key>` is ready for review.

Implemented:

- ...

Changed files:

- ...

Validation:

- `command` — PASS
- `command` — NOT RUN: reason

Legacy / DRY evidence:

- ...

Remaining risks:

- None / ...

Reviewer focus:

- ...
```
