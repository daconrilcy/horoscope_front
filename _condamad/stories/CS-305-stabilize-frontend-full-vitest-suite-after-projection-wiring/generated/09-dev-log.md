# Dev Log

## Preflight

- Initial `git status --short`: clean.
- Story tracker verified: CS-305 path and source brief match `_condamad/stories/story-status.md`.
- Capsule generated files were missing; generated and validated with the CONDAMAD preparation scripts after activating `.venv`.
- A mistaken parallel `_condamad/stories/cs-305` capsule from an ambiguous prepare command was removed after path verification.

## Implementation notes

- The initial full Vitest run failed in dashboard shortcuts, dashboard page, daily horoscope, and consultations tests.
- Language leakage came from shared test state and explicit English fixtures that only set `localStorage.lang`, while runtime language detection prioritizes `navigator.language`.
- Fixed the test setup to clear `localStorage.lang` before each test and made English fixtures explicitly stub `navigator.language` to `en-US`.
- Added the missing `back_to_overview` consultation translation instead of tolerating the raw key.
- Increased one dashboard async wait to remove a full-suite timing flake on Windows.
- CS-303 API and rendering source files remained unchanged.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | FAIL then PASS | Before log captured 18 initial failures; after log captured 116 files passing. |
| `pnpm lint` | PASS | First attempt hit a Windows `pnpm` lockfile EPERM, retry passed. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi` | PASS | CS-303 API guard retained. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation` | PASS | CS-303 rendering guard retained. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi` | PASS | Architecture guard retained. |
| `rg -n "fetch\\(.*/v1/astrology/projections" src` | PASS | Exit 1 interpreted as no matches. |
| `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src` | PASS | Exit 1 interpreted as no matches. |
| `rg -n "style=" <touched TSX tests>` | PASS | Exit 1 interpreted as no matches. |
| `python -B ...condamad_validate.py <capsule>` | PASS | Run with `.venv` active. |

## Issues encountered

- The story text mentions a global inline-style scan. The repository already contains pre-existing allowlisted inline styles outside the touched files; this story introduced none and the inline-style policy suite passes as part of full Vitest.
- `pnpm` created an untracked `frontend/pnpm-lock.yaml` during lint execution; it was removed because dependency changes are out of scope.

## Decisions made

- Kept `detectLang` behavior unchanged because existing i18n tests enforce navigator-over-localStorage precedence.
- Treated the failing English assertions as stale fixtures unless the runtime contract required a translation update.
- Updated delivery evidence only for validation-status closure; no backend or product UI behavior was changed.
