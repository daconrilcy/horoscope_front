# CS-313 cause ledger

## Classification

- `command`: `pnpm lint`
- `working_directory`: `frontend`
- `result`: `pass`
- `cause`: `resolved-windows-environment`
- `fallback_status`: `not-used`
- `residual_risk`: Windows file locking can still block pnpm lock renames on another machine or during concurrent node activity.

## Evidence

- CS-308 recorded `pnpm lint` as blocked before script execution with EPERM while renaming `node_modules\.pnpm\lock.yaml.*`.
- Fresh CS-313 reproduction on 2026-05-26 passes and prints the package script: `tsc --noEmit -p tsconfig.lint.json && tsc --noEmit -p tsconfig.node.json`.
- Local binary checks also pass:
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json`
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json`
- No repository-owned TypeScript or pnpm lock defect was reproduced.
- A documentation drift was found in `frontend/README.md`: quality commands used `npm run ...` despite the pnpm workflow. The README was updated to `pnpm ...`.

## Closure decision

The lint path is closed through the standard `pnpm lint` command. No fallback command is required for this machine. The supported fallback remains the exact local `tsc.CMD` pair only if a future Windows EPERM prevents pnpm from starting the script.
