# No Legacy / DRY Guardrails

## Canonical Ownership

- Critical load scenario classification lives only in `scripts/load-test-critical.ps1`.
- Scenario definitions must be grouped through one manifest/source of truth, not parallel ad hoc lists.
- `privacy_delete_request` is allowed only as an explicitly selected destructive privacy scenario.

## Forbidden Patterns

- `Story 66.35`
- `Legacy critical scenarios`
- `privacy_delete_request` in the default selected groups
- Compatibility wrappers, aliases, duplicate active scenario lists, or silent fallback to destructive scenarios.

## Required Negative Evidence

- `pytest -q app/tests/unit/test_load_test_critical_script.py`
- `rg -n "Story 66\\.35|Legacy critical scenarios" scripts/load-test-critical.ps1`
- `rg -n "privacy_delete_request" scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py` with classified hits.
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py`

## Allowlist Exception

| Symbol | Allowed location | Reason | Guard |
|---|---|---|---|
| `privacy_delete_request` | `destructive-privacy` scenario group and tests that assert the boundary | Required scenario remains available by explicit selection. | `test_default_groups_exclude_privacy_delete_request` |

## Review Checklist

- Default group selection is non-destructive.
- Existing non-destructive scenarios remain listed in explicit groups.
- JSON and Markdown report generation still uses the existing report path.
- New tests are registered for `RG-015` ownership.
