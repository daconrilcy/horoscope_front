<!-- Doctrine de revue redactionnelle adversariale CONDAMAD. -->

# Review Doctrine

## Purpose

CONDAMAD Story Draft Review is an adversarial quality gate after story drafting.
The reviewer challenges whether the story contract is precise enough for a dev
agent to implement safely, validate locally, and avoid scope drift.

This file lives under the `condamad-story-draft-review` skill path. The
doctrine is editorial story review, not application-code review.

## Review Mindset

Assume the story may be subtly ambiguous even when validation passes.

Prefer concrete evidence over confidence:

- source brief or audit finding;
- story status and tracker row;
- acceptance criteria;
- validation plan and strict lint output;
- scoped regression guardrails;
- non-goals and forbidden paths;
- review artifact path.

## Required Review Layers

### 1. Source Alignment Review

Check:

- source objective is preserved;
- domain boundary is exactly one domain;
- non-goals match source constraints;
- target files and tests match the source;
- review artifact path is separate and canonical.

### 2. Acceptance Audit

For each AC:

- identify the exact observable requirement;
- identify the validation evidence;
- flag missing, partial, compound, or contradicted evidence;
- verify tasks map back to ACs.

### 3. Validation Audit

Check whether validation commands are:

- exact;
- relevant;
- executable locally;
- tied to ACs;
- honest about skipped or future implementation checks.

Do not claim validation passed unless the exact story validator and strict lint
commands ran successfully.

### 4. DRY / No Legacy Audit

Challenge whether the story forbids:

- duplicate active paths;
- compatibility wrappers;
- aliases and re-exports;
- fallback behavior;
- old imports or registry keys;
- tests/docs that preserve legacy behavior as supported.

### 5. Guardrail Audit

Check:

- scoped guardrails are listed;
- unrelated guardrails are not copied wholesale;
- registry gaps are recorded without normal-mode registry edits;
- required regression evidence maps to the story's scope.

## False CLEAN Prevention

Never return `CLEAN` when:

- story validation or strict lint fails;
- an AC lacks concrete evidence;
- the source brief is not covered;
- status/tracker rows are inconsistent;
- review artifact path is wrong or ambiguous;
- dependency policy is missing or contradicted;
- No Legacy constraints are missing for a story that creates, changes, or
  removes routes, contracts, or namespaces.
