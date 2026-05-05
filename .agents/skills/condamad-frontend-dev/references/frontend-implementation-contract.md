# Frontend Implementation Contract

## TypeScript

Keep strict TypeScript intact:

- Do not weaken `tsconfig`.
- Do not add `skipLibCheck`, disable strictness, or suppress errors to pass.
- Avoid `any`; if unavoidable, add a short comment explaining the boundary.
- Prefer `unknown` for untrusted external data.
- Export explicit types for API payloads, form values, and domain models.
- Prefer discriminated unions for stateful variants when useful.

## API and TanStack Query

All HTTP calls must go through `src/lib/api/http-client.ts`.

Each feature owns its queries, mutations, API payload types, and query-key
construction. Never call API functions directly inside React components; expose
and consume hooks from the feature API layer.

Query keys must be stable, structured arrays:

```ts
["dashboard", "summary"]
["users", "detail", userId]
["invoices", "list", filters]
```

Do not duplicate query-key shapes for the same resource. Prefer a feature-local
query-key helper when a feature has more than one query or mutation.

Feature API modules should expose small functions and hooks:

```ts
export type DashboardSummary = {
  totalUsers: number;
};

export function useDashboardSummaryQuery() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: getDashboardSummary,
  });
}
```

Mutations must either:

- invalidate every relevant query; or
- update the cache manually with an explicit reason.

Validate untrusted server payloads with zod at the boundary when shape matters
to UI behavior. Do not call `fetch` or `axios` directly from components, hooks
outside feature API modules, or pages.

## Imports and public exports

Use the repository's existing import alias convention. Do not mix deep relative
imports and alias imports inconsistently in the same feature or layer.

Prefer canonical public imports when available. A feature may expose a small
public surface only when that convention already exists or when multiple
callers need stable access. Do not import another feature's private files to
reuse internals.

Do not create barrel files by default. Create `index.ts` only when:

- the repository already uses that convention for the same kind of module; or
- the feature needs a deliberate public export surface.

Avoid circular imports caused by barrels. If a barrel hides ownership or makes
imports ambiguous, import the canonical file directly.

## Forms

Use react-hook-form and zod:

- Place schemas under `src/features/<feature>/schemas`.
- Export `type FormValues = z.infer<typeof schema>`.
- Keep submission side effects in feature hooks or route containers.
- Show validation errors from schema output.
- Cover submit loading, success, server error, and invalid input states.

## State

Use the smallest state scope:

1. Component state for local UI state.
2. URL/search params for navigational state.
3. TanStack Query for server state.
4. Zustand only for cross-page client state that is not server-owned and cannot
   be derived from URL, props, or colocated React state.

Do not mirror query results into Zustand. Do not create a store for a single
component unless it is a documented stepping stone to a cross-page behavior.

Zustand is allowed only when all of these are true:

- state is shared across multiple pages or route branches;
- state is not owned by the server;
- state cannot be derived from TanStack Query, URL/search params, props, or
  colocated React state;
- the store has a single clear responsibility.

If any condition is false, use local state, URL state, props, or TanStack Query.

## Styling

Use Tailwind utilities and existing design tokens.

Rules:

- Use `cn()` for conditional classes.
- Do not use inline `style`.
- Check existing CSS variables and Tailwind tokens before creating new ones.
- Keep global CSS limited to base styles, Tailwind layers, tokens, and truly
  global behavior.
- Use lucide-react icons in icon buttons when available.
- Do not put text-only rounded rectangles where a standard icon button is the
  natural control.

## shadcn/ui

`src/components/ui` is for shadcn/ui primitives only.

Do not add business props, API calls, feature-specific text, or app-specific
state to shadcn/ui components. Compose shadcn primitives from feature,
common, or layout components instead.

When `src/components/ui` files are modified, inspect them manually for:

- business props;
- API calls;
- feature-specific text;
- app-specific state;
- TanStack Query usage;
- imports from feature modules.

If modifying a shadcn/ui primitive is required, document why in the final
response and keep the change generic.

## Error handling

Every user-facing server interaction should have intentional states:

- loading;
- success;
- empty when applicable;
- validation error;
- server/network error;
- retry or recovery path when appropriate.

The API layer must normalize transport and server errors into the repository's
canonical error shape. Do not expose raw `fetch`, `axios`, or unknown thrown
values directly to UI components.

UI must render fallback states for loading, empty, and error cases when those
states can occur. Never ignore errors, swallow them silently, or leave a
component with no recovery or fallback UI.

Use central HTTP error handling when available. Do not use silent fallbacks to
hide failed requests, invalid payloads, or missing configuration.

## Separation of concerns

Do not mix data fetching, business logic, and UI rendering in one component.

Components should:

- render UI;
- receive data via props or feature hooks;
- delegate non-trivial decisions to hooks, schemas, API modules, or utilities;
- stay small enough to review without scrolling through unrelated concerns.

Move logic to:

- feature API modules for transport and server payload mapping;
- feature hooks for UI orchestration and reusable interactions;
- schemas for runtime validation;
- feature utilities for pure feature-specific transformations;
- shared `src/lib` or `src/hooks` only when logic is business-neutral.

Do not place business decisions, payload mapping, or cache orchestration inside
shadcn/ui primitives or generic layout components.

## Accessibility

Use semantic HTML and shadcn/ui accessibility behavior.

Check:

- labels for form controls;
- keyboard interaction for menus, dialogs, tabs, and custom controls;
- visible focus states;
- meaningful button names and icon labels;
- no text overlap at common viewport sizes.
