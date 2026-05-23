<!-- Etape de cadrage pour identifier la story et les preuves redactionnelles. -->

# Step 1 - Target and Context

## Objective

Identify exactly which story contract is being reviewed and load only the
context required for a reliable editorial review.

## Actions

1. Locate the repository root.
2. Resolve the story target in this order:
   - explicit story file or CONDAMAD capsule path from the user;
   - tracker row in `_condamad/stories/story-status.md`;
   - active story file mentioned in recent context.
3. Read only the story drafting artifacts needed for the review:
   - `00-story.md` or story markdown;
   - `_condamad/stories/story-status.md` matching row;
   - source brief, audit finding, or story candidate when referenced;
   - `generated/11-code-review.md` when present;
   - scoped `RG-XXX` rows when the story names guardrails.
4. Run story validation and strict lint when the story file exists.
5. Check the story contract for target files, tests, validation plan, non-goals,
   guardrails, dependency policy, review artifact path, and status.
6. Prepare `generated/11-code-review.md` for the editorial review result when a
   CONDAMAD capsule exists.

Do not collect git diff baselines, inspect implementation files, or review
application code in this skill.

## Required Context Summary

Before reviewing, know:

- story key and story path;
- source brief or audit source;
- current story status;
- ACs and non-goals;
- expected files and tests;
- validation and strict lint result;
- scoped guardrail IDs;
- existing review artifact path, if any.

## Halt Conditions

Stop only when:

- no story target can be identified;
- required story/capsule files are inaccessible;
- story validation cannot run and no safe diagnostic can be recorded.

Otherwise continue to Step 2.
