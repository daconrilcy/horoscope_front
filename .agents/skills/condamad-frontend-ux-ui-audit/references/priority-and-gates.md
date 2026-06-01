# Priority and Launch Gates

## Severity Levels

### P0 - Blocking

The issue must be fixed before production. Use P0 when the interface is not
ready because it blocks or seriously risks blocking usability, accessibility,
trust, safety, legal/commercial transparency, or critical measurement.

Examples:

- critical journey cannot be completed;
- mobile prevents the task;
- keyboard cannot complete the flow;
- focus is invisible;
- contrast blocks reading of important content;
- form data can be lost;
- error gives no repair path;
- sensitive action lacks confirmation;
- hidden costs, commitment, or cancellation constraints;
- consent refusal is harder than acceptance;
- AI takes important action without human validation;
- loading, network, or server failure leaves the user stuck;
- critical journey has no success metric or tracking plan.

### P1 - Major

The issue should be fixed before launch or soon after launch. Use P1 when it
strongly affects comprehension, conversion, confidence, perceived quality,
consistency, or maintainability but does not fully block the experience.

Examples:

- weak hierarchy or competing CTAs;
- jargon-heavy labels;
- missing empty state guidance;
- incomplete component states;
- excessive form effort;
- poor mobile ergonomics that remains technically usable;
- hardcoded visual values causing design-system drift;
- AI recommendation not sufficiently explained;
- personalization not clearly controllable.

### P2 - Optimization

The issue improves polish, consistency, perception, or efficiency but does not
block launch.

Examples:

- subtle spacing inconsistency;
- minor typography rhythm issue;
- non-critical microcopy improvement;
- visual refinement that improves perceived quality;
- optional analytics enrichment after core metrics exist.

## Launch Gate Decision

Use this verdict model:

- **Ready**: no P0, limited P1, acceptable residual risk.
- **Ready with reservations**: no P0, several P1 requiring scheduled fixes.
- **Not ready**: one or more P0, or many P1 on a critical journey.

Do not mark a page ready when any non-negotiable P0 remains.

## Scoring Gate

Score each full audit from 1 to 5:

| Criterion | Minimum |
| --- | ---: |
| Clarity | 4 |
| Utility | 4 |
| Hierarchy | 4 |
| Accessibility | 5 |
| Performance UX | 4 |
| Coherence | 4 |
| Trust | 5 |
| Control | 4 |
| Content | 4 |
| Measurement | 4 |

If clarity, hierarchy, accessibility, trust, or control is below 4, require
correction before readiness. If accessibility, trust, or control is below 3 on
a critical path, classify at least one P0.
