# Architecture - Frontend

## Scope
Part: `frontend`
Project type: `web`

## Runtime and Framework
- React 19 + TypeScript
- Vite build/dev toolchain
- TanStack Query for server-state fetching

## Structure
- `src/pages/`: route-level screens (`HomePage`, `ChatPage`, `NatalChartPage`)
- `src/components/`: feature panels (Billing, Privacy, B2B, Ops)
- `src/api/`: centralized client modules by domain
- `src/state/`: provider wiring (`providers.tsx`)
- `src/tests/`: component/API tests with Vitest + Testing Library

## UI/Interaction Model
- SPA interaction with panels and domain-specific modules
- Consistent loading/error/empty state handling through API layer patterns
- Token-based auth state via utility helpers (`src/utils/authToken.ts`)

## Integration Contract
- Backend consumed via `http://localhost:8000/v1/*` in local dev
- API modules provide typed wrappers for endpoints and errors

## Quality Strategy
- `npm run test` for frontend test suites
- `npm run lint` for TS type-check quality gate
- Dedicated B2B test config (`vitest.b2b.config.ts`)
