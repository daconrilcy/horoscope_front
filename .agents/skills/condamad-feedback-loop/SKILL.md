---
name: condamad-feedback-loop
description: >
  Run a CONDAMAD feedback loop after a correction, failed validation, review
  finding, regression, or repeated skill mistake that should become durable
  learning. Capture, classify, apply the smallest validated fix, and propagate
  accepted learning to evidence, tests, guardrails, AGENTS.md, or the owning
  skill. Do not use for tiny contained edits.
---

<!-- Skill CONDAMAD pour transformer les retours en apprentissages durables et reutilisables. -->

# CONDAMAD Feedback Loop

## Role

Act as the CONDAMAD feedback integrator. Your responsibility is to transform
feedback into the smallest durable improvement that prevents the same issue from
recurring, while preserving the authority of the owning story, review,
guardrail, implementation, or skill workflow.

Stay evidence-first and conservative:

- distinguish facts, risks, preferences, and missing proof;
- accept feedback only when it is actionable and supported by context;
- reject or defer feedback explicitly when it is out of scope, contradictory,
  or insufficiently evidenced;
- route fixes to the skill or workflow that owns the affected surface;
- never use feedback to downgrade review findings, weaken acceptance criteria,
  or skip validation.

## Objective

Convert feedback into durable improvement without turning every comment into a
large refactor. The loop must preserve the current source of truth, separate
facts from preferences, and decide whether the right output is code, tests,
story evidence, guardrails, documentation, or a skill update.

This skill composes existing CONDAMAD skills. It does not replace
implementation, review, frontend, audit, or story-writing workflows.

## When not to use

Do not run this loop when:

- the fix is a one-off typo or local edit with no recurrence risk;
- the feedback is only a personal preference and does not affect correctness,
  evidence, workflow, or reusable skill behavior;
- the target spans unrelated stories, skills, or domains;
- the required response is already fully covered by the owning skill and no
  propagation is needed.

## Recursion guard

Run at most one feedback loop for a closure event. If feedback concerns this
feedback-loop skill itself, update only this skill or its references, validate
the change, record the result, and stop.

Do not start a second feedback loop from the closure of the first one unless the
user explicitly requests it.

## Required inputs

Accept one bounded feedback target:

- a user correction in the current conversation;
- a review finding or review evidence file;
- a failed validation log;
- a CONDAMAD story capsule;
- a regression guardrail gap;
- an existing skill that should learn from repeated feedback;
- a small set of related artifacts that all describe the same issue.

If the feedback target is ambiguous or spans unrelated domains, stop and ask for
the exact target. Do not run a single feedback loop over unrelated stories,
skills, and product areas.

## Source of truth

Apply instructions in this order:

1. System/developer safety rules and tool constraints.
2. Current user request.
3. Repository `AGENTS.md` files for touched paths.
4. Target story, review, audit, guardrail, or skill artifacts.
5. Existing CONDAMAD skills relevant to the feedback domain.
6. Existing implementation patterns and validation evidence.

Do not use feedback as permission to weaken acceptance criteria, hide residual
risk, add broad exceptions, or bypass validation.

## Workflow

### 1. Capture

Record the feedback in concrete terms:

- quoted or summarized feedback;
- source artifact or conversation context;
- affected domain;
- expected outcome;
- evidence that currently supports or contradicts the feedback.

Use `references/feedback-record.md` as the durable record shape when writing
story evidence, review notes, guardrail updates, or skill-change notes.

### 2. Classify

Classify each feedback item into exactly one primary category:

- `bug`: runtime, data, integration, or user-visible behavior is wrong;
- `test-gap`: behavior is correct or unclear, but regression coverage is weak;
- `evidence-gap`: implementation may be correct, but proof is missing;
- `workflow-gap`: the process missed a required step or produced confusion;
- `skill-gap`: a reusable skill needs clearer instructions or resources;
- `story-gap`: acceptance criteria, scope, or closure map is under-specified;
- `preference`: style or workflow preference that does not change correctness;
- `non-actionable`: insufficient evidence or outside the current scope.

If multiple categories apply, choose the category that determines the first
required change. Mention secondary categories in the record.

### 3. Decide

For each item, choose the smallest durable response:

- code fix plus targeted test when behavior is wrong;
- test or guardrail update when the missing protection is the issue;
- evidence update when the implementation is already sufficient;
- story recut or clarification when the scope is wrong;
- skill update when the same mistake could recur across executions;
- AGENTS.md update when the learning is a repository-wide operating rule;
- no change with rationale when feedback is non-actionable or out of scope.

Prefer updating an existing skill over creating a new one when the feedback
belongs to that skill's normal responsibility. Create a new skill only when the
loop itself is reusable across several workflows.

### 4. Apply

Apply changes through the domain skill that owns the affected surface:

- Use `../condamad-dev-story/SKILL.md` for story implementation fixes.
- Use `../condamad-code-review/SKILL.md` for review doctrine updates or review
  evidence.
- Use `../condamad-review-fix-story/SKILL.md` for review-to-fix closure loops.
- Use `../condamad-frontend-dev/SKILL.md` for any frontend code, style, test,
  build tooling, or browser validation change.
- Use `../condamad-regression-guardrails/SKILL.md` for persistent regression
  guardrail creation or updates.
- Use the system `skill-creator` workflow when creating or materially updating
  skills.

When updating skills, keep the patch small:

- add or adjust triggering text only when selection failed;
- add workflow instructions only when execution failed;
- add references only when the detail is reusable but too large for `SKILL.md`;
- avoid duplicating rules already owned by another skill;
- link to the owning skill instead of copying its full doctrine.

### 5. Validate

Run validation proportional to the change:

- code changes: targeted tests, lint, and required story validation;
- frontend changes: package script discovery plus relevant lint, typecheck,
  tests, and browser checks required by the owning workflow;
- Python commands in this repository: activate `.\.venv\Scripts\Activate.ps1`
  before running `python`, `pip`, `pytest`, `ruff`, or related tools;
- skill changes: run the available skill validation script when present; if no
  validator exists, verify required frontmatter, referenced paths, YAML syntax,
  integration snippets, and absence of contradictory instructions;
- evidence-only changes: verify referenced files, paths, dates, and commands
  are accurate.

Do not mark skipped validation as passed. Record the reason and residual risk.

### 6. Propagate

After validation, decide whether the learning must be propagated:

- update the current story evidence when the feedback affects story closure;
- update `_condamad/stories/regression-guardrails.md` when it reveals a
  reusable regression pattern;
- update `AGENTS.md` only when the learning is a durable repository operating
  rule and not better owned by a narrower skill;
- update the owning skill when the process should change next time;
- update only the final response when the feedback is local and not reusable.

Before changing multiple skills, identify the owner skill and keep secondary
skills as references. Avoid conflicting instructions between skills.

### 7. Close

End the loop with:

- feedback items accepted, rejected, or deferred;
- files changed;
- validation run and result;
- integration points updated or proposed;
- remaining risks or `Aucun risque restant identifie`.

## Integration guidance

To integrate this loop into another skill, add a short handoff section instead
of duplicating the full process:

```text
When review findings, user corrections, failed validations, regressions, or
repeated execution mistakes reveal reusable learning, invoke
$condamad-feedback-loop before closure. Apply only accepted feedback, validate
the resulting code, evidence, guardrail, AGENTS.md, or skill changes, and record
any propagation.

Do not invoke the loop for one-off local edits that are fully resolved and have
no reusable learning value.

If explicit skill invocation is unavailable, read
../condamad-feedback-loop/SKILL.md and follow its workflow.
```

Use the loop at natural boundaries:

- after implementation evidence but before final closure;
- after a code review returns findings;
- after validation fails for a reason not already covered by the story;
- after a user correction shows the skill selected the wrong scope or process;
- after two similar issues recur in separate stories.

Do not use it as a mandatory ceremony for tiny, already-contained edits.
