---
name: condamad-dev-review-fix-story
description: >
  Orchestrate an efficient end-to-end CONDAMAD story workflow: implement exactly
  one story with condamad-dev-story, run independent read-only subagent review
  layers when Codex subagents are available and the current user request
  explicitly authorizes delegation, fix accepted findings, re-review until clean,
  and close the story
  without automatic commit or push unless the user explicitly asks for it. Use
  when the user asks to develop a story with independent review, run dev then
  review/fix, finish a CONDAMAD story end-to-end, or use dedicated subagents for
  story review after implementation.
---

<!-- Skill orchestrateur CONDAMAD pour developper, revoir et corriger une story avec separation de contexte. -->

# CONDAMAD Dev Review Fix Story

## Objective

Implement and close exactly one CONDAMAD story with a short, effective
orchestration loop:

1. Use `../condamad-dev-story/SKILL.md` to implement the story.
2. Run independent read-only review layers, using dedicated subagents only when
   the current user request explicitly authorizes delegation.
3. Use `../condamad-code-review/SKILL.md` as the authoritative review doctrine.
4. Use `../condamad-review-fix-story/SKILL.md` for the review/fix/re-review
   closure loop.
5. Keep final triage, fixes, validation, and status synchronization in the main
   Codex session.

This skill composes existing CONDAMAD skills. Do not duplicate or weaken their
rules. The only wrapper-specific override is that `condamad-review-fix-story`
must not commit or push unless the current user request explicitly asks for it.

## Required inputs

Accept one target:

- a CONDAMAD story capsule directory;
- a CONDAMAD story file such as
  `_condamad/stories/story-key/00-story.md`;
- a single source story markdown file that `condamad-dev-story` can convert
  into a capsule;
- the currently active story only when user context identifies exactly one.

If more than one plausible target exists, stop and ask for the exact story path.
Never run this workflow for multiple stories in one execution.

## Source of truth

Apply instructions in this order:

1. System/developer safety rules and tool constraints.
2. Current user request.
3. Repository `AGENTS.md` files for touched paths.
4. Target story acceptance criteria and explicit non-goals.
5. CONDAMAD capsule evidence.
6. This wrapper's explicit no-auto-commit/no-auto-push rule.
7. `condamad-dev-story`, `condamad-code-review`, and
   `condamad-review-fix-story`.
8. Existing implementation patterns.

Do not weaken acceptance criteria, validation requirements, or review findings
to make the workflow pass.

## Subagent authorization

Use dedicated subagents for the review phase only when the current user request
explicitly authorizes delegation. Explicit authorization includes either:

- the user explicitly names this skill, for example
  `$condamad-dev-review-fix-story`; or
- the user asks for subagents, delegated agents, parallel review, or dedicated
  independent reviewers.

If this skill is selected implicitly from a broad request such as "finish this
story end to end", do not spawn subagents unless the user also authorized
delegation.

Subagent rules:

- Use subagents only after the development phase has produced a readable story
  capsule, implementation diff, and validation evidence.
- Use subagents only for read-only review layers.
- Do not let subagents modify files, run mutating commands, commit, push, or
  update evidence.
- Give subagents only the minimum task-local context: story path, repository
  root, allowed inputs, and review mission.
- Treat subagent outputs as findings candidates, not final truth.
- The main Codex session owns final triage, corrections, validation, review
  evidence, and status synchronization.

If subagents are unavailable or not authorized, run the same review layers
sequentially in the main session and record that no subagent delegation was used.

## Context isolation policy

Before the review phase, rebuild review context from durable repository
evidence:

- applicable `AGENTS.md`;
- target `00-story.md`;
- generated capsule files;
- `_condamad/stories/regression-guardrails.md`;
- `git status --short`;
- `git diff --stat` and `git diff`;
- files changed by the story;
- tests and validation commands actually run.

The development summary may be used only as an index of touched areas. It is not
evidence that the implementation is correct.

## Workflow

### 1. Preflight

1. Locate the repository root.
2. Run `git status --short` and record pre-existing dirty files.
3. Read applicable `AGENTS.md` files.
4. Resolve exactly one story target.
5. Ensure `_condamad/stories/regression-guardrails.md` exists and read it.

Preserve unrelated dirty files. Do not overwrite user changes.

### 2. Development

Run `condamad-dev-story` on the target story.

Required outcome before review:

- implementation is complete or a blocker is recorded;
- relevant tests and validation commands were run or honestly classified as not
  run;
- `generated/10-final-evidence.md` is complete when a capsule exists;
- `_condamad/stories/story-status.md` is `ready-to-review` for the target
  story when implementation is complete.

If development blocks, stop and report the blocker. Do not start review on an
incomplete implementation unless the user explicitly asks for a partial review.

### 3. Independent review layers

After development, rebuild context using the isolation policy, then launch the
independent review layers. When subagents are authorized and available, run the
two read-only review layers in parallel. Otherwise, run them sequentially in the
main session.

#### Story Conformance Reviewer

Inputs:

- target `00-story.md`;
- generated acceptance and final evidence files;
- `git diff`;
- files changed by the story.

Mission:

- compare acceptance criteria to implementation;
- find missing proof, missing tests, forgotten scope, or unintended scope;
- avoid refactor-only suggestions.

#### Technical Risk Reviewer

Inputs:

- applicable `AGENTS.md`;
- generated validation and No Legacy evidence;
- `_condamad/stories/regression-guardrails.md`;
- `git diff`;
- files changed by the story and relevant tests.

Mission:

- find runtime bugs, broken imports, data/API risks, missing tests, validation
  gaps, DRY violations, No Legacy violations, and regression-guardrail gaps.

Each review layer must return findings with severity, file/line evidence when
possible, reason, and expected correction. If it finds no issue, it must say
that clearly and list residual validation risk.

Then run one full `condamad-code-review` pass as the authoritative review. Feed
only evidence-backed layer findings into the main triage; do not treat layer
findings as accepted until the main session has verified them against repository
evidence.

### 4. Triage and fixes

Merge the `condamad-code-review` result and independent review-layer findings.

For each candidate finding:

- accept it only when it is evidence-backed and actionable;
- reject false positives explicitly in the review evidence or dev log;
- fix accepted findings with the smallest coherent patch;
- add or update tests/guards when the finding exposes behavior or regression
  risk;
- update `generated/10-final-evidence.md` and `generated/11-code-review.md`
  when a capsule exists.

### 5. Re-review loop

Use `condamad-review-fix-story` for the closure loop, with this mandatory
wrapper override:

- do not commit or push unless the current user request explicitly asks for
  commit and push.
- if `condamad-review-fix-story` says to commit or push as part of closure,
  stop before that step, report the uncommitted clean state, and wait for an
  explicit commit/push request.

Repeat review, fix, and validation until a fresh review reaches `CLEAN` or
`ACCEPTABLE_WITH_LIMITATIONS` with all required validation evidence present. Do
not treat optional residual validation risk as a finding unless the story,
guardrails, or repository instructions require that validation.

Stop only for a real blocker: missing story, unreadable required instructions,
unsafe destructive change, conflicting acceptance criteria, repeated validation
failure with no safe fix, or a user stop request.

### 6. Final closure

Before final response:

1. Run required final validation from the story and repository instructions.
2. Run `git status --short`.
3. Review `git diff --stat` and `git diff` for scope.
4. Synchronize `_condamad/stories/story-status.md`:
   - `done` only when the fresh review is clean or acceptable with complete
     required validation;
   - `ready-to-review` when findings remain or validation is incomplete.
5. Commit and push only when explicitly requested by the user.

## Final response

Respond in French. Include:

- story key and final status;
- whether subagents were used;
- number of review/fix iterations;
- findings fixed or rejected by category;
- files changed;
- validations run and result;
- commit and push result only when requested;
- remaining risks, or `Aucun risque restant identifie`.
