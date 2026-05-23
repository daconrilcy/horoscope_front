# Evidence Profiles

Evidence profiles define acceptable proof for audit findings. Each evidence entry should include command/source, repository-relative inspected path, inspected symbol or surface, result, and limitation when relevant.

## Evidence clarity rules

- Prefer commands and source references that another auditor can rerun or reopen.
- State whether the evidence proves presence, absence, classification, closure,
  or limitation.
- For negative scans, include the exact searched target, excluded paths, and
  why those exclusions are valid for the audited domain.
- For source inspection, include the file path and the symbol, route, export,
  selector, setting, or contract being inspected.
- For runtime evidence, include the command, environment assumption, observed
  output, and any skipped runtime path.
- Do not use vague notes such as "looks unused", "seems covered", "probably
  legacy", or "no issue found" without the concrete proof that supports the
  conclusion.

## Evidence profile: file_usage_classification

Required evidence:

- complete audited file or surface inventory;
- inbound usage scan or structural owner evidence for each classified item;
- export, route, configuration, migration, packaging, or framework registration
  evidence when relevant;
- test ownership evidence for `test-only` classifications;
- explicit negative usage scan plus non-public-export proof for
  `delete-candidate` classifications;
- blocker or decision statement for `needs-user-decision` classifications.

Valid classification values:

- `used`: directly used by application, configuration, runtime registration, or
  tests relevant to the audited domain;
- `intentional-public-export`: intentionally exposed even if no in-repository
  inbound usage exists;
- `test-only`: exists only to support tests, fixtures, guards, or audit tooling;
- `delete-candidate`: appears removable under current evidence and has a known
  canonical replacement or no remaining owner;
- `needs-user-decision`: repository evidence cannot determine whether to keep,
  expose, rewrite, or remove it;
- `out-of-domain`: inspected only to bound the audit and belongs elsewhere.

## Evidence profile: repo_wide_negative_scan

Required evidence:

- command proving forbidden symbols are absent or present;
- explicit repository root;
- known exclusions.

## Evidence profile: targeted_forbidden_symbol_scan

Required evidence:

- target path;
- forbidden symbols;
- file:line hits or PASS result.

## Evidence profile: dependency_direction_scan

Required evidence:

- command scanning forbidden imports;
- inspected source path;
- expected dependency direction;
- findings classified as valid violation or justified exception.

Acceptable commands:

```bash
rg -n "from app.api|import app.api" backend/app/services backend/app/domain
rg -n "fastapi|HTTPException|JSONResponse" backend/app/domain backend/app/services
```

## Evidence profile: runtime_openapi_contract

Required evidence:

- runtime OpenAPI source or explicit reason it was skipped;
- route or schema excerpts;
- comparison against router/source expectations.

## Evidence profile: route_table_inventory

Required evidence:

- route table command or source inventory;
- included router ownership;
- duplicate or legacy route notes.

## Evidence profile: python_import_boundary_scan

Required evidence:

- import scan command;
- affected layer;
- expected allowed import direction.

## Evidence profile: ast_dependency_guard

Required evidence:

- AST or parser-based guard command;
- forbidden imports/symbols;
- pass/fail result.

## Evidence profile: test_coverage_inventory

Required evidence:

- tests inspected;
- covered behavior;
- missing negative paths.

## Evidence profile: architecture_guard_inventory

Required evidence:

- guard tests or scripts inspected;
- forbidden dependency or symbol guarded;
- reintroduction risk if absent.

## Evidence profile: auth_security_control_check

Required evidence:

- auth entrypoint or dependency;
- unauthorized and forbidden behavior;
- secret/token/session handling;
- mapped OWASP ASVS control area where applicable.

## Evidence profile: entitlement_policy_flow_trace

Required evidence:

- canonical policy owner;
- policy decision path;
- mutation path;
- bypass scan result.

## Evidence profile: mutation_audit_trail_check

Required evidence:

- mutation entrypoints;
- audit trail writes;
- state transition proof;
- missing event risk.

## Evidence profile: observability_signal_check

Required evidence:

- log/metric/trace/audit signal source;
- error path or mutation path;
- signal absence or adequacy.
