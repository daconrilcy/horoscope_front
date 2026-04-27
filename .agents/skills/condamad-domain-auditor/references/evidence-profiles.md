# Evidence Profiles

Evidence profiles define acceptable proof for audit findings. Each evidence entry should include command/source, inspected path, result, and limitation when relevant.

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
