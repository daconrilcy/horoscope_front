# Story CS-313 stabiliser-validation-pnpm-lint-apres-cs308: Stabilize pnpm lint Validation After CS-308
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-313-stabiliser-validation-pnpm-lint-apres-cs308.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: CS-308 is delivered, but final closure keeps a `pnpm lint` blocker caused by Windows EPERM before script execution.
- Source stakes: make frontend lint validation reproducible, avoid permanent manual substitution, and keep CS-308 closure evidence auditable.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without expanding frontend code scope.

## Objective

Stabilize the standard frontend lint validation after CS-308 by proving `pnpm lint` passes from `frontend` or by documenting one official Windows command path.
The story closes only when the final evidence cites the cause, command, result, and residual risk for the lint validation path.

## Target State

- `pnpm lint` from `frontend` passes, or a Windows EPERM limitation is proven with a supported command path using the existing local binaries.
- The equivalent TypeScript commands from the current lint script pass from `frontend`.
- The root cause is classified as local repository cause, concurrent process, pnpm lock handling, or environmental Windows EPERM.
- No application file is changed unless it is directly required to close a proven repository-owned lint blocker.
- CS-308 evidence or a CS-313 validation report records the final command, result, cause, and residual risk.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-313-stabiliser-validation-pnpm-lint-apres-cs308.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-313` after `CS-312`.
- Evidence 3: `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md` - CS-308 limitation read.
- Evidence 4: `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt` - EPERM details read.
- Evidence 5: `frontend/package.json` - lint script read and maps to two TypeScript no-emit commands.
- Evidence 6: `frontend/pnpm-lock.yaml` - lockfile presence checked for the frontend workspace.
- Evidence 7: `AGENTS.md` - Windows PowerShell and validation discipline read.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - scoped resolver selected local guardrails only.
- Source-alignment evidence: PASS; the story targets the exact CS-308 `pnpm lint` validation gap and keeps package manager changes out of scope.

## Domain Boundary

- Domain: frontend-validation
- In scope:
  - Reproducing or rechecking `pnpm lint` from `frontend` in Windows PowerShell.
  - Classifying the EPERM cause using bounded repository and process evidence.
  - Correcting only a repository-owned local cause that blocks the existing lint script.
  - Documenting one official fallback command path when the cause is environmental.
  - Updating CS-308 evidence or a CS-313 evidence report with the final validation outcome.
- Out of scope:
  - Backend behavior, API contracts, DB schema, auth, i18n wording, styling, build tooling redesign, migrations, and package-manager replacement.
  - Broad dependency reinstall, lockfile regeneration without proof, TypeScript or ESLint configuration change unrelated to the EPERM blocker.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No frontend UI route, screen, styling change, feature behavior change, or product wording change.
  - No switch from pnpm to another package manager.
  - No broad reformat or dependency churn to obtain a passing validation.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend validation tooling stabilization contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only frontend validation procedure, CS-308 evidence, CS-313 evidence, or a proven repository-owned lint blocker.
  - Keep the existing `lint` script semantics: `tsc --noEmit -p tsconfig.lint.json` then `tsc --noEmit -p tsconfig.node.json`.
  - Keep package manager choice as pnpm.
  - Preserve application runtime behavior unchanged.
  - Preserve TypeScript and ESLint configuration unless the reproduced blocker proves a local configuration defect.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: closure requires package-manager replacement, dependency reinstall, or lint-script semantic changes.
- Additional validation rules:
  - A fresh `pnpm lint` attempt must be captured before accepting a fallback path.
  - The final fallback path must use existing `node_modules/.bin` local binaries and match the current `frontend/package.json` script.
  - TypeScript no-emit commands must pass after any local correction.
  - Evidence must state whether the fallback is temporary environmental guidance or canonical Windows validation guidance.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pnpm lint` and the two `tsc.CMD` commands prove frontend validation behavior. |
| Baseline Snapshot | yes | Before and after validation logs prove the validation path changed only by evidence or a local fix. |
| Ownership Routing | yes | Validation procedure, CS-308 evidence, and frontend files must stay in canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for masking lint failures or weakening validation. |
| Contract Shape | yes | The validation report has exact cause, command, result, and residual-risk fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Package-manager swaps, broad reinstall churn, and app-only changes must stay absent. |
| Persistent Evidence | yes | Repro logs, TypeScript command output, final validation report, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The fresh `pnpm lint` state is captured. | Evidence profile: baseline_before_after_diff; `pnpm lint` from `frontend`. |
| AC2 | The EPERM cause is classified. | Evidence profile: baseline_before_after_diff; `python` checks CS-313 cause ledger. |
| AC3 | The lint path is closed. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` or `tsc.CMD` commands from `frontend`. |
| AC4 | TypeScript lint projects pass. | Evidence profile: frontend_typecheck_no_orphan; `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json`. |
| AC5 | Node TypeScript project passes. | Evidence profile: frontend_typecheck_no_orphan; `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json`. |
| AC6 | Application source changes are classified. | Evidence profile: targeted_forbidden_symbol_scan; `python` checks changed-files ledger; `rg` scans TSX styles. |
| AC7 | Package manager remains pnpm. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks package-manager scripts and docs. |
| AC8 | Final validation evidence is persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-313 validation artifact paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the CS-308 final evidence, CS-308 validation log, `frontend/package.json`, lockfile state, and AGENTS rules. (AC: AC1)
- [ ] Task 2: Run `pnpm lint` from `frontend` and persist the fresh output in the CS-313 evidence directory. (AC: AC1)
- [ ] Task 3: Classify the EPERM cause using bounded lockfile, process, script, and local repository evidence. (AC: AC2)
- [ ] Task 4: Correct a proven repository-owned blocker with the smallest coherent delta. (AC: AC2, AC3)
- [ ] Task 5: Document the official Windows fallback command path only when the cause is environmental. (AC: AC3)
- [ ] Task 6: Run both local TypeScript no-emit commands from `frontend` and persist their output. (AC: AC4, AC5)
- [ ] Task 7: Verify package manager and application-source boundaries with targeted scans and `git diff --name-only`. (AC: AC6, AC7)
- [ ] Task 8: Update CS-308 evidence or create the CS-313 final validation report with cause, command, result, and risk. (AC: AC8)

## Files to Inspect First

- `_story_briefs/cs-313-stabiliser-validation-pnpm-lint-apres-cs308.md` - source brief.
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md` - CS-308 final limitation.
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt` - EPERM reproduction details.
- `frontend/package.json` - canonical lint script.
- `frontend/pnpm-lock.yaml` - workspace lockfile state.
- `AGENTS.md` - Windows PowerShell and validation discipline.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `pnpm lint` from `frontend`.
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json` from `frontend`.
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json` from `frontend`.
  - `git diff --name-only -- frontend _condamad` from repository root.
  - `AST guard` through TypeScript no-emit validation and targeted source scans.
- Secondary evidence:
  - CS-313 cause ledger under `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/`.
  - Targeted `rg` scans for package-manager replacement and unsupported validation commands.
- Static scans alone are not sufficient because:
  - The story closes a runtime validation blocker, so command output from Windows PowerShell is decisive.

## Contract Shape

- Contract type:
  - Frontend validation closure evidence contract.
- Fields:
  - `command`: exact command that was run.
  - `working_directory`: `frontend` or repository root.
  - `result`: pass, blocked-environmental-eperm, blocked-local-cause, or blocked-user-decision.
  - `cause`: pnpm-lock-rename, concurrent-process, local-script, local-repository-file, or windows-environment.
  - `fallback_status`: not-used, temporary-environmental, or canonical-windows.
  - `residual_risk`: concise risk statement.
- Required fields:
  - `command`
  - `working_directory`
  - `result`
  - `cause`
  - `fallback_status`
  - `residual_risk`
- Optional fields:
  - `local_fix_path`
  - `linked_cs308_update`
- Required commands:
  - `pnpm lint`
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json`
  - `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json`
- Status codes:
  - none; this story does not change HTTP behavior or API response codes.
- Serialization names:
  - Evidence keys are written exactly as `command`, `working_directory`, `result`, `cause`, `fallback_status`, and `residual_risk`.
- Frontend type impact:
  - only type changes required by a proven repository-owned lint blocker are authorized.
- Backend type impact:
  - none; backend API contracts remain unchanged.
- Generated contract impact:
  - no generated client, OpenAPI output, or build manifest change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/pnpm-lint-before.txt`
  - `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/cause-ledger.md`
- Comparison after implementation:
  - `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/pnpm-lint-after.txt`
  - `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/typescript-lint.txt`
  - `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/validation.txt`
- Expected invariant:
  - The only intended validation delta is that CS-308 lint closure no longer depends on an undocumented manual substitution.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Frontend lint script | `frontend/package.json` | Root package script or alternate package manager |
| TypeScript project validation | `frontend/tsconfig.lint.json` and `frontend/tsconfig.node.json` | Ad hoc project file outside `frontend` |
| Local lint blocker fix | Exact frontend file proven by reproduction | Unrelated frontend UI or backend files |
| Validation evidence | CS-313 `evidence/` or CS-308 evidence update | Application source comments as validation log |
| Package manager policy | Existing pnpm workflow | npm, yarn, bun, or broad reinstall workflow |

## Mandatory Reuse / DRY Constraints

- Reuse the existing `frontend/package.json` lint script semantics.
- Reuse local binaries from `frontend/node_modules/.bin` for the documented Windows fallback path.
- Reuse CS-308 evidence paths when updating the original limitation is clearer than duplicating the same closure statement.
- Reuse existing frontend TypeScript configs; do not add parallel lint config files.
- Do not add external packages, generated tooling, broad helper scripts, or duplicate validation procedures.

## No Legacy / Forbidden Paths

- No legacy validation path may be introduced for frontend lint.
- No compatibility package-manager path may be introduced for frontend lint.
- No fallback may bypass the current lint script semantics.
- Do not add `npm`, `yarn`, or `bun` commands as the canonical validation path.
- Do not add broad lockfile regeneration, dependency reinstall, or source reformat churn without proof of a local cause.
- Do not preserve a hidden manual substitution without final evidence that classifies its status.

## Reintroduction Guard

- Forbidden validation drift:
  - New canonical lint command using `npm`, `yarn`, or `bun`.
  - New broad reinstall step as closure proof.
  - New application source change unrelated to a proven lint blocker.
- Required deterministic guards:
  - `rg -n "npm run lint|yarn lint|bun lint" frontend _condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308`
  - `git diff --name-only -- frontend _condamad`
  - `pnpm lint` or both local `tsc.CMD` commands from `frontend`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `styles-inline-tsx-frontend` | Application TSX style drift remains out of scope. | `rg` style scan when TSX changes. |
| RG-052 `css-migration-only-frontend` | CSS token migration drift remains out of scope. | `rg` CSS token scan when CSS changes. |
| Registry gap | No exact `pnpm lint` Windows EPERM guardrail exists in the scoped registry. | Resolver output and CS-313 cause ledger. |

Non-applicable examples kept out of scope:

- Frontend DB, auth, i18n, API projection, and migration guardrails do not match this validation-tooling story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Initial lint output | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/pnpm-lint-before.txt` | Preserve fresh `pnpm lint` state. |
| Cause ledger | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/cause-ledger.md` | Record cause, command, result, and risk. |
| TypeScript output | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/typescript-lint.txt` | Preserve equivalent lint command output. |
| Final validation | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/validation.txt` | Preserve final closure commands. |
| Review output | `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for lint failures, package-manager drift, or validation weakening.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/pnpm-lint-before.txt` - fresh `pnpm lint` output.
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/cause-ledger.md` - cause classification.
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/typescript-lint.txt` - local binary command output.
- `_condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308/evidence/validation.txt` - final validation summary.
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt` - original evidence closure update.

Likely tests:

- `frontend` command `pnpm lint` - standard lint validation.
- `frontend` command `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json` - lint TypeScript project.
- `frontend` command `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json` - node TypeScript project.

Files not expected to change:

- `backend/**` - out of scope; no backend behavior is touched.
- `frontend/src/**` - out of scope unless a reproduced repository-owned lint blocker points to an exact source file.
- `frontend/package.json` - unchanged unless a local script defect is proven.
- `frontend/pnpm-lock.yaml` - unchanged unless a repository-owned lockfile cause is proven.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: from `frontend`, run `pnpm lint` and persist stdout or stderr to `evidence/pnpm-lint-before.txt`.
- VC2: from `frontend`, run `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.lint.json`.
- VC3: from `frontend`, run `.\node_modules\.bin\tsc.CMD --noEmit -p tsconfig.node.json`.
- VC4: from repository root, run `git diff --name-only -- frontend _condamad`.
- VC5: from repository root, run `rg -n "npm run lint|yarn lint|bun lint" frontend _condamad/stories/CS-313-stabiliser-validation-pnpm-lint-apres-cs308`.
- VC6: from repository root after venv activation, run story validation:
  `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308\00-story.md`.
- VC7: from repository root after venv activation, run strict story lint:
  `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-313-stabiliser-validation-pnpm-lint-apres-cs308\00-story.md`.

## Regression Risks

- A local EPERM blocker could be hidden by documenting only the `tsc.CMD` commands.
- A package-manager drift could make future validation different from the current pnpm workflow.
- Broad reinstall or lockfile churn could change dependencies without addressing the reproducible cause.
- Updating only CS-308 evidence without a CS-313 cause ledger could make the closure hard to review.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Use Windows PowerShell paths and commands exactly as recorded in the validation plan.
- Keep Python validation commands behind the activated `.venv`.
- Keep application source changes at zero unless a reproduced repository-owned lint blocker proves an exact target file.

## References

- `_story_briefs/cs-313-stabiliser-validation-pnpm-lint-apres-cs308.md`
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/generated/10-final-evidence.md`
- `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/evidence/validation.txt`
- `frontend/package.json`
- `frontend/pnpm-lock.yaml`
- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
