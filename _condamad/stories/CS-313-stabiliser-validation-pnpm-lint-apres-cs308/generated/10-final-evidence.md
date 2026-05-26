# Final Evidence — CS-313-stabiliser-validation-pnpm-lint-apres-cs308

## Story status

- Validation outcome: pass
- Ready for review: yes
- Story key: CS-313-stabiliser-validation-pnpm-lint-apres-cs308
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `00-story.md`
- Initial `git status --short`: `?? _condamad/run-state.json`
- Pre-existing dirty files: `_condamad/run-state.json` untracked before implementation.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, because required `generated/` files were missing.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Capsule validated after generation. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Capsule validated after generation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC-by-AC evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated for done closure. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `evidence/pnpm-lint-before.txt` | `pnpm lint` from `frontend` exit 0. | PASS | Fresh state captured. |
| AC2 | `evidence/cause-ledger.md` | CS-308 EPERM evidence read; fresh run no longer reproduces EPERM. | PASS | Classified as resolved Windows-environment blocker. |
| AC3 | Standard `pnpm lint` remains the closure path. | `evidence/pnpm-lint-after.txt` exit 0. | PASS | No fallback required. |
| AC4 | Existing lint TypeScript config unchanged. | `tsc.CMD --noEmit -p tsconfig.lint.json` exit 0. | PASS | Output in `evidence/typescript-lint.txt`. |
| AC5 | Existing node TypeScript config unchanged. | `tsc.CMD --noEmit -p tsconfig.node.json` exit 0. | PASS | Output in `evidence/typescript-lint.txt`. |
| AC6 | No app source files changed. | `git diff --name-only`; TSX style scan reviewed as pre-existing/out of scope. | PASS | Changed frontend file is documentation only. |
| AC7 | `frontend/README.md` quality commands now use pnpm. | Drift scan leaves only story self-references. | PASS | `package.json` and `pnpm-lock.yaml` unchanged. |
| AC8 | CS-313 evidence report created. | `evidence/validation.txt` plus generated traceability/final evidence. | PASS | Final command/cause/result/risk persisted. |

## Files changed

- `frontend/README.md`
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/**`
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/generated/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- No automated test files changed; this validation-tooling story is covered by command evidence.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `condamad_prepare.py ... --story-key CS-313-stabiliser-validation-pnpm-lint-apres-cs308` | repo root after venv activation | PASS | Generated missing capsule files. |
| `condamad_validate.py _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308` | repo root after venv activation | PASS | Capsule valid after generation. |
| `pnpm lint` | `frontend` | PASS | 0 | Fresh lint state captured. |
| `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json` | `frontend` | PASS | 0 | Equivalent lint project passes. |
| `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json` | `frontend` | PASS | 0 | Equivalent node project passes. |
| `pnpm lint` | `frontend` | PASS | 0 | Final lint path passes after README drift correction. |
| `rg -n "npm run lint|yarn lint|bun lint" frontend _condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308` | repo root | PASS | 0 | Only story self-references remain; frontend README drift removed. |
| `rg -n "npm run lint|yarn lint|bun lint" frontend` | repo root | PASS | 1 | No frontend package-manager drift remains; exit 1 means no matches. |
| `rg -n "style=" src -g "*.tsx"` | `frontend` | PASS | 0 | Existing matches classified as pre-existing and out of scope because no TSX changed. |
| `rg -n -- "--default_dropshadow|migration-only" src` | `frontend` | PASS | 0 | Existing registry/test matches only; no CSS changed. |
| `condamad_story_validate.py _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308\00-story.md` | repo root after venv activation | PASS | 0 | Story contract valid. |
| `condamad_story_lint.py --strict _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308\00-story.md` | repo root after venv activation | PASS | 0 | Strict story lint valid. |
| `python -B -c <cause-ledger key check>` | repo root after venv activation | PASS | 0 | Required validation evidence keys are present. |

## Commands skipped or blocked

- No Playwright or full Vitest run: story changes validation procedure/docs only and `pnpm lint` plus both TypeScript projects are the required checks.

## DRY / No Legacy evidence

- No duplicate lint path was introduced.
- No package-manager replacement was introduced.
- No compatibility shim, alias, fallback script, dependency reinstall, or lockfile churn was added.
- README command examples now align with the existing pnpm package-manager contract.

## Diff review

- `git diff --name-only -- frontend _condamad`: no frontend or CONDAMAD implementation delta remained before this final evidence refresh.
- `git status --short`: only `_condamad/run-state.json` was untracked before this final evidence refresh.
- `git diff --check -- frontend _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308 _condamad\stories\story-status.md`: PASS in closure evidence with line-ending normalization warnings only.

## Final worktree status

- Before this final evidence refresh, the only dirty path reported by `git status --short` was `?? _condamad/run-state.json`.
- This alignment review refreshes CS-313 evidence/review text only, to keep closure metadata aligned with story and tracker status `done`.

## Remaining risks

- Windows EPERM can recur when another process locks pnpm internal files; no repository-owned cause is currently reproduced.

## Suggested reviewer focus

- Verify that accepting standard `pnpm lint` as closed is appropriate now that the EPERM blocker is not reproduced and no fallback is used.

## Feedback loop routing

- No reusable guardrail update: the issue resolved as environment-specific EPERM, and the only repository drift was corrected in `frontend/README.md`.
