# CONDAMAD Domain Auditor Workflow

<!-- Workflow operationnel read-only pour auditer un domaine applicatif borne. -->

## Step 1 - Resolve Audit Target

Determine:

- domain target;
- audit archetype;
- output folder;
- read-only mode.

Default the output folder to
`_condamad/audits/<domain-key>/<YYYY-MM-DD-HHMM>/` when no explicit output
location is provided by the user, story brief, or governing task contract. If
an explicit deliverable path is provided, produce the requested audit artifact
there and keep any optional CONDAMAD companion report under `_condamad/audits/**`.

If the request is too broad, such as "Audit the backend", ask the user to select one bounded domain:

- `backend/app/api`
- `backend/app/domain`
- `backend/app/services`
- `auth`
- `entitlement`
- `infra/db`

## Step 2 - Load Applicable Contracts

Read the minimal routing set first:

- `references/audit-principles.md`
- `references/audit-archetypes.md`
- `references/report-output-contract.md`

Then select the archetype and load only the references needed by that archetype
and the current diagnostic:

- `references/finding-taxonomy.md`
- `references/evidence-profiles.md`
- `references/story-candidate-contract.md`
- the domain-specific contract matching the selected archetype.
- `../condamad-dev-story/references/condamad-principles.md` when No Legacy,
  DRY, closure, or story-candidate implementation rules are involved.
- `../condamad-regression-guardrails/SKILL.md` only before creating or updating
  guardrails.

## Step 2a - Load Prior Domain History

For the same domain key, inspect the latest audit folder and the stories
directly generated from its candidates. Build a short closure ledger:

- prior findings still active under current evidence;
- prior findings closed by implementation and guardrails;
- findings superseded by a newer, narrower finding;
- issues that belong to a different domain;
- user-decision blockers.

Do not rely on the previous audit's status text alone. Confirm closure with
current files, guards, tests, or scans when feasible. Inspect older same-domain
audits only when the latest audit references an active finding, unresolved
closure map, superseded finding, or explicit blocker that cannot be understood
from the latest folder and linked stories.

## Step 3 - Evidence Planning

Define:

- files to inspect;
- file/export/surface inventory to classify;
- commands to run;
- runtime evidence if applicable;
- static scans;
- forbidden dependency patterns;
- No Legacy scans;
- security or policy checks for auth and entitlement.
- closure evidence needed to prove whether each prior finding is fully closed.
- evidence required to classify each audited surface as `used`,
  `intentional-public-export`, `test-only`, `delete-candidate`,
  `needs-user-decision`, or `out-of-domain`.

## Step 4 - Execute Read-Only Evidence Collection

Allowed by default:

- `rg`;
- `git status`;
- `git grep`;
- read-only Python scripts;
- targeted non-mutating tests;
- check-only lint or typecheck commands.

Forbidden unless explicitly requested:

- formatters;
- migrations;
- generators;
- dependency install/update;
- destructive git commands;
- application code edits.

## Step 5 - Classify Findings

Each finding must include:

- ID;
- severity;
- confidence;
- category;
- domain;
- evidence;
- expected rule;
- actual state;
- impact;
- recommended action;
- story candidate decision.

For every implementation finding, also decide whether it is:

- `closure-ready`: one candidate can close the finding fully;
- `phased-with-map`: several bounded slices are justified, and the audit gives
  the complete remaining surface plus stop condition;
- `blocked`: user/product/technical decision is required before implementation;
- `non-domain`: defer to another domain without emitting an implementation
  candidate here.

Avoid vague follow-up language such as "next cluster" unless the complete
remaining cluster map and finish line are documented in the same audit.

## Step 5a - Classify File And Surface Usage

For every audited file, export, route, component, service, test helper, or
bounded surface, assign exactly one classification:

- `used`: current application, configuration, runtime registration, or
  in-domain tests use it;
- `intentional-public-export`: kept as a deliberate public API even if no
  in-repository inbound usage exists;
- `test-only`: owned by tests, fixtures, guards, or audit tooling;
- `delete-candidate`: no current owner remains and deletion can be proposed
  with a canonical replacement or explicit no-owner rationale;
- `needs-user-decision`: repository evidence cannot decide keep/remove/export;
- `out-of-domain`: inspected only to bound the audit.

Classification evidence rules:

- Use direct evidence IDs, not prose-only conclusions.
- Pair negative usage scans with ownership checks before using
  `delete-candidate`.
- Treat ambiguous public exports as `needs-user-decision` unless source-backed
  public intent exists.
- Keep test-only files separate from application files in closure and story
  candidate surfaces.

## Step 6 - Generate Reports

When no explicit audit deliverable path is provided, create the standard report
set:

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`

When the user, story brief, or governing task contract names an explicit audit
deliverable path, write only the requested audit artifact(s) there and keep any
optional CONDAMAD companion report under `_condamad/audits/**`.

The report set must include:

- a domain closure status;
- prior audit/story history consulted;
- file usage classification for every audited file or surface;
- exhaustive files or surfaces to modify for every active implementation
  finding;
- explicit "none" entries when no application or governance file remains;
- deferred non-domain context separated from audited-domain findings.

## Step 7 - Validate Reports

Run from the repository root after verifying and activating the virtual
environment:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder>
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py <audit_folder>
```

For a human-readable summary:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder> --explain-audit
```

Run the human-readable summary only when validation fails, the result needs
diagnostic explanation, or the current request explicitly asks for it.

Official package self-validation command:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_self_validate.py
```

Use direct `python -S -B -m unittest discover ...` only as a diagnostic command when the wrapper reports a failure:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B -m unittest discover -s .agents/skills/condamad-domain-auditor/scripts/self_tests -p "*selftest.py" -v
```

Run the wrapper smoke test before packaging or releasing the skill:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
python -S -B .agents/skills/condamad-domain-auditor/scripts/self_tests/condamad_domain_audit_wrapper_smoke.py
```

## Step 8 - Final Response

Respond with:

- audit folder path;
- summary of findings by severity;
- top risks;
- story candidates count;
- recommended next action;
- validation status.
