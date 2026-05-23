---
name: condamad-dev-story
description: >
  Implement exactly one development story using CONDAMAD, a Codex-native story
  execution method. Use when the user asks to implement, develop, continue, or
  fix a single story with CONDAMAD; when converting a BMAD story into a Codex
  execution capsule; or when implementing architecture/refactor stories that
  require DRY, No Legacy, tests, validation, and final evidence. Invoke
  condamad-feedback-loop before closure when failed validation, user correction,
  regression evidence, or repeated execution mistakes reveal reusable learning
  that should update evidence, tests, guardrails, AGENTS.md, or an owning skill.
  Do not use for pure story writing, roadmap planning, review-only analysis, or
  broad multi-story epics.
---

<!-- Commentaire global: ce skill pilote une seule story CONDAMAD avec preuve locale, validation et discipline No Legacy/DRY. -->

# CONDAMAD Dev Story

CONDAMAD = **COdex Native Development Agent Method for Architecture Discipline**.

Use this skill to execute exactly one story from real repository evidence. The
agent must inspect the code, make scoped changes, prove each Acceptance
Criterion (AC), update the story capsule, and avoid legacy-by-inertia.

## 1. Outcome

A successful run produces:

- scoped code changes for one story only;
- tests, architecture guards, or static checks proving the change;
- AC-by-AC traceability with code and validation evidence;
- complete `generated/10-final-evidence.md`;
- synchronized `_condamad/stories/story-status.md`;
- no compatibility shim, alias, fallback, duplicate active path, or transitional
  legacy unless the story explicitly requires it.

## 2. Compact Loading Policy

Start from the target story/capsule and load only decision-relevant context.

Always read:

- target `00-story.md`;
- generated capsule files listed in Section 4;
- applicable repository `AGENTS.md`;
- scoped regression guardrail IDs already named by the story/capsule, or a
  resolver/search result for the touched surface.

Read references only on trigger:

- `references/condamad-principles.md`: unclear architecture, SOLID/DRY, or
  source-finding closure.
- `references/story-capsule-contract.md`: missing, invalid, generated, or
  repaired capsule.
- `references/validation-contract.md`: ambiguous validation status,
  failed/skipped checks, or evidence classification.
- `references/no-legacy-contract.md`: legacy, compatibility, fallback,
  duplicate paths, service ownership, imports, or removals.
- `../condamad-regression-guardrails/SKILL.md`: registry missing or scoped
  guardrail resolution is insufficient.
- `../condamad-feedback-loop/SKILL.md`: reusable learning must be propagated.
- `../condamad-frontend-dev/SKILL.md`: story touches `frontend/`, frontend
  styles/tests/tooling, or user-facing React behavior.

Do not paste large reference, registry, diff, or generated evidence bodies into
chat. Summarize facts and cite paths.

Conflict order:

1. current user instruction, unless unsafe/destructive;
2. story ACs and explicit non-goals;
3. capsule files;
4. applicable `AGENTS.md`;
5. project docs and test conventions;
6. existing implementation patterns.

Normative detail owners:

- `story-capsule-contract.md`: capsule structure;
- `validation-contract.md`: validation/evidence status;
- `no-legacy-contract.md`: No Legacy interpretation;
- `condamad-regression-guardrails`: shared invariant registry workflow;
- `condamad-feedback-loop`: accepted feedback propagation;
- `condamad-frontend-dev`: frontend implementation, validation, and guardrails.

## 3. Inputs

Accept one of:

- a CONDAMAD capsule directory;
- a single story markdown file, including legacy BMAD;
- a story body in the prompt.

If no capsule exists, persist one before implementation. Never implement from an
in-memory capsule. Do not ask the user to create generated files manually unless
story content or filesystem access is missing.

## 4. Required Capsule

Required files:

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

Optional files: `02-context-map.md`, `05-implementation-plan.md`,
`08-subagent-briefs.md`, `09-dev-log.md`.

When generating or repairing a capsule, use `scripts/condamad_prepare.py` and
`scripts/condamad_validate.py` when available. Preserve human-owned story intent:
do not rewrite ACs, business scope, or non-goals unless the user explicitly asks.

## 5. Non-Negotiables

Workspace safety:

- locate repository root before editing;
- run `git status --short` before and after editing when `.git` exists;
- if `.git` is absent, record `not a git repository` once and skip git commands;
- record dirty files in `generated/09-dev-log.md` or final evidence;
- never overwrite unrelated user changes;
- never run destructive git commands, amend, squash, reset, rebase, or
  force-push unless explicitly requested;
- delete files only when justified by the story/plan.

Command hygiene:

- prefer `apply_patch` for manual edits;
- in PowerShell snippets, avoid ambiguous interpolation such as `"$p:$i"`; use
  `"{0}:{1}" -f $p,$i` or `${p}`;
- use `rg`/targeted reads before broad inventories;
- avoid root-wide inventories unless necessary; exclude build/cache paths;
- do not include `__pycache__`, `.pytest_cache`, `.ruff_cache`, or compiled
  outputs in evidence;
- do not recursively enumerate cache directories to prove or clean them. If
  cleanup is needed, check fixed known paths or touched roots with `Test-Path`
  / `Resolve-Path`, verify they are inside the workspace, then remove them
  without printing child contents;
- for Python validation prefer `python -B -m pytest ...` after venv activation
  when repository instructions require a venv;
- prefer scoped formatting over root formatting unless the repo/story requires
  root-wide formatting.

Scope:

- implement only the current story;
- no opportunistic unrelated refactors or dependencies;
- do not change public behavior or ACs unless the story requires it;
- for audit-sourced stories, stop if the story claims closure but lacks exact
  surface, closure map, stop condition, before/after evidence, or anti-return
  guard requirements.

DRY / No Legacy forbidden unless explicit:

- compatibility wrappers, transitional aliases, re-export legacy modules;
- legacy import paths or duplicate active implementations;
- silent fallback behavior;
- root-level service files when a canonical namespace exists;
- tests that preserve legacy paths as nominal behavior.

Required when relevant:

- one canonical path per responsibility;
- negative search evidence for removed symbols/imports;
- tests or guards preventing legacy reintroduction;
- explicit error behavior instead of silent fallback;
- safe deletion of obsolete code in scope.

## 6. Frontend Delegation

If a story touches frontend code, tests, styles, build tooling, React behavior,
Tailwind/shadcn, TanStack Query, Zustand, forms, routing, or Playwright flows,
use `condamad-frontend-dev` as the dedicated frontend implementation subagent.

Main CONDAMAD agent owns the capsule, source precedence, scope, final evidence,
story status, and final response. The frontend subagent owns assigned
`frontend/**` implementation and reports evidence. Review and integrate its
result before marking ACs complete.

Prompt shape:

```text
Use $condamad-frontend-dev for story <story-key>.
You are not alone in the codebase; do not revert unrelated changes.
Ownership: frontend/** [plus explicit evidence files if assigned].
Goal: <frontend goal>.
Acceptance criteria: <relevant ACs>.
Regression guardrails: <RG list/evidence>.
Validation expected: <commands from validation plan/package scripts>.
Implement the smallest coherent change, add/update tests, run feasible checks,
and report changed files, validation, skipped checks with reasons, static guard
results, registry updates needed, risks.
```

Do not let multiple subagents edit the same frontend files concurrently unless
the user explicitly requests a parallel worktree strategy.

## 7. Workflow

1. **Preflight**
   Locate root, inspect git status, read applicable `AGENTS.md`, ensure or
   create `_condamad/stories/regression-guardrails.md`, resolve scoped
   guardrails, identify one story/capsule, and stop if none is accessible.

2. **Generate or validate capsule**
   For a story file/body, infer a stable story key, create the capsule, persist
   `00-story.md`, generate required files, then validate. For an existing
   capsule, confirm required files and regenerate missing generated files only
   without overwriting user evidence.

3. **Load story context**
   Read required capsule files in Section 4 plus scoped guardrail evidence and
   optional context files only when useful. Extract story key, goal, ACs,
   non-goals, changed-area constraints, validation expectations, forbidden
   legacy patterns, guardrail IDs, and whether frontend delegation is required.

   For audit-sourced stories, also read the referenced finding/candidate and
   nearby same-domain stories when paths exist. Classify source closure as
   `full-closure`, `phased-with-map`, `blocked`, or `non-domain`; do not
   implement under-scoped closure claims.

4. **Inspect before editing**
   Use targeted `rg` and file reads. Adapt searches to the story. Include
   legacy/compat/fallback and import scans when relevant.

5. **Plan**
   Create or update `generated/05-implementation-plan.md` when useful. Include
   architecture finding, approach, files, tests, frontend assignment, deletion
   candidates, No Legacy stance, and rollback strategy. This is not a user
   approval request unless a HALT condition is met.

6. **Implement**
   Patch in small coherent increments. Reuse existing abstractions, update
   imports to canonical paths, delete obsolete paths when required, and add or
   update tests/guards for each AC before considering it complete. If prior
   review findings exist, read them first, convert unresolved findings into
   traceability entries, fix higher-severity issues before cleanup, and record
   code plus validation evidence for each resolution.

7. **Validate**
   Run the story validation plan in order: targeted tests, architecture/negative
   scans, lint/static checks, broader regression suite, project quality gate.
   Also run applicable regression guard commands. Record exact command, result,
   skipped reason, and risk for every skipped check.

   Typical backend commands, adjusted to repo instructions:

   ```bash
   ruff format <changed python files or touched dirs>
   ruff check .
   python -B -m pytest -q
   ```

   Typical frontend evidence includes package script discovery, `pnpm lint`,
   `pnpm typecheck`, `pnpm test`, `pnpm test:e2e` when required by flow risk,
   static guards, and applicable `RG-XXX` commands or documented skips.

8. **Review diff**
   When `.git` exists, run `git diff --stat` and review `git diff`. Confirm no
   unrelated churn, forbidden legacy, unjustified deletions, unproved ACs, or
   unclassified audit residual work. When `.git` is absent, use scoped file
   inventories instead.

9. **Complete evidence**
   Update `03-acceptance-traceability.md`, `09-dev-log.md` when useful,
   `10-final-evidence.md`, `story-status.md`, and guardrails if new durable
   invariants were created or changed. Route accepted reusable learning through
   `condamad-feedback-loop`; otherwise record `no-propagation` or deferred
   rationale.

10. **Final response**
    Respond in the user's language using the response budget in Section 8.

## 8. Response Budget

Persist detail in capsule evidence, not chat. Chat is for status and decisions.

During execution:

- send only meaningful progress updates, normally one or two sentences;
- do not paste capsule tables, diff excerpts, command inventories, or AC lists;
- give at most one mini-plan, max five items, and only before substantial work;
- when a check fails, summarize the cause and next action, not the full output;
- mention repeated known dirty-worktree context once, then stop repeating it.

Final response:

- target 8-14 lines unless the user asks for detail;
- include story key/status, 2-4 implementation bullets, grouped changed files,
  validation summary, skipped checks/risks only when non-empty, reviewer focus;
- group files by area and use `path/**` for capsule/evidence directories;
- do not list every test file or every command when final evidence already does;
- do not repeat that Python used the venv unless it is a risk or user asked;
- do not duplicate the final response content elsewhere in chat.

## 9. Status And Evidence

`generated/03-acceptance-traceability.md` must classify every AC as `PASS`,
`PASS_WITH_LIMITATIONS`, `FAIL`, or `BLOCKED`, with code and validation
evidence.

`generated/10-final-evidence.md` must include story status, AC validation,
changed/deleted files, tests added/updated, commands run, skipped checks,
Legacy/DRY evidence, remaining risks, reviewer focus, frontend subagent result
when applicable, source finding closure status when audit-sourced, and feedback
loop routing.

Synchronize `_condamad/stories/story-status.md`:

- `ready-to-review`: implementation evidence complete and review-ready;
- `done`: review evidence exists;
- `ready-to-dev`: implementation incomplete but story remains implementable.

Preserve existing story ID/key/title/path/source unless this run generated the
story. Update `Last update` to local `YYYY-MM-DD`. Do not mark final evidence
ready for review without matching `story-status.md`.

For legacy BMAD stories, preserve the original contract. Only update allowed
sections such as Tasks/Subtasks, Dev Agent Record, File List, Change Log, and
Status.

## 10. HALT Conditions

Stop with a precise blocker only when:

- story/capsule or required repository instructions are inaccessible;
- required secret/config/dependency is missing and cannot be inferred safely;
- implementation requires an unapproved new dependency;
- validation fails repeatedly and no safe fix is clear;
- requested change is destructive or outside story scope;
- ACs require contradictory behavior;
- user explicitly asks to stop.

Do not stop merely because the story is large or a milestone was reached.

## 11. Completion Bar

A story is complete only when:

- every AC has implementation and validation evidence or a documented blocker;
- relevant tests/checks pass or limitations are honestly classified;
- no unrelated files changed;
- no forbidden legacy path remains unclassified;
- audit-sourced closure claims have no hidden in-domain residual work;
- final evidence and story registry are synchronized;
- final git status is reported, or `not a git repository` was recorded.

## 12. Helper Scripts

Available helpers under `scripts/`:

- `condamad_prepare.py`: create a capsule from a story markdown file.
- `condamad_validate.py`: validate capsule structure/evidence readiness.
- `condamad_legacy_scan.py`: scan selected paths for legacy patterns.
- `condamad_collect_evidence.py`: capture git status and diff-stat evidence.

Scripts assist agent judgment; investigate conflicts between script output and
repository evidence.

## 13. Final Response Template

```md
Story `<story-key>`: `ready-to-review`.

Implémenté: <2-4 bullets or one sentence>.

Fichiers: `<main area>`, `<tests area>`, `_condamad/stories/<story-key>/**`.

Validation: targeted tests PASS; lint/static PASS; capsule validation PASS.

Non lancé: <only if any>.

Risques: <only if any>.

Focus review: <one specific point>.
```
