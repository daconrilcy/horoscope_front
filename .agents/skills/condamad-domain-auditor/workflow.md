# CONDAMAD Domain Auditor Workflow

<!-- Workflow operationnel read-only pour auditer un domaine applicatif borne. -->

## Step 1 - Resolve Audit Target

Determine:

- domain target;
- audit archetype;
- output folder;
- read-only mode.

If the request is too broad, such as "Audit the backend", ask the user to select one bounded domain:

- `backend/app/api`
- `backend/app/domain`
- `backend/app/services`
- `auth`
- `entitlement`
- `infra/db`

## Step 2 - Load Applicable Contracts

Read:

- `references/audit-principles.md`
- `references/audit-archetypes.md`
- `references/finding-taxonomy.md`
- `references/evidence-profiles.md`
- `references/report-output-contract.md`
- `references/story-candidate-contract.md`
- the domain-specific contract matching the selected archetype.

## Step 2a - Load Prior Domain History

For the same domain key, inspect the latest relevant audit folders and the
stories generated from their candidates. Build a short closure ledger:

- prior findings still active under current evidence;
- prior findings closed by implementation and guardrails;
- findings superseded by a newer, narrower finding;
- issues that belong to a different domain;
- user-decision blockers.

Do not rely on the previous audit's status text alone. Confirm closure with
current files, guards, tests, or scans when feasible.

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

Create:

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`

The report set must include:

- a domain closure status;
- prior audit/story history consulted;
- file usage classification for every audited file or surface;
- exhaustive files or surfaces to modify for every active implementation
  finding;
- explicit "none" entries when no application or governance file remains;
- deferred non-domain context separated from audited-domain findings.

## Step 7 - Validate Reports

Run:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder>
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py <audit_folder>
```

For a human-readable summary:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py <audit_folder> --explain-audit
```

Official package self-validation command:

```bash
python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_self_validate.py
```

Use direct `python -S -B -m unittest discover ...` only as a diagnostic command when the wrapper reports a failure:

```bash
python -S -B -m unittest discover -s .agents/skills/condamad-domain-auditor/scripts/self_tests -p "*selftest.py" -v
```

Run the wrapper smoke test before packaging or releasing the skill:

```bash
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
