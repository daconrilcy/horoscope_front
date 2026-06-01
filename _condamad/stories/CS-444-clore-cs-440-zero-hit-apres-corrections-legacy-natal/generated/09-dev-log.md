# Dev Log

## Preflight

- Initial `git status --short`: `_condamad/run-state.json` was already dirty.
- Capsule was incomplete; first prepare attempt created an unintended `_condamad/stories/cs-444` capsule because the story mentions multiple CS IDs.
- The unintended generated capsule was removed after resolving it inside `_condamad/stories`; canonical capsule was repaired with `--repair-generated-only`.
- `condamad_validate.py` passed before implementation.

## Implementation notes

- No runtime source file was changed.
- CS-440 blocker evidence was updated after CS-441, CS-442, and CS-443 were verified `done` with clean reviews.
- CS-440 CR-3 and CR-4 were closed using current executable evidence.
- CS-444 previous review was replaced and is not used as final review proof.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py --repair-generated-only <CS-444 capsule>` | PASS | Repaired missing generated files. |
| `condamad_validate.py <CS-444 capsule>` | PASS | Structure valid before implementation. |
| `ruff check .` | PASS | Run from `backend` after venv activation. |
| Backend architecture/LLM guard pytest suite | PASS | `54 passed`. |
| Backend theme natal product/read pytest suite | PASS | `24 passed, 22 deselected`. |
| Runtime route/OpenAPI assertions | PASS | Old public natal routes absent. |
| Frontend targeted Vitest suite | PASS | `136 passed`. |
| `pnpm --dir frontend lint` | PASS | TypeScript lint configs passed. |
| Bounded `rg` scans | PASS / classified | Zero-hit for generator, URL, and positive mocks; old-key residuals are classified readonly/admin/rejection/extinction. |

## Issues encountered

- The broad story scan `rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src` returns classified readonly/admin/rejection/extinction residuals. This is accepted under RG-174 and recorded as `PASS` for AC4 because no unauthorized public/runtime generator hit remains.

## Final `git status --short`

- Recorded during final evidence after validation.
