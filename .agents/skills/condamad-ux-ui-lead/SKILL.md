---
name: condamad-ux-ui-lead
description: >
  Coordinate a CONDAMAD UX/UI expert review or from-scratch page design plan
  for React applications when the request requires cross-cutting judgment across
  page structure, visual hierarchy, interaction design, React implementation,
  and styling ownership.
---

<!-- Skill CONDAMAD pour audit et conception UX/UI coordonnes par un lead. -->

# CONDAMAD UX/UI Lead

Coordinate four analysis roles to produce a concrete, reviewed UX/UI
implementation plan: a lead, a UX/UI expert, a senior React expert, and a
Styling expert. Use the skill either to design a page from a brief or to audit
an existing page and propose improvements. Do not modify application code by
default; produce the plan first unless the user explicitly asks for
implementation.

## Scope Control

Use this skill only when the request requires UX/UI judgment across page
structure, visual hierarchy, interaction design, React implementation, and
styling ownership.

Do not use this skill for:

- isolated CSS fixes with an obvious local cause;
- small visual tweaks, icon swaps, copy-only edits, or one-token changes;
- simple component implementation requests where the user already gave the
  design;
- pure bug fixes unrelated to UX/UI hierarchy or page experience;
- generic React explanations;
- implementation-only tasks where a plan was already approved.

For small UI requests, provide the smallest useful answer. Use the full
CONDAMAD UX/UI workflow only when the request requires cross-cutting UX, React,
and styling judgment.

## Planning Boundary

For audit requests, stop at recommendations unless the user asks for an
implementation plan.

When Design Upgrade Mode is active, produce the design ambition, redesign
paths, and concrete implementation plan even if the original wording is framed
as an audit. The plan is part of the upgrade diagnosis; it is not permission to
edit application code.

For implementation-plan requests, translate recommendations into ordered tasks,
target files, ownership, and validation.

For coding requests, only implement after the user explicitly asks for code
changes.

## Design Upgrade Mode

When the user asks to "go further", "upgrade quality", "make the page more
premium", "improve the design deeply", "avoid small tweaks", "raise the UX/UI
level", or when the current page looks generic, weak, flat, visually
inconsistent, or below product quality expectations, activate Design Upgrade
Mode.

In Design Upgrade Mode, do not limit the answer to local corrections. The goal
is to propose a meaningful qualitative leap in page perception, clarity,
hierarchy, and craft.

The agent must produce:

1. A diagnosis of why the page currently feels limited, generic, confusing,
   flat, immature, noisy, or not premium enough.
2. A target design ambition, expressed as a clear creative direction.
3. At least two redesign paths:
   - Conservative upgrade: preserves most of the current structure but improves
     hierarchy, rhythm, visual system, and interaction clarity.
   - Ambitious upgrade: rethinks page composition, section order, visual
     hierarchy, component treatment, and perceived product quality.
4. A recommendation between the redesign paths, with rationale.
5. A concrete implementation plan that translates the selected direction into
   React, styling, responsive, accessibility, and validation tasks.

Design Upgrade Mode is not decorative mode. Every visual proposal must improve
at least one of:

- comprehension;
- trust;
- conversion or task completion;
- perceived quality;
- hierarchy;
- emotional fit;
- accessibility;
- interaction clarity;
- cross-page coherence.

Do not answer only with small retouches such as "increase spacing", "adjust
border radius", "improve contrast", or "make cards cleaner" unless the page is
already at a high design quality level. If only small changes are proposed,
explicitly justify why a deeper redesign would create more risk than value.

## Non-Negotiable Inputs

Read applicable repository instructions before analysis. If
`_condamad/stories/regression-guardrails.md` exists, read it and identify
applicable guardrails before proposing changes. Treat guardrails as constraints,
not suggestions.

When the request targets an existing page, inspect directly relevant evidence
first:

1. repository instructions and guardrails;
2. the route/page entrypoint;
3. directly imported child components;
4. directly imported style files, tokens, primitives, layout helpers, and
   existing visual conventions;
5. one or two neighboring pages using the same visual system;
6. tests only when behavior, state, accessibility, or regression risk is
   affected;
7. screenshots or browser-rendered evidence when available or necessary.

Do not expand recursively beyond directly related files unless a concrete risk
is discovered. If evidence remains incomplete, label the recommendation as a
hypothesis and name the missing evidence or validation step.

When the request starts from a brief, inspect the current design system and
neighboring pages before inventing new primitives. Mark missing product
decisions explicitly instead of filling them with assumptions that would affect
positioning, conversion goals, legal copy, or paid flows.

Use market inspiration only when the user explicitly asks for inspiration,
benchmarking, or trend alignment; when the page is brand-sensitive,
conversion-sensitive, or visually underdefined; or when current category
conventions materially affect user trust or comprehension. Never copy a
competitor layout, brand asset, illustration, animation, or wording. Summarize
patterns abstractly and adapt them to the existing design system, accessibility,
performance, and regression guardrails. If current references cannot be checked
with available tools, label market observations as non-current design
heuristics, not as recent trends.

## Role Model

Use these roles as explicit analysis lenses. Delegate to subagents only when
the runtime instructions allow it and the user explicitly asked for parallel
agent work; otherwise perform the roles sequentially in the main agent.

Do not present role-by-role transcripts by default. Use the roles as internal
lenses and present a consolidated plan unless the user explicitly asks for
separate expert findings or role-specific findings materially affect the final
recommendation.

## Responsibility Boundaries

Keep responsibilities separated before consolidation. Each role must be
considered as a separate analysis lane before the lead merges them into one
plan. Expose only the consolidated result unless separate expert findings are
useful.

- UX/UI owns user intent, page structure, hierarchy, content clarity, trust,
  interaction design, accessibility goals, market inspiration, and the
  user-visible outcome. It may name visual direction and required states, but
  must not prescribe low-level selector architecture.
- Senior React owns component boundaries, data flow, state, hooks, routing,
  semantics in JSX, accessibility implementation feasibility, API integration,
  test strategy, and TS/TSX refactor risk. It must not invent visual tokens or
  override styling ownership.
- Styling owns style architecture across CSS, SCSS, Tailwind, shadcn/ui, CSS
  variables, design tokens, component-level class composition, responsive
  rules, themes, specificity, layout mechanics, states, motion, and visual
  consistency implementation. It must not change product messaging or component
  responsibilities unless required by styling ownership.
- Lead owns scope, tradeoffs, conflict resolution, prioritization,
  non-regression constraints, and final plan quality. It decides how to combine
  UX value, React feasibility, and styling ownership into implementation steps.

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
- Marketing, landing, and onboarding sections: first-viewport signal, headline
  clarity, proof or value support, primary action, secondary action, and
  next-section visibility.
- User journey: entry context, decision points, friction, trust signals,
  cognitive load, and completion path.
- Market fit: current references only when checked with available tools;
  otherwise use category heuristics, expected interaction patterns, and visual
  conventions that improve clarity or perceived quality.
- Content and trust: microcopy, labels, proof points, reassurance, pricing or
  commitment clarity, error wording, and credibility signals.
- User context: likely device, expertise level, emotional state, urgency,
  arrival intent, and continuity with previous or next pages.

### Design Craft and Creative Direction

In Design Upgrade Mode, the UX/UI expert must define a visual and experiential
direction before listing recommendations.

The direction must include:

- Design ambition: what the page should feel like after redesign.
- Perception target: premium, calm, expert, playful, editorial, operational,
  immersive, trustworthy, high-conversion, etc.
- Hierarchy strategy: what the user must see first, second, third.
- Composition strategy: page grid, section rhythm, density, whitespace, visual
  anchors, and focal points.
- Typography strategy: title scale, body rhythm, label treatment, metadata
  style, readability constraints.
- Color and material strategy: semantic color usage, background depth,
  contrast, surfaces, borders, shadows, gradients, glass, glow, or flat
  treatment when useful.
- Interaction strategy: hover, focus, active, selected, disabled, loading,
  transition, and motion principles.
- Trust and quality signals: what elements make the page feel credible,
  finished, intentional, and product-grade.
- Removal strategy: what visual or structural elements should be removed
  because they create noise, cheapness, confusion, or duplication.

The UX/UI expert must distinguish:

- polish improvements;
- structural UX improvements;
- visual identity improvements;
- interaction improvements;
- content/trust improvements.

### Senior React Expert

Audit implementation feasibility and TS/TSX structure.

- Component boundaries, props, state ownership, hooks, side effects, API calls,
  routing, conditional rendering, error handling, and testability.
- Existing reusable components and primitives to reuse before creating new
  code.
- Risks from duplication, oversized components, mixed concerns, unstable keys,
  weak typing, hidden business logic in UI, and inaccessible markup.
- Concrete TS/TSX changes required for each UX recommendation.

### Styling Expert

Audit style ownership and visual implementation details across CSS, SCSS,
Tailwind, shadcn/ui, CSS variables, design tokens, and component-level class
composition.

- Existing CSS variables, design tokens, theme variables, mixins, primitives,
  breakpoints, and ownership boundaries.
- Inline styles, hardcoded visual values, duplicate selectors, fallback drift,
  specificity issues, theme inconsistencies, and responsive defects.
- Tailwind class duplication, arbitrary values, inconsistent spacing utilities,
  variant drift, and misuse of shadcn primitives.
- Borders, shadows, radii, spacing scales, typography scales, layout grids,
  focus rings, hover/active states, dark/light mode behavior, and reduced motion.
- Concrete styling changes required for each UX recommendation.

## Workflow

1. Infer the mode whenever possible:
   - **Audit existing page**: screenshot, route, existing component, or current
     UI problem.
   - **Creation from brief**: product or page brief without existing
     implementation.
   - **Implementation mode**: approved plan plus explicit coding request.
   Ask a clarification question only if the ambiguity would materially change
   the recommendation or implementation plan.
2. Classify the page type before applying the checklist:
   - marketing / landing page;
   - authentication page;
   - dashboard;
   - data table / list view;
   - form / wizard;
   - editor / canvas / node-based interface;
   - settings / admin page;
   - upload / processing workflow;
   - other operational surface.
   Apply only the criteria relevant to that page type. Do not force hero, CTA,
   proof, or conversion analysis onto operational product screens. For
   operational screens, prioritize task success, readability, state feedback,
   error recovery, density, and control clarity.
3. Gather evidence:
   - read guardrails if present;
   - locate the page, components, styles, tokens, tests, and related stories;
   - capture screenshots or browser observations when useful.
4. Build the expert findings:
   - UX/UI findings with user impact and visual rationale;
   - React findings with file-level implementation implications;
   - styling findings with token/style ownership implications.
5. Reconcile responsibilities:
   - keep design recommendations separate from React refactors and styling
     ownership until the lead consolidation;
   - resolve conflicts explicitly, such as a desired visual effect that would
     violate tokens, accessibility, performance, or guardrails;
   - discard recommendations that only make sense in one lane but create
     avoidable debt in another.
6. Convert findings into a precise implementation plan when the request asks
   for planning or handoff:
   - group changes by user-visible outcome, not by personal preference;
   - include target files or likely file areas;
   - include validation evidence for each meaningful change.
7. Review and correct the plan:
   - remove duplicate tasks;
   - resolve contradictions between experts;
   - ensure every recommendation is actionable and testable;
   - ensure guardrails are respected;
   - ensure no item is left as an unresolved issue or open question unless the
     user must make a product decision;
   - ensure each task includes the relevant implementation dimensions. Do not
     invent React, styling, measurement, or analytics work when the change does
     not require it. If a dimension is not applicable, write
     "N/A - no change required" with a short reason.
8. Present the result:
   - concise diagnosis;
   - prioritized implementation plan;
   - validation plan;
   - risks, limits, and required decisions if any.

## Transformation Levels

For every significant audit, classify each recommendation by transformation
level.

### Level 1 - Polish

Small refinements that improve finish without changing the page structure:
spacing, contrast, alignment, icon sizing, border consistency, hover states,
minor typography corrections.

### Level 2 - UX/UI Restructure

Meaningful changes to hierarchy, grouping, section order, CTA priority, card
logic, layout rhythm, content density, responsive behavior, and user decision
path.

### Level 3 - Design Upgrade

A stronger redesign direction that changes the perceived quality of the page:
new composition, clearer visual narrative, stronger first viewport, improved
visual identity, better emotional fit, stronger trust signals, refined component
system, richer states, and more intentional motion or depth.

In Design Upgrade Mode, the final plan must include at least:

- 3 Level 2 recommendations;
- 2 Level 3 recommendations;
- 1 explicit "what not to keep" section;
- 1 final recommended redesign path.

If the agent cannot identify Level 2 or Level 3 changes, it must explain why
the current page is already structurally strong and provide evidence.

## Anti-Overdesign Rules

Do not propose visual decoration unless it improves hierarchy, comprehension,
trust, accessibility, or task success.

Reject:

- decorative gradients without hierarchy purpose;
- excessive shadows, glows, borders, or nested cards;
- animations that do not clarify state or transition;
- new design primitives when existing primitives can be reused;
- layout changes that increase cognitive load;
- visual novelty that conflicts with the product's existing tone.

Prefer targeted improvements over redesigns unless the current page structure
is fundamentally broken.

## Audit Checklist

Use this checklist when auditing an existing page:

- Purpose: the page goal is clear within the first viewport.
- User context: the design matches the user's likely intent, device, expertise,
  emotional state, and urgency.
- Hierarchy: primary, secondary, and tertiary content are visually distinct.
- Flow: sections follow the user's likely decision path.
- CTA: for marketing, onboarding, and action-led screens, the primary action is
  obvious, specific, and not competing with equal-weight actions.
- Hero: for marketing, landing, or onboarding pages, the page announces the
  product, offer, or task directly and leaves a hint of continuation content.
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
- Styling: no new inline styles, no avoidable hardcoded values, and token reuse
  is explicit across CSS, SCSS, Tailwind, shadcn/ui, and CSS variables.

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

## Output Depth

Default to the smallest output depth that satisfies the request.

Design Upgrade Mode overrides the default shallow output depth. When it is
active, use the Design Upgrade Output Contract and keep the answer deep enough
to describe the target page, the redesign alternatives, and the implementation
path.

Use one of these output depths:

### Quick Review

For screenshot-only or narrowly scoped visual feedback:

- Diagnostic
- Corrections prioritaires
- Validation visuelle

### Full Audit

For existing pages with code and rendered evidence:

- Diagnostic
- Contraintes et garde-fous
- Plan de mise en oeuvre
- Validation plan
- Revue du plan

### Build Plan

For from-scratch page creation:

- Page goal
- UX structure
- Component plan
- Styling plan
- States
- Validation

### Implementation Plan

For approved recommendations that need coding guidance or handoff:

- Ordered tasks
- Target files or file areas
- Relevant React, styling, state, accessibility, and test implications
- Validation

## Output Contract

Return a plan in this shape for Full Audit or Implementation Plan unless the
user requested another format:

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
   - React TS/TSX: <component, state, hook, route, semantic, test impact, or "N/A - no change required">
   - Styling: <token, selector, Tailwind utility, shadcn primitive, layout, responsive, theme, state impact, or "N/A - no change required">
   - Validation: <test, lint, screenshot, manual flow, contrast check>
   - Mesure: <only when the change affects conversion, activation, retention, or task completion>

## Revue du plan

- Separation des responsabilites: <design/react/styling boundaries respected>
- Duplications supprimees: <summary>
- Contradictions resolues: <summary>
- Elements non actionnables retires: <summary>
- Priorisation impact/effort: <quick wins, structural work, design debt>
- Risques restants: <none or explicit user decision>
```

Do not present generic advice such as "improve spacing" without naming the
surface, the likely token or styling owner, and the expected user-visible
result.

## Design Upgrade Invocation Prompt

When asking another expert, subagent, or follow-up workflow to analyze a page in
Design Upgrade Mode, use this intent:

```md
Analyse cette page en Design Upgrade Mode.

Je ne veux pas un audit de petites retouches. Je veux une analyse profonde
UX/UI/design qui explique pourquoi la page ne parait pas encore au niveau
attendu, puis qui propose une vraie montee en qualite.

Contraintes :
- Ne te limite pas a spacing / couleurs / borders / CTA.
- Propose au moins deux scenarios : conservative upgrade et ambitious upgrade.
- Donne une ambition design cible claire.
- Identifie ce qu'il faut garder, supprimer, restructurer ou rendre plus premium.
- Classe les recommandations en Level 1 Polish, Level 2 UX/UI Restructure,
  Level 3 Design Upgrade.
- Termine par un plan d'implementation actionnable pour React + styling +
  responsive + accessibilite.
- Chaque tache doit avoir un critere d'acceptation verifiable visuellement.
```

## Design Upgrade Output Contract

When Design Upgrade Mode is active, return the result in this shape:

```md
## Diagnostic qualite

- <3-7 observations explaining why the current page does not yet feel strong,
  premium, clear, coherent, conversion-ready, or product-grade>

## Ambition design cible

- Perception recherchee: <premium / expert / immersive / operational / playful / etc.>
- Promesse visuelle: <what the page should communicate in 3 seconds>
- Niveau de transformation recommande: <Level 1 / Level 2 / Level 3>
- Ce qu'il faut preserver: <existing strengths>
- Ce qu'il faut abandonner: <visual or UX patterns that lower quality>

## Scenarios de redesign

### Option A - Conservative upgrade

- Structure: <what changes>
- Hierarchie: <what becomes dominant / secondary / muted>
- UI system: <cards, surfaces, spacing, typography, colors, states>
- Impact attendu: <clarity / trust / conversion / task success>
- Risque: <implementation or regression risk>

### Option B - Ambitious upgrade

- Structure: <what changes more deeply>
- Hierarchie: <new scanning path>
- UI system: <new composition / stronger visual language>
- Impact attendu: <quality leap>
- Risque: <implementation or regression risk>

## Recommandation lead

- Option recommandee: <A / B / hybrid>
- Pourquoi: <impact / effort / coherence / regression risk>
- Niveau d'ambition retenu: <Level 2 or Level 3>

## Plan de mise en oeuvre

1. <Outcome-oriented transformation task>
   - Niveau: <Level 1 / 2 / 3>
   - Fichiers cibles: `<path>`, `<path>`
   - Design UX/UI: <visible change and design rationale>
   - React TS/TSX: <component/state/props/semantics/accessibility/test impact>
   - Styling: <tokens/classes/layout/responsive/theme/motion/state impact>
   - Validation visuelle: <before/after screenshot, viewport, checklist>
   - Validation technique: <lint/test/build/accessibility>
   - Critere d'acceptation: <observable result>

## Criteres de qualite apres refonte

- First viewport: <expected result>
- Visual hierarchy: <expected result>
- Interaction clarity: <expected result>
- Responsive: <expected result>
- Accessibility: <expected result>
- Perceived quality: <expected result>

## Anti-regression visuelle

- <what must not be degraded>
- <screenshots/viewports to compare>
- <states to verify>
```

## Anti-Shallow Audit Rules

Reject shallow reports.

A report is considered shallow if it:

- only lists local UI fixes;
- does not define a target design ambition;
- does not explain why the current page feels weaker than expected;
- does not propose an alternative composition or hierarchy;
- does not separate polish from structural redesign;
- does not include acceptance criteria visible in screenshots;
- does not say what should be removed, simplified, merged, or visually
  deprioritized;
- does not give enough implementation detail for a developer to produce a
  visible quality upgrade.

When the report is shallow, revise it before answering.
