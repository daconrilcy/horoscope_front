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

## Step 3 - Evidence Planning

Define:

- files to inspect;
- commands to run;
- runtime evidence if applicable;
- static scans;
- forbidden dependency patterns;
- No Legacy scans;
- security or policy checks for auth and entitlement.

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

## Step 6 - Generate Reports

Create:

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`

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
