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
  story review after implementation. During closure, invoke
  condamad-feedback-loop when review findings, user corrections, failed
  validations, regressions, or repeated execution mistakes reveal reusable
  learning that should update evidence, tests, guardrails, AGENTS.md, or an
  owning skill.
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
5. Use `../condamad-frontend-dev/SKILL.md` for every frontend implementation
   and frontend review-fix slice.
6. Invoke `../condamad-feedback-loop/SKILL.md` before closure when accepted
   feedback reveals reusable learning that must be propagated to evidence,
   tests, guardrails, AGENTS.md, or the owning skill.
7. Verify that the story is sufficient to close the finding or bounded phase it
   claims to close before spending implementation time.
8. Keep final triage, fixes, validation, and status synchronization in the main
   Codex session.

This skill composes existing CONDAMAD skills. Do not duplicate or weaken their
rules. The only wrapper-specific override is that `condamad-review-fix-story`
must not commit or push unless the current user request explicitly asks for it.
Apply `../condamad-dev-story/references/condamad-principles.md` throughout the
orchestration so SOLID, DRY, KISS, and YAGNI remain mandatory across
implementation, review, fixes, validation, and closure evidence.

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
8. `condamad-frontend-dev` for frontend implementation, frontend review fixes,
   frontend validation, and frontend static/regression guards.
9. Existing implementation patterns.

Do not weaken acceptance criteria, validation requirements, or review findings
to make the workflow pass.

When review findings, user corrections, failed validations, regressions, or
repeated execution mistakes reveal reusable learning, invoke
`$condamad-feedback-loop` before final closure and record the decision in the
review or final evidence. Apply only accepted feedback, validate the resulting
code, evidence, guardrail, AGENTS.md, or skill changes, and record any
propagation. Do not invoke the loop for one-off local edits that are fully
resolved and have no reusable learning value. If explicit skill invocation is
unavailable, read `../condamad-feedback-loop/SKILL.md` and follow its workflow.

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

Frontend exception: `condamad-frontend-dev` is the required implementation
subagent for frontend development and frontend review-fix slices through
`condamad-dev-story` and this wrapper. This is implementation delegation, not a
read-only review layer. It is mandatory when a fix touches `frontend/**`,
frontend tests, frontend styles, frontend build tooling, React behavior,
Tailwind/shadcn UI, TanStack Query, Zustand, forms, routing, or Playwright
flows.

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
6. If the story was generated from an audit, read the source audit finding,
   story candidate, latest same-domain audit if any, and nearby stories that
   already attempted the same finding.

Preserve unrelated dirty files. Do not overwrite user changes.

### 1a. Story sufficiency gate

Before implementation, decide whether the target story is closure-ready for its
declared objective.

The gate must inspect:

- source finding and candidate text;
- target story objective, scope, ACs, expected files, non-goals, and validation
  plan;
- prior stories and audits for the same domain/finding;
- applicable regression guardrails.

Pass the gate only when all are true:

- the story has exact files or an exact selection rule for the full surface it
  claims to remediate;
- it defines before/after evidence or equivalent persistent proof;
- it requires deterministic reintroduction guards for removed or converged
  debt;
- it forbids broad allowlists, wildcard exceptions, unclassified fallback,
  compatibility, legacy, migration-only, shim, alias, or `PASS with limitation`
  when the source finding expects full closure;
- its validation commands cover the changed domain and the relevant guardrails;
- any known residual work is either outside the domain, explicitly out of scope,
  or blocked by a user decision.

If the story says "next batch", "next cluster", "continue reducing", or similar
without a finite closure map and stop condition, stop before implementation and
report that the story must be recut or expanded. Do not implement an
under-scoped story that is likely to require another story for the same finding.

If the story is intentionally phased, record the exact phase boundary and the
remaining closure map in the dev log/final evidence. A phased story can be
accepted only when the phase boundary is explicit and does not claim full
closure.

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
read-only review layers in parallel. Otherwise, run them sequentially in the
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

#### Source Finding Closure Reviewer

Inputs:

- source audit finding and story candidate;
- latest same-domain audit when available;
- prior sibling stories for the same finding or domain;
- generated final evidence;
- `git diff`.

Mission:

- verify that the implementation closes the exact finding, phase, or user
  decision stated by the story;
- detect leftover application files, governance files, allowlist entries,
  unguarded literals, legacy/fallback/compatibility surfaces, or validation
  gaps that would force another story on the same subject;
- separate true residual findings from non-domain concerns.

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
- route every accepted frontend finding through `condamad-frontend-dev` before
  editing frontend files;
- fix accepted findings with the smallest coherent patch;
- add or update tests/guards when the finding exposes behavior or regression
  risk;
- for source-finding closure findings, fix the whole remaining in-domain
  surface covered by the story objective, not just the first example that made
  the reviewer fail;
- update `generated/10-final-evidence.md` and `generated/11-code-review.md`
  when a capsule exists.

Frontend review-fix rules:

- A finding is a frontend finding when its fix touches `frontend/**`, frontend
  tests, frontend styles, frontend build tooling, React behavior,
  Tailwind/shadcn UI, TanStack Query, Zustand, forms, routing, or Playwright
  flows.
- For each frontend finding batch, use `condamad-frontend-dev` as the frontend
  implementation subagent with ownership limited to `frontend/**` and explicit
  evidence files when needed.
- Pass the review finding text, story ACs, target files, applicable
  `_condamad/stories/regression-guardrails.md` IDs, and expected validation
  commands to the frontend subagent.
- Require the frontend subagent to report changed files, tests, validation
  commands, skipped checks, static guard results, applicable `RG-XXX` evidence,
  and remaining risks.
- The main session must verify the subagent output against the review finding,
  update capsule evidence, and decide whether the finding is resolved.
- Do not mark a frontend review finding resolved without code/evidence plus
  `condamad-frontend-dev` validation evidence or an explicit blocker.

Use this prompt shape for frontend review fixes:

```text
Use $condamad-frontend-dev to fix accepted frontend review findings for story <story-key>.
You are not alone in the codebase; do not revert unrelated changes.
Ownership: frontend/** [and only these explicit evidence files if needed].
Accepted findings: <finding IDs/text>.
Acceptance criteria: <relevant ACs>.
Regression guardrails: <RG-XXX list and expected evidence>.
Validation expected: <commands from story validation plan and frontend package scripts>.
Fix the smallest coherent frontend slice, add/update tests, run feasible checks, and report changed files, validation results, skipped checks with reasons, static guard results, registry updates needed, and remaining risks.
```

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

For stories sourced from audits, `ACCEPTABLE_WITH_LIMITATIONS` is not allowed
when the story objective, ACs, source finding, or regression guardrails require
full closure. In that case the loop must continue until `CLEAN`, or stop with a
real blocker and explicit evidence.

Before accepting a clean result, perform a final source-finding closure check:

- every AC is satisfied by durable evidence;
- source finding status is closed, intentionally phased, non-domain, or blocked;
- no new broad allowlist, wildcard, fallback, alias, shim, compatibility,
  migration-only, No Legacy exception, or TODO was introduced to pass tests;
- all changed frontend surfaces have exact guard coverage or a documented reason
  why existing guards already cover them.
- reusable learning from review findings, user corrections, failed validations,
  regressions, or repeated execution mistakes has either been routed through
  `condamad-feedback-loop` or explicitly classified as local/no-propagation.

Stop only for a real blocker: missing story, unreadable required instructions,
unsafe destructive change, conflicting acceptance criteria, repeated validation
failure with no safe fix, or a user stop request.

### 6. Final closure

Before final response:

1. Run required final validation from the story and repository instructions.
2. Confirm all frontend review fixes include `condamad-frontend-dev` evidence
   when any frontend surface changed.
3. Run `git status --short`.
4. Review `git diff --stat` and `git diff` for scope.
5. Synchronize `_condamad/stories/story-status.md`:
   - `done` only when the fresh review is clean or acceptable with complete
     required validation;
   - `ready-to-review` when findings remain or validation is incomplete.
6. Commit and push only when explicitly requested by the user.

## Final response

Respond in French. Include:

- story key and final status;
- whether subagents were used;
- number of review/fix iterations;
- findings fixed or rejected by category;
- frontend subagent usage and evidence when frontend fixes were involved;
- files changed;
- validations run and result;
- commit and push result only when requested;
- remaining risks, or `Aucun risque restant identifie`.
