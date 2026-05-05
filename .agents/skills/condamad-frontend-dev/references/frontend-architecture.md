# Frontend Architecture Reference

## Source-of-truth order

Apply this order when instructions conflict:

1. Explicit user request for the current task.
2. Repository `AGENTS.md` instructions.
3. Applicable invariants in `_condamad/stories/regression-guardrails.md`.
4. Existing frontend code and configuration.
5. This skill's stack and structure contract.
6. General React conventions.

## Feature ownership

Business code belongs in `src/features/<feature>/`.

Use feature folders for:

- API functions and query/mutation hooks;
- feature-specific components;
- feature-specific hooks;
- zod schemas;
- domain types;
- feature-local constants and mappers.

Use shared folders only for code that has no business ownership:

- `src/components/ui`: shadcn/ui only.
- `src/components/layout`: app shell, sidebar, navbar, navigation frame.
- `src/components/common`: reusable business-neutral UI.
- `src/lib`: technical utilities, HTTP client, query client, date helpers,
  class-name helpers, environment utilities.
- `src/hooks`: generic React hooks with no feature dependency.
- `src/stores`: Zustand stores only when cross-page client state is justified.

Each feature owns its own API modules, hooks, schemas, types, constants,
mappers, and feature-specific components. Other features must not import or
modify those internals.

When two features need the same behavior, extract it deliberately to:

- `src/components/common` for reusable business-neutral UI;
- `src/lib` for shared technical utilities;
- `src/hooks` for generic React hooks.

Cross-feature imports are forbidden unless the current task explicitly
justifies them and the final evidence documents the reason.

## Routing and providers

Prefer:

- `src/app/router.tsx` for route definitions.
- `src/app/providers.tsx` for QueryClientProvider, router providers, theme,
  toast, and other app-wide providers.
- `src/app/App.tsx` as a thin composition root.

Default to `src/app` plus `src/features` for new React Router work. Do not add
new `src/pages` route screens unless the existing repository already uses
`src/pages` as the canonical route-screen convention. Never create the same
screen in both `src/pages` and `src/features`.

Do not hide feature data loading inside the root app when it belongs to a
route or feature hook.

## DRY checks before adding files

Before adding a component, hook, schema, API function, or store, search for:

```powershell
rg "<feature-or-domain-term>" frontend/src
rg "use[A-Z].*Query|use[A-Z].*Mutation" frontend/src
rg "z\\.object|react-hook-form|useForm" frontend/src
rg "zustand|from ['\\\"]zustand|createStore|create\\(" frontend/src/stores frontend/src/features
```

Reuse or extend an existing implementation when responsibilities match. Creating
a parallel component, hook, schema, API function, route, or store for the same
responsibility is forbidden.

The Zustand/store scan is heuristic: classify hits manually instead of treating
every `create(` match as a violation.

## Placement decision table

| Need | Location |
| --- | --- |
| shadcn/ui primitive | `src/components/ui` |
| app shell/sidebar/navbar | `src/components/layout` |
| reusable neutral widget | `src/components/common` |
| business-specific component | `src/features/<feature>/components` |
| server call and query hook | `src/features/<feature>/api` |
| form schema | `src/features/<feature>/schemas` |
| domain or payload type | `src/features/<feature>/types.ts` |
| HTTP transport | `src/lib/api/http-client.ts` |
| query client defaults | `src/lib/api/query-client.ts` |
| app-wide client state | `src/stores` |

## Component boundaries

Keep components focused:

- Presentational components render props and delegate side effects.
- Container/route components wire hooks, mutations, and navigation.
- Hooks own reusable interaction or data orchestration.
- Schemas own runtime validation.
- API modules own transport and server payload mapping.

Avoid large prop-heavy components. Prefer composition, smaller child
components, and feature-local hooks.
