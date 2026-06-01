# Output Contract

Use this contract for frontend UX/UI audits unless the user asks for another
format.

## Executive Summary

Start with:

- **Verdict**: Ready / Ready with reservations / Not ready.
- **Risk level**: Low / Medium / High.
- **Counts**: P0, P1, P2.
- **Primary risk**: one sentence.
- **Top corrections**: 3 items maximum.
- **Assumptions**: only if context was incomplete.

## Score

For full audits and launch readiness, include:

| Criterion | Score | Rationale |
| --- | ---: | --- |
| Clarity | /5 |  |
| Utility | /5 |  |
| Hierarchy | /5 |  |
| Accessibility | /5 |  |
| Performance UX | /5 |  |
| Coherence | /5 |  |
| Trust | /5 |  |
| Control | /5 |  |
| Content | /5 |  |
| Measurement | /5 |  |

For quick audits, scoring is optional.

## Prioritized Findings

Format each finding as:

```md
### [P0/P1/P2] <Problem title>

**Rule family:** <product / IA / visual UI / accessibility / forms /
performance / responsive / trust / AI / ethics / design system / content /
handoff / QA / measurement>
**Observation:** <what is visible, inspected, or inferred>
**Impact:** <concrete user or business consequence>
**Correction:** <specific fix>
**Acceptance criteria:** <verifiable done condition>
**QA:** <manual or automated validation>
**Surface:** <component, section, route, step, screenshot area, or "to locate">
```

Findings must be ordered by severity and user risk, not by page order.

## Correction Plan

Use phases:

```md
## Phase 1 - P0 Blockers

1. <Correction>
   - Surface/files: `<path>` or <area>
   - Owner: Design / Frontend / Product / QA / Analytics
   - Acceptance: <done condition>
   - Validation: <test/check/screenshot/flow>

## Phase 2 - P1 Major Fixes

1. <Correction>
   - Surface/files:
   - Owner:
   - Acceptance:
   - Validation:

## Phase 3 - P2 Optimizations

1. <Correction>
   - Benefit:
   - Acceptance:
```

If no code was inspected, use "Surface/files: to locate in implementation".
Do not invent file paths.

## Global Acceptance Checklist

Include the relevant items:

- Page objective is clear.
- Primary CTA is visible and explicit.
- Critical journey works with keyboard.
- Focus is visible.
- Critical contrasts are compliant.
- Mobile can complete the task.
- Errors explain how to fix the issue.
- Loading, empty, error, and success states exist where needed.
- Sensitive actions require confirmation.
- Costs, commitments, data usage, and consequences are transparent.
- User-entered data is not lost.
- Edge cases are tested.
- Success measurement is defined.

## Implementation Guidance

If repository context exists, include:

- target components or likely files;
- states to add;
- tokens/styles to adjust;
- tests to write or update;
- analytics events to add;
- product/design decisions still needed.

If repository context does not exist, keep guidance at the design/spec/QA
level.

## Final Review

End with:

- **Ready after fixes:** <yes/no/conditional>
- **Remaining decisions:** <none or list>
- **Validation needed:** <browser, accessibility, mobile, analytics, user test>

Do not end with open-ended generic offers. Keep the output actionable.
