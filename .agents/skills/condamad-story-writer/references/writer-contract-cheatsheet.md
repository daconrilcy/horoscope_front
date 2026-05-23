# CONDAMAD Story Writer Contract Cheatsheet

Use this short checklist before reading broad references. It captures the
validator-sensitive rules that most often cause slow correction loops.

## First Lines And Dependency Gate

Every generated story file must start exactly like this:

```md
# Story CS-001 health-endpoint: Add Backend Health Endpoint

Status: ready-to-dev
```

Do not run validation until the `Status:` line is present directly below the
title.

When the story says no dependency may be added, still include the complete
Dependency Policy section:

```md
## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.
```

Avoid extra dependency wording elsewhere. Use `Do not add external packages`
instead of repeating broad `dependency` prose in many sections.

## Required Runtime Evidence Names

For API-route stories, name runtime evidence explicitly:

- `app.openapi()` for OpenAPI contract evidence.
- `app.routes` for registered route evidence.
- `pytest` or `TestClient` for HTTP behavior evidence.

Do not write only generic evidence such as "runtime validation" or "API test".

## Acceptance Criteria Shape

Every AC must include:

- an exact observable requirement;
- deterministic validation evidence;
- at least one validator-recognized evidence token: `pytest`, `python`,
  `ruff`, `rg`, `npm`, `pnpm`, `vitest`, `eslint`, `tsc`, an explicit
  `tests/...` file path, or a bounded `Manual check:` sentence.

Prefer short AC rows. Keep each markdown table line under 180 characters.
Keep each AC requirement single-invariant. Avoid `and`, slash-separated
requirements, or multi-outcome wording in the Requirement cell. Put details
such as status code plus payload shape in the evidence or Validation Plan.
Never shorten paths with `...`; strict lint treats ellipses as template
placeholders. If a full path makes an AC row too long, shorten the Requirement
cell first and keep the full test path or command in the evidence cell.

If an AC Requirement contains `runtime`, `route`, `API`, `schema`, `manifest`,
`config`, or similar runtime-contract terms, its evidence cell must include a
real runtime check: a full `pytest -q ...` test path, `TestClient`, `AST guard`,
`app.routes`, `app.openapi()`, a loaded config/settings check, or an equivalent
validator-recognized runtime command. A vague phrase such as "`pytest` runs the
runtime test file" is not enough.

Do not use `Test-Path`, `Get-Content`, an artifact path alone, or prose such as
"validation artifact exists" as the only evidence. Those are not concrete AC
evidence for `condamad_story_validate.py`.

Validator-safe evidence examples:

- `pytest -q backend/tests/api/test_health.py`
- `python -c "from backend.app.main import app; assert '/health' in app.openapi()['paths']"`
- `python -c "from backend.app.main import app; assert '/health' in {getattr(r, 'path', '') for r in app.routes}"`
- `rg -n "/api/health|/healthz|/ready|/status" backend/app backend/tests`
- `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-001-health-endpoint/evidence/validation.txt').exists()"`

Use only validator-known evidence profiles in AC rows:

- `route_removed`
- `python_module_removed`
- `frontend_route_removed`
- `no_legacy_contract`
- `field_removed`
- `namespace_converged`
- `runtime_openapi_contract`
- `openapi_before_after_snapshot`
- `route_absence_runtime`
- `python_import_absence`
- `ast_architecture_guard`
- `repo_wide_negative_scan`
- `targeted_forbidden_symbol_scan`
- `allowlist_register_validated`
- `json_contract_shape`
- `api_error_shape_contract`
- `frontend_typecheck_no_orphan`
- `baseline_before_after_diff`
- `batch_migration_mapping`
- `reintroduction_guard`
- `external_usage_blocker`

Never write `Evidence profile: persistent_evidence` in an AC row. Persistent
evidence is a contract section, not a validator-known AC evidence profile.

## Validator-Sensitive Required Markers

Include these markers in the first draft. They are intentionally exact because
the local validator checks wording and list shapes.

Current State Evidence must include at least one item in this shape:

```md
- Evidence 1: `_story_briefs/<brief>.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign the story number.
- Repository structure alert: `backend` is absent in this workspace.
```

Use the marker `Repository evidence assumption risk:` only when no concrete
evidence item exists. Prefer concrete `Evidence N:` rows.
Do not write transient tracker evidence such as "no existing row" in the story
after registering it. The final story must describe stable tracker use, because
the tracker row may already exist by the time review runs.

Domain Boundary must include both exact markers:

```md
- Domain: backend-api
- In scope:
  - Backend API route creation for `GET /health`.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, and business logic.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
```

Implementation Tasks must use checklist rows starting with `- [ ] Task`:

```md
- [ ] Task 1: Register `GET /health` on the loaded app object. (AC: AC1)
```

No Legacy / Forbidden Paths must include the words `legacy`, `compatibility`,
and `fallback`, plus explicit forbidden surfaces. For a simple `GET /health`
create story, use short lines like:

```md
- No legacy route path may be added for this endpoint.
- No compatibility route path may be added for this endpoint.
- No fallback route path may be added for this endpoint.
```

Dev Agent Instructions must include these guardrail sentences exactly once:

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## API Story AC Starter Rows

For simple API-route stories, start from this shape, replace paths/statuses, and
keep the final markdown table rows under 160 characters by moving long commands
to the Validation Plan when needed.

- AC1 runtime route evidence:
  `Evidence profile: runtime_openapi_contract; python -c "<app.routes assertion>"`.
- AC2 OpenAPI evidence:
  `Evidence profile: runtime_openapi_contract; python -c "<app.openapi() assertion>"`.
- AC3 HTTP behavior evidence:
  `Evidence profile: json_contract_shape; pytest -q <TestClient test path>`.
  Requirement example: `GET /health returns the exact success payload.`
- AC4 No Legacy evidence:
  `Evidence profile: route_absence_runtime; python -c "<app.routes absence assertion>"; rg -n "<forbidden paths>" <bounded paths>`.
  Requirement example for create stories: `Only the /health public route is authorized.`
- AC5 persisted evidence:
  `Evidence profile: baseline_before_after_diff; python -c "<Path(...).exists() assertion>"`.

When an AC cites a named validation command such as `VC1`, keep `python`,
`pytest`, `rg`, or the exact test path in the AC evidence cell; a bare `VC1` is
not enough for the validator.

Validator-safe compact AC table for a simple `GET /health` story:

```md
| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The loaded app registers `GET /health`. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`. |
| AC2 | OpenAPI exposes `/health` with method `get`. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`. |
| AC3 | `GET /health` returns the exact payload. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_health.py`. |
| AC4 | Only the `/health` public route is authorized. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `rg` checks paths. |
| AC5 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence paths. |
```

When the source brief lists broad validation commands, keep them in the
Validation Plan even when AC rows use narrower targeted commands. For this test
brief, include all three commands:

```md
- VC5: `ruff format .`
- VC6: `ruff check .`
- VC8: `pytest -q`
```

## Mandatory Contract Names For API Routes

For a new or changed API route, include concrete content for:

- Runtime Source of Truth Contract: `app.openapi()` and `app.routes`.
- Contract Shape Contract: method, path, response status, JSON fields.
- Baseline Snapshot Contract: before/after route or OpenAPI artifact.
- Reintroduction Guard Contract: forbidden aliases or removed paths.
- Persistent Evidence Contract: generated evidence artifact path.

Mark non-applicable contracts explicitly with a short reason.

## Custom Backend Domain Stories

For backend domain or runtime stories that are not API-route, removal,
migration, split, move, or convergence stories, do not invent a new primary
archetype name. Use:

```md
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
```

When such a story touches runtime enrichment, the Runtime Source of Truth
section must name validator-recognized runtime artifacts explicitly:

- `AST guard` for architecture checks;
- a full `pytest -q backend/tests/...` path for runtime behavior;
- loaded config/settings, DB schema, generated manifest, `app.routes`, or
  `app.openapi()` only when those surfaces are actually in scope.

Do not rely on generic phrases such as "runtime tests" or "runtime evidence"
alone.

Before drafting a complex domain story, extract the source brief's named work
items and preserve them explicitly. If the brief names primitives such as
`factory`, `factories`, `resolver`, `runtime`, `catalog`, `contract`, `profile`,
`enum`, `prompt`, `renderer`, `API`, `DB`, or `migration`, classify each one as
in scope or out of scope in the story. In-scope primitives must appear in:

- Domain Boundary or Target State;
- Implementation Tasks;
- Ownership Routing or Expected Files to Modify;
- Validation Plan or Acceptance Criteria evidence.

Do not hide a named brief primitive behind a broader word. For example, when a
brief asks for "factories/runtime de resolution", the story must explicitly
mention factory helpers, runtime resolution, and resolver behavior rather than
only saying catalog or profile layer.

## Expected Files To Modify Block

Use this block for simple backend API route creation stories. Keep the marker
`Files not expected to change:` exactly as written.

```md
## 19. Expected Files to Modify

Likely files:

- `backend/app/main.py` - register the health route.
- `backend/app/api/health.py` - define `GET /health`.
- `_condamad/stories/<story>/evidence/openapi-after.json` - persist OpenAPI evidence.

Likely tests:

- `backend/tests/api/test_health.py` - cover status, payload and route behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
```

## Create Story Removal-Trigger Hygiene

For `Operation type: create`, keep removal vocabulary out of `Objective`,
`Trigger / Source`, and `Acceptance Criteria`. These sections feed the removal
detector and can cause slow false-positive correction loops.

Avoid these tokens in those sections unless the operation is actually `remove`:

- `legacy`
- `compat`
- `fallback`
- `alias`
- `shim`
- `deprecated`
- `delete`
- `remove`
- `removal`

Use neutral create-story wording instead:

- Prefer `Only the /health public route is authorized.`
- Include runtime evidence with `python` over `app.routes` or `app.openapi()` when
  an AC says a route is the only authorized public surface.
- Prefer `rg -n "/api/health|/healthz|/ready|/status" backend/app backend/tests`
  in the Validation Plan.
- Put sensitive technical scan terms only in a bounded validation command when
  they are required by a guardrail.

## Compact API Contract Blocks

Use these compact blocks for simple API-route stories instead of opening every
transverse contract file.

For simple `GET /health` stories, do not improvise section names. Use these
exact headings and markers in the first draft:

```md
# Story CS-001 health-endpoint: Add Backend Health Endpoint
Status: ready-to-dev

## Trigger / Source
## Objective
## Target State
## Current State Evidence
## Domain Boundary
## Operation Contract
## Required Contracts
## Acceptance Criteria
## Implementation Tasks
## Files to Inspect First
## Runtime Source of Truth
## Contract Shape
## Baseline / Before-After Rule
## Ownership Routing Rule
## Mandatory Reuse / DRY Constraints
## No Legacy / Forbidden Paths
## Reintroduction Guard
## Regression Guardrails
## Persistent Evidence Artifacts
## Allowlist / Exception Register
## Batch Migration Plan
## Expected Files to Modify
## Dependency Policy
## Validation Plan
## Regression Risks
## Dev Agent Instructions
## References
```

Operation Contract for a simple create API route must include these exact
markers without trailing periods in marker values:

```md
- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds a public API route with OpenAPI and JSON response contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `GET /health`.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the backend cannot expose a loaded app object.
```

Required Contracts table for a simple `GET /health` story:

```md
| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, and `TestClient` prove runtime API behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical ownership is required because backend files may be created. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical route. |
| Contract Shape | yes | The route has an exact status code and JSON response payload. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Forbidden alternate health paths must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |
```

Task lines must use `(AC: AC1)` or `(AC: AC1, AC2)` exactly. Do not write
`(AC1)` or `(AC1, AC2)`.

Persistent Evidence Artifacts must be a table with exactly these column names:

```md
| Artifact | Path | Purpose |
|---|---|---|
```

For generated story capsules, the separate review artifact path is always:

```md
| Review output | `_condamad/stories/<story>/generated/11-code-review.md` | Keep automatic review in a separate generated file. |
```

Do not use `review/00-review.md`, `review.md`, or a non-generated review path
for the automatic CONDAMAD review handoff.

When a contract is marked `no`, include its not-applicable section with a
`Reason:` line, for example:

```md
## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.
```

Runtime Source of Truth active snippet:

```md
- Primary source of truth:
  - `app.routes`, `app.openapi()`, and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for unauthorized route paths.
- Static scans alone are not sufficient for this story because:
  - Route registration and OpenAPI exposure must be proven from the loaded app.
```

Baseline / Before-After Rule active snippet:

```md
- Baseline artifact before implementation:
  - `_condamad/stories/<story>/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/<story>/evidence/openapi-after.json`
- Expected invariant:
  - The only intended API surface difference is `<path or field>`.
```

Ownership Routing Rule active snippet:

```md
| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| `<responsibility>` | `<canonical module/path>` | `<non-canonical path>` |
```

Use the table even when ownership is mostly unchanged, if the Required
Contracts table marks Ownership Routing as `yes`.

Contract Shape active snippet:

```md
- Contract type:
  - API route and OpenAPI path.
- Fields:
  - `<field>`: `<type/value rule>`
- Required fields:
  - `<field>`
- Optional fields:
  - none
- Status codes:
  - `200` for successful `<method> <path>`.
- Serialization names:
  - `<json key>` is emitted as `<json key>`.
- Frontend type impact:
  - none, unless a frontend generated client is in scope.
- Generated contract impact:
  - `app.openapi()` must expose `<path>` with method `<method>`.
```

Reintroduction Guard active snippet:

- List exact forbidden route paths, imports, or symbols.
- Require a deterministic `python`, `pytest`, or `rg` guard.

Persistent Evidence:

- List artifact paths for snapshots, validation output, review output, or
  mapping/register files.
- AC rows still need validator-safe command tokens; artifact paths alone are
  not enough.

Not-applicable contracts:

- Keep the contract heading and write one `Reason:` line.

## Missing App Roots

If the brief targets backend or frontend surfaces but the current workspace
lacks `backend`, `backend/app`, `backend/tests`, `frontend`, or `frontend/src`,
do not mark the story blocked solely for that absence.

Instead:

- add `Repository structure alert:` in Current State Evidence;
- state exactly which roots are absent;
- say the implementation must create the missing directories/files if the
  story remains in scope;
- list those paths in Files to Inspect First with an assumption-risk note;
- list them in Expected Files to Modify as implementation-created paths;
- keep validation commands targeted to the expected final paths.

## Guardrail Resolver

The registry is global. The story is local.

Never load, print, or restate the full guardrail registry. Build a scope vector
from:

- operation type;
- touched files and directories;
- route paths;
- contract types;
- domains;
- explicitly forbidden or out-of-scope surfaces.

Select guardrails in this order:

1. Exact route/path match.
2. Exact file or directory surface match.
3. Operation type match.
4. Contract type match.
5. Universal guardrails.

A guardrail is active only if it matches one of these dimensions. Mention at
most three non-applicable guardrails, only when they prevent scope drift.

Prefer the resolver command when available:

```powershell
python -B .agents\skills\condamad-story-writer\scripts\resolve_guardrails.py `
  --operation create `
  --domain backend-api `
  --path backend/app/api `
  --path backend/tests/api `
  --path /health `
  --contract openapi `
  --contract json-response
```

For health-route stories, always include `--path /health`. If the registry
contains `RG-053`, the resolver must return it for that scope.

In normal story generation, if `RG-053` or another exact route-specific
invariant is missing, do not read guardrail templates and do not update
`_condamad/stories/regression-guardrails.md`. Record the absence as
`Registry gap` or `Needs-investigation` in the story, then continue with the
existing registry selection. Registry enrichment is a separate mode and is
allowed only when the user explicitly asks for guardrail registry maintenance.

For a simple backend API route, usually select only:

- backend layout guardrail;
- API boundary guardrail;
- API contract guardrail;
- backend tests guardrail;
- local validation guardrail;
- no-legacy guardrail;
- exact route-specific guardrail when it exists.

Keep each Regression Guardrails table row under 160 characters. Do not put long
commands or long regexes in Regression Guardrails rows; use short evidence
labels and move full commands to the Validation Plan.

Compact guardrail row examples:

```md
| RG-002 `backend-layout` | Backend route files stay in canonical API paths. | `rg --files`; targeted `pytest`. |
| RG-007 `api-contracts` | Runtime API contract must prove `/health`. | `python` OpenAPI check; targeted `pytest`. |
```

## Validation Commands For Story Writing

For simple API stories, do not open `templates/story-template.md`. Use this
cheatsheet and the compact API blocks directly; open the full template only
when the story is a deletion, migration, broad architecture change, or a
validator diagnostic names a missing section not covered here.

Do not read `scripts/condamad_story_validate.py` or
`scripts/condamad_story_lint.py` before the first validation. If a validation
fails, fix from the printed diagnostics and this cheatsheet first. Inspect the
script source only for an unknown diagnostic.

Before the first validation run, make a single targeted text check of the
story draft:

- Reject any `...`, `<placeholder>`, `TODO`, or `TBD`; replace them with full
  concrete paths, commands, or wording before validation.
- Check AC Requirements for compound words such as `and` or comma-separated
  invariants. Split or shorten the Requirement so each AC states one invariant.
- For every AC Requirement containing `runtime`, keep a full test path or
  runtime command in the evidence cell.
- If `Allowlist Exception` is `no`, remove `exception`, `exceptions`, and
  `except` from Objective, Trigger / Source, Operation Contract, Acceptance
  Criteria, Validation Plan, and No Legacy / Forbidden Paths. Use `allowed
  delta`, `unchanged`, or `only allowed surface delta` instead.
- Remove strict-lint vague phrases before validation: `if needed`,
  `where relevant`, `as applicable`, `if absent`, `if present`, `as needed`,
  and `when needed`.
- Replace `implementation-created path if absent` with
  `implementation-created path` or `expected implementation-created path`.

For a normal story generation session, run only:

```powershell
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py <story>
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict <story>
```

Do not run the skill self-tests unless the skill implementation itself changed.

## Inventory Commands

Avoid broad inventory commands. Never scan build/cache directories.

If inventory is needed, use scoped commands such as:

```powershell
if (Test-Path backend) { rg --files backend --glob '!__pycache__/**' }
rg --files _condamad .agents --glob '!target/**' --glob '!node_modules/**' --glob '!.venv/**' --glob '!__pycache__/**'
```

Do not use unrestricted `rg --files` from the repository root.

## Output Discipline

- Do not print full file diffs.
- Do not paste full contents of large files.
- Report only modified paths, validator errors, and final status.
- Write the story once, validate, then perform at most one correction pass
  unless a distinct blocker appears.
- If you edit the story or tracker after a failed validation, rerun both
  validation commands before saying the story is `ready-to-dev`.
- If strict lint reports several diagnostics, fix the complete list in the same
  correction batch: every long line, placeholder, compound AC, and lint blocker
  must be resolved before ending the pass.
- Treat allowlist false positives and vague optional phrases as first-draft
  blockers, not validation-discovered issues.
- If the correction budget prevents a clean rerun, say the story is not proven
  green and record the blocker instead of claiming success.
- Strict lint treats line length, template placeholders, and compound ACs as
  blockers. Keep AC requirements short and single-invariant.
