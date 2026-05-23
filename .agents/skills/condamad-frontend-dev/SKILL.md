---
name: condamad-frontend-dev
version: 1
description: >
  Implement, fix, refactor, or review-to-fix frontend work with CONDAMAD
  discipline for Vite + React + strict TypeScript applications. Use when the
  user asks for frontend development, UI features, React components, pages,
  feature modules, forms, API hooks, TanStack Query integration, Tailwind or
  shadcn/ui work, Zustand state, Vitest component tests, or Playwright E2E
  changes. Optimized for pnpm projects using Tailwind CSS, shadcn/ui,
  lucide-react, react-hook-form, zod, TanStack Query, Vitest, Testing Library,
  and Playwright.
---

<!-- Skill CONDAMAD dedie au developpement frontend React strict. -->

# CONDAMAD Frontend Dev

This skill applies CONDAMAD development discipline to frontend work. It turns a
frontend request into a scoped implementation with repository inspection,
small patches, tests, validation evidence, and explicit architectural
guardrails.

## Required references

Load these references before editing frontend files:

- `../condamad-dev-story/references/condamad-principles.md`
- `references/frontend-architecture.md`
- `references/frontend-implementation-contract.md`
- `references/frontend-validation-contract.md`

Also apply `../condamad-regression-guardrails/SKILL.md` for every frontend
task, even when the task is not attached to a CONDAMAD story capsule. Read
repository `AGENTS.md` files that apply to touched paths. If a CONDAMAD story
capsule is involved, also apply `../condamad-dev-story/SKILL.md`.

## Stack contract

Use this stack unless the existing repository has a stricter compatible
configuration:

- Framework: Vite + React
- Language: TypeScript strict
- Styling: Tailwind CSS
- Base UI: shadcn/ui
- Icons: lucide-react
- Forms: react-hook-form + zod
- Server state: TanStack Query
- Local global state: Zustand only when strict eligibility rules are met
- Unit/component tests: Vitest + Testing Library
- E2E: Playwright
- Lint/format: ESLint + Prettier
- Package manager: pnpm

Do not introduce another framework, state manager, UI system, form library, or
package manager without explicit user approval.

## Canonical structure

Prefer this frontend structure and adapt to the existing repository only when
it already has a clear equivalent:

```text
src/
  app/
    App.tsx
    router.tsx
    providers.tsx
  features/
    <feature>/
      api/
      components/
      hooks/
      schemas/
      types.ts
  components/
    ui/
    layout/
    common/
  lib/
    api/
      http-client.ts
      query-client.ts
    utils/
      cn.ts
      date.ts
  hooks/
  stores/
  styles/
    globals.css
  types/
    global.ts
tests/
  unit/
  e2e/
```

`src/components/ui` is reserved for shadcn/ui base components. Business logic
must live in `src/features/<feature>/`, shared technical utilities in
`src/lib`, layout components in `src/components/layout`, and reusable
business-neutral components in `src/components/common`.

Use `src/app` for router, providers, and application composition. Do not create
new `src/pages` entries unless the existing repository already uses `src/pages`
as its canonical route-screen convention; if it does, extend that convention
without duplicating the same screen under both `src/pages` and `src/features`.

## Execution strategy

For each task, follow this sequence:

1. Inspect the repository:
   - identify the concerned feature;
   - search for existing implementations;
   - identify patterns, test helpers, and UI primitives to reuse.
2. Decide placement:
   - choose the correct feature folder or shared location;
   - avoid creating folders unless the repository lacks a canonical location.
3. Implement the minimal change:
   - extend existing code when responsibilities match;
   - avoid broad rewrites or parallel implementations.
4. Add or update tests:
   - cover success, loading, error, empty, and validation states when relevant.
5. Run validation:
   - targeted checks first, then lint, typecheck, tests, and E2E when required.
6. Run static guard checks:
   - direct HTTP calls, `any`, inline styles, misplaced UI/business logic,
     duplicate state, and unauthorized Zustand usage.
7. Provide evidence:
   - changed files, commands, skipped checks, risks, and local startup status.
   - Do not claim validation passed unless the command was actually run and
     completed successfully.

## Anti-duplication rule

Before creating any new file, search for an existing similar implementation.

If a similar component, hook, schema, API function, type, store, route, or test
helper exists:

- extend or reuse it;
- converge naming and imports on the canonical implementation;
- do not create a parallel version.

Duplicate logic, hooks, schemas, API functions, state stores, page routes, or
business components are forbidden unless the task explicitly justifies separate
responsibilities.

Apply SOLID, KISS, and YAGNI with the same force as DRY: keep component, hook,
API, state, and style responsibilities narrow; prefer the smallest readable
React design that satisfies the current task; do not add generic abstractions,
configuration surfaces, or future-proof variants without present evidence.

## Pattern consistency

Before implementing, search for a similar feature, route, form, query hook,
mutation, component, test, or styling pattern.

If a matching pattern exists:

- reuse the same folder shape, naming style, hook shape, query-key shape, and
  testing style;
- prefer the most recent or most used pattern when several valid patterns
  exist;
- do not introduce a third variation unless the task explicitly requires a new
  convention and the final evidence documents why.

Pattern drift is a defect. Fix avoidable drift before returning the result.

## Naming conventions

Use consistent names unless the repository already has a stronger convention.

Files:

- components: `PascalCase.tsx`
- hooks: `useSomething.ts`
- API functions/modules: verb-noun names such as `getUsers.ts`,
  `updateInvoice.ts`, or an existing feature-local equivalent
- schemas: `something.schema.ts`
- types: `something.types.ts` when a feature needs multiple type files;
  otherwise keep the canonical `types.ts`
- tests: mirror the unit under test with the repository's existing suffix

React symbols:

- components: `PascalCase`
- hooks: `useSomething`
- query hooks: `useUsersQuery`, `useUserQuery`, `useUpdateUserMutation`, or the
  existing repository equivalent
- query keys: stable structured arrays such as `["feature", "entity", params]`

Avoid generic feature-local names like `data.ts`, `utils.ts`, `helpers.ts`, or
`misc.ts` unless the repository already uses them for a narrow, clear purpose.
Avoid inconsistent singular/plural names for the same domain object.

## Import and barrel rules

Use the repository's existing import alias convention. Do not mix relative deep
imports and alias imports inconsistently in the same area.

Prefer stable imports from canonical public files when they already exist. Do
not reach into another feature's internals through deep imports.

Do not create barrel files by default. Create `index.ts` only when the
repository already uses that convention for the same layer or when it clearly
improves public feature exports. Avoid circular imports caused by barrels.

## Ownership rules

Each feature fully owns:

- its API functions and query/mutation hooks;
- its feature hooks;
- its schemas;
- its domain and payload types;
- its feature-specific components.

No feature should import another feature's internals or modify another
feature's private structure. Shared code must be extracted deliberately to
`src/components/common`, `src/lib`, or `src/hooks` when multiple features need
it.

Cross-feature dependencies are forbidden unless explicitly justified by the
task and documented in the final evidence.

## Regression guardrails registry

Every frontend task must use `_condamad/stories/regression-guardrails.md` as a
shared source of non-regression truth.

Required behavior:

1. Ensure `_condamad/stories/regression-guardrails.md` exists before frontend
   implementation. If it is missing, create it through
   `../condamad-regression-guardrails/SKILL.md`.
2. Read the registry during preflight.
3. Classify guardrails as:
   - applicable: the task touches or depends on the protected surface;
   - non-applicable: the task is outside that surface;
   - needs-investigation: the task may overlap and requires repository search.
4. Include applicable guardrails in the mini-plan and validation plan.
5. Run or document the expected guards for applicable rows.
6. Add or update a registry row when the frontend work creates a durable new
   invariant: design-system rule, route ownership rule, API-client boundary,
   feature ownership boundary, token/style constraint, E2E critical flow, or
   anti-reintroduction rule.
7. Do not remove, weaken, renumber, or generalize an existing `RG-XXX`
   invariant unless the user explicitly asks for that governance change.

For frontend work, pay special attention to existing frontend guardrails such
as design tokens, hardcoded visual values, typography roles, inline styles, CSS
fallbacks, legacy style surfaces, and design-system anti-drift guards. Use the
current registry as the source of the exact IDs and commands.

When adding a new invariant, use the registry's row format:

```md
| RG-XXX | `<source-story-or-task-key>` | <protected surface> | <durable invariant> | <deterministic guard> |
```

Only add concrete invariants with executable or objectively reviewable guards.
Avoid vague rows such as "do not break the UI".

## Workflow

### 1. Preflight

1. Locate the repository root and frontend root.
2. Run `git status --short`.
3. Read applicable `AGENTS.md` instructions.
4. Ensure and read `_condamad/stories/regression-guardrails.md`.
5. Classify applicable frontend guardrails and identify their expected guards.
6. Inspect `frontend/package.json`, `tsconfig*`, Vite config, Tailwind config,
   ESLint/Prettier config, Vitest config, and Playwright config when relevant.
7. Inspect the existing source tree before proposing files.
8. Identify matching components, hooks, schemas, API calls, stores, routes, and
   tests with `rg` before creating anything new.

### 2. Mini-plan

Before coding, provide a mini-plan of 3 to 7 steps. Include:

- files or areas likely to change;
- tests to add or update;
- applicable regression guardrails and expected evidence;
- validation commands to run;
- any dependency or architecture risk.

Do not pause for approval unless the change requires a new dependency,
destructive action, unclear product behavior, or a stack deviation.

### 3. Implement

Make the smallest coherent patch that satisfies the request.

Required implementation rules:

- Keep TypeScript strict; do not use `any` unless a nearby comment justifies it.
- Prefer `unknown` for untrusted values.
- Export explicit types for API payloads, form values, and domain models.
- Validate external data with zod.
- Route all HTTP through `src/lib/api/http-client.ts`.
- Expose feature API hooks under `src/features/<feature>/api`.
- Use TanStack Query for server state.
- Use Zustand only when state is shared across multiple pages, is not
  server-owned, and cannot be derived from URL, props, or colocated React
  state.
- Use react-hook-form with zod schemas for forms.
- Use Tailwind utility classes and `cn()` for conditional classes.
- Do not use inline styles.
- Do not modify shadcn/ui components unless the change is intentional and
  documented.
- Prefer named exports.
- Keep components small and focused; extract hooks before a component exceeds
  roughly 200 lines.
- Reuse existing patterns before adding abstractions.
- Separate data fetching, business logic, and UI rendering. Move reusable
  logic to feature hooks, feature API modules, or shared utilities.
- Handle loading, empty, error, and fallback UI states for user-facing async
  surfaces.

### 4. Test

Add or update tests for important behavior:

- component rendering and states with Vitest + Testing Library;
- hooks and API behavior with mocked clients or existing test utilities;
- form validation through zod and user interactions;
- E2E coverage with Playwright for critical user flows.

Cover loading, error, empty, success, and validation states when the feature
surface includes them.

### 5. Validate

Run the repository's frontend quality commands from the frontend root:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
```

If the project uses different script names, discover them from `package.json`
and run the closest equivalent. Do not mark the task complete when lint,
typecheck, or tests fail unless a precise blocker is documented.

Also run or document every guard command required by applicable rows in
`_condamad/stories/regression-guardrails.md`. If an applicable guard cannot be
run, classify it as `NOT_RUN` or `BLOCKED` with reason and risk.

### 6. Review and evidence

Before final response:

1. Run `git diff --stat`.
2. Inspect the relevant diff.
3. Confirm applicable regression guardrails were preserved or updated.
4. Check whether the task created a durable frontend invariant that must be
   added to `_condamad/stories/regression-guardrails.md`.
5. Check for direct `fetch` / `axios` usage in components.
6. Check for accidental `any`, inline `style=`, duplicate feature logic, and
   misplaced business code in modified `src/components/ui` files.
7. Run the self-review checklist below.
8. Run `git status --short`.

If this is a CONDAMAD story execution, update capsule evidence and
`_condamad/stories/story-status.md` according to `condamad-dev-story`.

## Self-review before completion

Before marking a task complete, verify:

- no duplication was introduced;
- files are placed in the correct feature or shared location;
- naming conventions are respected;
- import alias and barrel-file conventions are respected;
- existing patterns were reused rather than forked;
- query keys are stable, structured, and not duplicated;
- mutations invalidate relevant queries or update cache deliberately;
- API calls go through feature hooks and the central HTTP client;
- loading, empty, error, and fallback UI states are handled;
- UI rendering is separated from data fetching and business logic;
- tests cover the main flows and states;
- applicable regression guardrails are represented in validation evidence.

If any issue is found, fix it before returning the result or document a precise
blocker.

## Forbidden

- Do not bypass `src/lib/api/http-client.ts`.
- Do not put API calls directly in React components.
- Do not put business logic in `src/components/ui`.
- Do not create global state when local state is enough.
- Do not duplicate server state in Zustand.
- Do not add CSS before checking Tailwind and existing style variables.
- Do not use inline styles.
- Do not create duplicate components, hooks, schemas, API clients, or stores
  when an existing one can be extended.
- Do not introduce naming drift or a new pattern variant without documented
  justification.
- Do not create barrel files by default or introduce circular imports through
  barrels.
- Do not mix import alias styles and relative deep imports inconsistently.
- Do not leave a user-facing async component without loading, empty, error, or
  fallback handling where those states can occur.
- Do not change the stack without explicit approval.
- Do not treat skipped validation as passed.

## Definition of Done

A task is complete only when:

- code is placed in the correct feature or shared location;
- no duplication was introduced;
- feature ownership boundaries are respected;
- naming conventions and existing patterns are respected;
- import alias and barrel-file conventions are respected;
- TypeScript strict mode still passes;
- lint passes with no errors;
- important states are covered by tests: success, loading, error, empty, and
  validation when relevant;
- E2E tests are added or updated for critical user flows when required;
- static guard checks show no unclassified violations;
- direct HTTP calls do not bypass the central client;
- TanStack Query keys are stable and mutations invalidate or update cache
  deliberately;
- UI, data fetching, and business logic are separated;
- Zustand usage, if any, satisfies the strict eligibility rules;
- `_condamad/stories/regression-guardrails.md` was read and applicable
  frontend invariants were classified;
- applicable regression guards were run or explicitly documented as skipped or
  blocked with risk;
- new durable frontend invariants were added to the registry when created;
- the implementation follows existing repository patterns;
- skipped validation is explicitly reported with risk.

## Final response

Respond in the user's language. Include:

- concise implementation summary;
- files changed;
- tests/checks run and their result;
- applicable regression guardrails and registry updates;
- skipped checks with reasons;
- remaining risks or limitations;
- local app start command or URL when relevant.

Keep the response short and evidence-based.
