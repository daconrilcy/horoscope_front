---
name: condamad-ux-ui-lead
description: >
  Coordinate a CONDAMAD UX/UI expert review or from-scratch page design plan
  for React applications. Use when the user asks to audit an existing page,
  analyze UX/UI, improve visual hierarchy, colors, typography, layout, cards,
  borders, CTAs, hero sections, user journeys, React TS/TSX structure, CSS/SCSS
  implementation, or produce a precise implementation plan before coding.
---

<!-- Skill CONDAMAD pour audit et conception UX/UI coordonnes par un lead. -->

# CONDAMAD UX/UI Lead

Coordinate four analysis roles to produce a concrete, reviewed UX/UI
implementation plan: a lead, a UX/UI expert, a senior React expert, and a
CSS/SCSS expert. Use the skill either to design a page from a brief or to audit
an existing page and propose improvements. Do not modify application code by
default; produce the plan first unless the user explicitly asks for
implementation.

## Non-Negotiable Inputs

Read applicable repository instructions before analysis. If
`_condamad/stories/regression-guardrails.md` exists, read it and identify
applicable guardrails before proposing changes. Treat guardrails as constraints,
not suggestions.

When the request targets an existing page, inspect:

- the route/page component and its child components;
- the related `ts`, `tsx`, `css`, `scss`, and test files;
- shared design tokens, variables, primitives, layout helpers, and existing
  visual conventions;
- screenshots or browser-rendered evidence when available or necessary.

When the request starts from a brief, inspect the current design system and
neighboring pages before inventing new primitives. Mark missing product
decisions explicitly instead of filling them with assumptions that would affect
positioning, conversion goals, legal copy, or paid flows.

When the user asks for market-level inspiration or when the page category is
trend-sensitive, check recent design references or current market patterns
before proposing the plan. Use trends as inspiration only: adapt them to the
product, audience, accessibility, performance, existing design system, and
regression guardrails instead of copying fashionable effects.

## Role Model

Use these roles as explicit analysis lenses. Delegate to subagents only when
the runtime instructions allow it and the user explicitly asked for parallel
agent work; otherwise perform the roles sequentially in the main agent.

## Responsibility Boundaries

Keep responsibilities separated before consolidation. Each role must produce
findings in its own lane, then the lead merges them into one plan.

- UX/UI owns user intent, page structure, hierarchy, content clarity, trust,
  interaction design, accessibility goals, market inspiration, and the
  user-visible outcome. It may name visual direction and required states, but
  must not prescribe low-level selector architecture.
- Senior React owns component boundaries, data flow, state, hooks, routing,
  semantics in JSX, accessibility implementation feasibility, API integration,
  test strategy, and TS/TSX refactor risk. It must not invent visual tokens or
  override CSS ownership.
- CSS/SCSS owns style architecture, token reuse, selectors, responsive rules,
  themes, specificity, layout mechanics, states, motion, and visual consistency
  implementation. It must not change product messaging or component
  responsibilities unless required by CSS ownership.
- Lead owns scope, tradeoffs, conflict resolution, prioritization,
  non-regression constraints, and final plan quality. It decides how to combine
  UX value, React feasibility, and CSS ownership into implementation steps.

When subagents are allowed and explicitly requested, assign one bounded prompt
per expert with a disjoint responsibility. Ask each expert for findings,
affected surfaces, risks, and validation evidence only in its lane. Do not let
subagents edit files for audit/planning tasks unless the user explicitly asks
for implementation.

### Lead UX/UI

Coordinate scope, evidence, conflicts, and final plan quality.

- Define the page goal, primary user intent, secondary intents, and conversion
  or task-success criteria.
- Identify constraints from guardrails, existing architecture, design tokens,
  accessibility, responsive behavior, and implementation cost.
- Merge the three expert analyses into one coherent plan.
- Challenge recommendations that are vague, decorative, duplicative, risky, or
  inconsistent with the product.
- Review the final plan before presenting it and remove unresolved issues,
  vague tasks, duplicated work, and contradictions between experts.

### Expert UX/UI

Audit or design the experience end to end.

- Page organization: information architecture, section order, density, rhythm,
  scanning path, hierarchy, and progressive disclosure.
- Visual system: color palette, contrast, semantic use of color, typography,
  spacing, border radius, elevation, cards, dividers, icons, imagery, and
  empty/loading/error states.
- Interaction: CTA hierarchy, button labels, affordances, forms, navigation,
  feedback, focus states, mobile gestures, and accessibility.
- Hero sections: first-viewport signal, headline clarity, proof or value
  support, primary action, secondary action, and next-section visibility.
- User journey: entry context, decision points, friction, trust signals,
  cognitive load, and completion path.
- Market fit: recent design trends, category benchmarks, expected interaction
  patterns, and visual conventions that improve clarity or perceived quality.
- Content and trust: microcopy, labels, proof points, reassurance, pricing or
  commitment clarity, error wording, and credibility signals.
- User context: likely device, expertise level, emotional state, urgency,
  arrival intent, and continuity with previous or next pages.

### Senior React Expert

Audit implementation feasibility and TS/TSX structure.

- Component boundaries, props, state ownership, hooks, side effects, API calls,
  routing, conditional rendering, error handling, and testability.
- Existing reusable components and primitives to reuse before creating new
  code.
- Risks from duplication, oversized components, mixed concerns, unstable keys,
  weak typing, hidden business logic in UI, and inaccessible markup.
- Concrete TS/TSX changes required for each UX recommendation.

### CSS/SCSS Expert

Audit style ownership and visual implementation details.

- Existing CSS variables, design tokens, theme variables, mixins, primitives,
  breakpoints, and ownership boundaries.
- Inline styles, hardcoded visual values, duplicate selectors, fallback drift,
  specificity issues, theme inconsistencies, and responsive defects.
- Borders, shadows, radii, spacing scales, typography scales, layout grids,
  focus rings, hover/active states, dark/light mode behavior, and reduced motion.
- Concrete CSS/SCSS changes required for each UX recommendation.

## Workflow

1. Clarify the mode:
   - **Creation from brief**: produce a build plan for a new page.
   - **Audit existing page**: inspect current code and rendered behavior, then
     propose improvements.
2. Gather evidence:
   - read guardrails if present;
   - locate the page, components, styles, tokens, tests, and related stories;
   - capture screenshots or browser observations when useful.
3. Build the expert findings:
   - UX/UI findings with user impact and visual rationale;
   - React findings with file-level implementation implications;
   - CSS/SCSS findings with token/style ownership implications.
4. Reconcile responsibilities:
   - keep design recommendations separate from React refactors and CSS/SCSS
     ownership until the lead consolidation;
   - resolve conflicts explicitly, such as a desired visual effect that would
     violate tokens, accessibility, performance, or guardrails;
   - discard recommendations that only make sense in one lane but create
     avoidable debt in another.
5. Convert findings into a precise implementation plan:
   - group changes by user-visible outcome, not by personal preference;
   - include target files or likely file areas;
   - include validation evidence for each meaningful change.
6. Review and correct the plan:
   - remove duplicate tasks;
   - resolve contradictions between experts;
   - ensure every recommendation is actionable and testable;
   - ensure guardrails are respected;
   - ensure no item is left as an unresolved issue or open question unless the
     user must make a product decision;
   - ensure each task names a user-visible outcome, target file area, style
     ownership, React implication, and validation evidence.
7. Present the result:
   - concise diagnosis;
   - prioritized implementation plan;
   - validation plan;
   - risks, limits, and required decisions if any.

## Audit Checklist

Use this checklist when auditing an existing page:

- Purpose: the page goal is clear within the first viewport.
- User context: the design matches the user's likely intent, device, expertise,
  emotional state, and urgency.
- Hierarchy: primary, secondary, and tertiary content are visually distinct.
- Flow: sections follow the user's likely decision path.
- CTA: primary action is obvious, specific, and not competing with equal-weight
  actions.
- Hero: the page announces the product, offer, or task directly and leaves a
  hint of continuation content.
- Cards: cards represent repeated or framed content only; avoid cards nested in
  cards or page sections disguised as cards.
- Borders and elevation: visual separation uses consistent tokens and does not
  create noise.
- Colors: palette supports hierarchy, state, accessibility, and light/dark mode
  without becoming one-note.
- Typography: sizes, weights, line heights, and text lengths match the surface.
- Content: microcopy, labels, helper text, empty states, and error messages are
  clear, specific, reassuring, and not overpromising.
- Trust: proof points, transparency, commitment, privacy, pricing, or safety
  signals are visible where the user needs confidence.
- Responsive: mobile and desktop layouts preserve order, readability, touch
  targets, and spacing.
- Accessibility: semantic HTML, labels, focus, contrast, keyboard flow, and
  reduced-motion behavior are covered.
- Complete states: loading, skeleton, empty, error, success, disabled, and
  timeout/offline states are designed when relevant.
- Perceived performance: layout shifts, image weight, animation cost, lazy
  loading, and time-to-understand are considered.
- Cross-page coherence: navigation, visual patterns, terminology, and journey
  continuity match neighboring pages and funnels.
- Content variability: long text, translations, dates, currencies, user names,
  and dynamic data cannot break the layout.
- Measurement: analytics or qualitative signals are identified when needed to
  validate whether the UX improvement worked after delivery.
- React: component structure, state, API boundaries, and tests support the
  proposed UX.
- CSS/SCSS: no new inline styles, no avoidable hardcoded values, and token
  reuse is explicit.

## Evidence Discipline

Do not infer visual quality from code alone when rendered evidence is available
or easy to obtain. Prefer screenshots, browser inspection, existing visual
artifacts, and local component/page evidence. When evidence is unavailable,
label the recommendation as a hypothesis and include the validation step needed
to confirm it.

For existing pages, cite repository-relative files or obvious page surfaces for
each major recommendation. For new pages, cite the existing design-system
primitives, tokens, neighboring routes, or patterns that should anchor the
implementation.

## Output Contract

Return a plan in this shape unless the user requested another format:

```md
## Diagnostic

- <3-7 high-signal observations grounded in evidence>

## Contraintes et garde-fous

- Guardrails lus: <yes/no + path>
- Guardrails applicables: <IDs or "aucun applicable">
- Contraintes design/code: <tokens, ownership, architecture, responsive, etc.>

## Plan de mise en oeuvre

1. <Outcome-oriented task>
   - Fichiers cibles: `<path>`, `<path>`
   - Design UX/UI: <user-visible change and rationale>
   - React TS/TSX: <component, state, hook, route, semantic, or test impact>
   - CSS/SCSS: <token, selector, layout, responsive, theme, or state impact>
   - Validation: <test, lint, screenshot, manual flow, contrast check>
   - Mesure: <analytics, usability signal, or "non necessaire">

## Revue du plan

- Separation des responsabilites: <design/react/css boundaries respected>
- Duplications supprimees: <summary>
- Contradictions resolues: <summary>
- Elements non actionnables retires: <summary>
- Priorisation impact/effort: <quick wins, structural work, design debt>
- Risques restants: <none or explicit user decision>
```

Do not present generic advice such as "improve spacing" without naming the
surface, the likely token or CSS owner, and the expected user-visible result.
