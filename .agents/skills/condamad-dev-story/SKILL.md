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
  Treat repeated status drift, stale pre-implementation reviews, weak route
  scans, cwd-dependent guards, and pnpm EPERM fallback patterns as reusable
  learning candidates instead of defaulting to no-propagation.
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
- final consistency gate across story, status, traceability, final evidence,
  and existing code review artifacts;
- no compatibility shim, alias, fallback, duplicate active path, or transitional
  legacy unless the story explicitly requires it.

## 2. Compact Loading Policy

Start from the target story/capsule and load only decision-relevant context.

Always read, but keep generated capsule loading compact:

- target `00-story.md`;
- a compact generated capsule summary containing story key, ACs, non-goals,
  target paths, validation commands, and guardrails;
- applicable repository `AGENTS.md`;
- scoped regression guardrail IDs already named by the story/capsule, or a
  resolver/search result for the touched surface.

Read a full generated capsule file only when the compact summary is missing,
conflicting, or insufficient for the next decision. Do not read all files under
`generated/` in full by default. The summary should stay within 80-120 lines.

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

Do not `Get-Content` or otherwise print an entire application file when
`rg -n`, a symbol search, or a line-bounded excerpt is enough. Treat broad file
reads as expensive: use at most two broad reads before editing, then switch to
targeted symbol/line reads unless new evidence justifies another broad read.

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
`08-subagent-briefs.md`, `09-dev-log.md`, `11-code-review.md`.

When generating or repairing a capsule, use `scripts/condamad_prepare.py` and
`scripts/condamad_validate.py` when available. Preserve human-owned story intent:
do not rewrite ACs, business scope, or non-goals unless the user explicitly asks.

Use `scripts/condamad_capsule_summary.py <capsule>` when available to load the
compact capsule summary. For an existing capsule, prefer repair-only generation
(`condamad_prepare.py --repair-generated-only <capsule>`) over re-preparing from
the story source. If a `CS-xxx` story already appears in `story-status.md`, pass
`--story-key` or `--capsule`; do not allow title-based inference to create a
parallel capsule.

## 5. Non-Negotiables

Workspace safety:

- locate repository root before editing;
- run `git status --short` before and after editing when `.git` exists;
- if `.git` is absent, record `not a git repository` once and skip git commands;
- record dirty files in `generated/09-dev-log.md` or final evidence;
- never overwrite unrelated user changes;
- never run destructive git commands, amend, squash, reset, rebase, force-push,
  commit, or push; repository publication is owned by the orchestrator;
- delete files only when justified by the story/plan.

Command hygiene:

- prefer `apply_patch` for manual edits;
- in PowerShell snippets, avoid ambiguous interpolation such as `"$p:$i"`; use
  `"{0}:{1}" -f $p,$i` or `${p}`;
- use `rg`/targeted reads before broad inventories;
- prefer `rg -n` plus line-bounded excerpts over `Get-Content` on whole source
  files; never print a full application file only to inspect one symbol;
- avoid root-wide inventories unless necessary; exclude build/cache paths;
- do not include `__pycache__`, `.pytest_cache`, `.ruff_cache`, or compiled
  outputs in evidence;
- do not recursively enumerate cache directories to prove or clean them. If
  cleanup is needed, check fixed known paths or touched roots with `Test-Path`
  / `Resolve-Path`, verify they are inside the workspace, then remove them
  without printing child contents;
- for Python validation prefer `python -B -m pytest ...` after venv activation
  when repository instructions require a venv;
- standardize Python commands from the repository root; in PowerShell, activate
  the documented venv first when required, then run `python -B -m ...`;
- prefer scoped formatting over root formatting unless the repo/story requires
  root-wide formatting.

Evidence strength:

- do not use `rg` as the only critical proof when a structured source exists;
- for FastAPI/Starlette routes or API contracts, prove behavior with
  `app.routes`, `app.openapi()`, route-level tests, or equivalent structured
  introspection before accepting negative/positive text scans;
- for Python imports, symbols, and source ownership, prefer AST parsing,
  importing the module under the repo's test environment, or
  `inspect.getsource()` over raw text scans;
- for TypeScript imports/routes/contracts, prefer parser-backed checks,
  compiler/typecheck output, or targeted guard tests over raw text scans;
- `rg` remains acceptable as supplemental negative evidence, legacy cleanup
  evidence, or a first-pass locator, but not as the sole proof for an AC or
  architecture invariant when structured inspection is practical.

CWD-independent tests and guards:

- any test or guard that reads repository files must resolve paths from the
  repository root, test file location, package root, or an imported module's
  `__file__`; never rely on the process current directory implicitly;
- prefer module introspection over filesystem reads when checking Python code
  ownership/import behavior;
- if a guard intentionally runs from a package directory, record that
  assumption and add a root-independent path resolver.

Scope:

- implement only the current story;
- no opportunistic unrelated refactors or dependencies;
- do not change public behavior or ACs unless the story requires it;
- for audit-sourced stories, stop if the story claims closure but lacks exact
  surface, closure map, stop condition, before/after evidence, or anti-return
  guard requirements.
- for audit-sourced stories, prepare a compact closure map before code:
  exact surface, forbidden symbols, existing guards, tests to modify, and stop
  condition.

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

Windows frontend mode:

- discover available scripts first (`package.json`, local scripts directory,
  package manager metadata) before choosing commands;
- on Windows, prefer repository-stable commands already present in the project
  when package-manager wrappers trigger locks or `EPERM`, for example
  `node .\scripts\run-vite-logged.mjs ...` for logged Vite runs and
  `.\node_modules\.bin\tsc.cmd` for TypeScript;
- when `pnpm` creates `frontend/pnpm-lock.yaml` accidentally in a repo that
  owns the lockfile elsewhere, remove the accidental lockfile after verifying
  it is not the canonical project lockfile and record the cleanup.

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

   If `generated/11-code-review.md` already exists before implementation, read
   it before using it as evidence. If it is a draft, pre-implementation,
   planning, or stale `CLEAN` review, mark it obsolete in place or add a clear
   handoff note stating it is not final review evidence. Do not let a
   pre-implementation `CLEAN` review satisfy the final review/evidence bar.

3. **Load story context**
   Load the compact capsule summary plus scoped guardrail evidence and optional
   context files only when useful. Extract story key, goal, ACs, non-goals,
   changed-area constraints, validation expectations, forbidden legacy patterns,
   guardrail IDs, and whether frontend delegation is required. Read a full
   generated file only on conflict, missing summary data, or when editing it.

   For audit-sourced stories, also read the referenced finding/candidate and
   nearby same-domain stories when paths exist. Classify source closure as
   `full-closure`, `phased-with-map`, `blocked`, or `non-domain`; do not
   implement under-scoped closure claims.

4. **Inspect before editing**
   Use targeted `rg` and file reads. Adapt searches to the story. Include
   legacy/compat/fallback and import scans when relevant.

   Run an architecture guard preflight before introducing sensitive domain
   vocabulary or namespaces such as doctrine, profile, school, runtime, canonical
   services, or known legacy imports. Read the relevant guard tests first, scan
   for forbidden terms/imports, and verify any new guard-test string against the
   existing guards before running broad pytest.

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
   Use an economical validation ladder. First run fast scans for forbidden
   terms, legacy imports, boundary violations, conflict markers, and guardrail
   IDs. Then run targeted tests, architecture/negative scans, lint/static
   checks, broader regression suite, and project quality gate. Stop and fix
   short-guard failures before expensive full-suite validation. Also run
   applicable regression guard commands. Record exact command, result, skipped
   reason, and risk for every skipped check.

   Typical backend commands, adjusted to repo instructions:

   ```bash
   ruff format <changed python files or touched dirs>
   ruff check .
   python -B -m pytest -q --tb=short
   ```

   Typical frontend evidence includes package script discovery, `pnpm lint`,
   `pnpm typecheck`, `pnpm test`, `pnpm test:e2e` when required by flow risk,
   static guards, and applicable `RG-XXX` commands or documented skips.

8. **Review diff**
   When `.git` exists, first run `git diff --stat -- <paths>` and
   `git diff --name-only -- <paths>` for the story surface. Use full
   `git diff -- <file>` only for targeted internal review of changed files.
   Confirm no unrelated churn, forbidden legacy, unjustified deletions,
   unproved ACs, or unclassified audit residual work. When `.git` is absent,
   use scoped file inventories instead.

9. **Complete evidence**
   Update `03-acceptance-traceability.md`, `09-dev-log.md` when useful,
   `10-final-evidence.md`, `story-status.md`, and guardrails if new durable
   invariants were created or changed. Route accepted reusable learning through
   `condamad-feedback-loop`; otherwise record `no-propagation` or deferred
   rationale.

10. **Internal reviewer simulation**
    Before handoff, simulate the reviewer checks yourself and fix any issue
    found:

    - every AC has fresh code and validation evidence;
    - non-goals stayed untouched;
    - final evidence is not copied from stale or pre-implementation review
      artifacts;
    - story status, traceability, final evidence, and review notes agree;
    - guards are cwd-independent and use structured proof when available;
    - skipped commands have risk and compensating evidence;
    - no proof is too weak for the claimed AC or invariant.

11. **Final consistency gate**
    Immediately before the final response, read and compare:
    `00-story.md`, `_condamad/stories/story-status.md`,
    `generated/03-acceptance-traceability.md`,
    `generated/10-final-evidence.md`, and every existing
    `generated/11-code-review.md`.

    The run must not close as implementation-ready if any artifact still says
    `ready-to-dev`, `BLOCKED`, draft, stale, or pre-implementation while the
    implementation evidence is ready. Resolve the artifact, mark stale review
    content obsolete, or downgrade the run honestly to blocked. Run
    `scripts/condamad_validate.py <capsule> --final` after this gate when the
    helper exists.

12. **Final response**
    Respond in the user's language using the response budget in Section 8.

## 8. Response Budget

Persist detail in capsule evidence, not chat. Chat is for status and decisions.

Output compression:

- write long command output, proof details, diff notes, and failure transcripts
  to capsule evidence files under `generated/` or `evidence/`;
- keep chat/log output to status, path, concise result, and next action;
- for long pytest runs, use `--tb=short` first and rerun only the failing test
  with fuller output when needed;
- after an orchestrator prints token usage or run metadata, do not repeat the
  final response body.

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

`generated/11-code-review.md`, when present, must be classified as final,
obsolete, or handoff-only. A pre-implementation or draft review cannot be cited
as final review evidence.

Synchronize `_condamad/stories/story-status.md`:

- `ready-to-review`: implementation evidence complete and review-ready;
- `done`: review evidence exists;
- `ready-to-dev`: implementation incomplete but story remains implementable.

Preserve existing story ID/key/title/path/source unless this run generated the
story. Update `Last update` to local `YYYY-MM-DD`. Do not mark final evidence
ready for review without matching `story-status.md`.

Update only the exact row matching `^| CS-xxx |` when a story ID exists. Use a
compact before/after row as evidence; never print the whole story registry.

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
- final consistency gate has passed across story, registry, traceability, final
  evidence, and code review artifacts;
- final git status is reported, or `not a git repository` was recorded.

## 12. Helper Scripts

Available helpers under `scripts/`:

- `condamad_prepare.py`: create a capsule from a story markdown file.
- `condamad_capsule_summary.py`: print an 80-120 line capsule summary for
  loading context without full generated-file reads.
- `condamad_update_story_status.py`: replace one exact `CS-xxx` registry row
  and print only before/after rows.
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
