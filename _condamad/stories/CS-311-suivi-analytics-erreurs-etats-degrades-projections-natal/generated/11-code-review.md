# CS-311 Editorial Story Review

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-311-suivi-analytics-erreurs-etats-degrades-projections-natal/00-story.md`
- Source brief: `_story_briefs/cs-311-suivi-analytics-erreurs-etats-degrades-projections-natal.md`
- Tracker row: `_condamad/stories/story-status.md`
- Guardrail lookup: scoped `RG-047` lookup only; the full registry was not read.
- Review type: compact pre-implementation story-contract review.

## Iteration 1

Finding fixed:

- The regression guardrail table used `Needs-investigation` as if it were an applicable guardrail.
  It is now a non-applicable resolver note outside the table, preserving the evidence need without creating a pseudo-guardrail.

Validation after fix:

- `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ...\00-story.md` - PASS.
- `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ...\00-story.md` - PASS.

## Final Brief Alignment Pass

Finding fixed:

- The story treated `empty` and `degraded` as generic states while the brief explicitly names missing birth data and degraded mode without time.
  The story now binds AC6, AC7, tasks, target state, and contract shape to those public UI reasons without allowing raw birth data in analytics.

## Final Review

- The story maps the brief objective to a minimal `/natal` projection analytics contract.
- The seven required events are explicit: started, success, API error, entitlement denied, empty, degraded, and retry.
- Missing birth-data empty states and degraded-without-time states are explicit and remain redacted through public `state_reason` only.
- Sensitive payload exclusions are explicit in target state, ACs, contract shape, reintroduction guards, and validation plan.
- Existing analytics ownership, frontend tests, documentation artifacts, and backend non-goals are stated without implementation drift.
- The tracker row points to the source brief and story path with status `ready-to-dev`.
- No unresolved drafting issue remains.

## Propagation

- no-propagation: the correction is local to the CS-311 story contract and review evidence.

## Residual Risk

- Implementation must still create the declared evidence artifacts and run the frontend validations before final delivery.
