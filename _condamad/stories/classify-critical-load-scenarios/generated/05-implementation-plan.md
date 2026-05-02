# Implementation Plan

## Findings

- `scripts/load-test-critical.ps1` used direct scenario calls and active comments carrying audited story/legacy labels.
- `privacy_delete_request` was executed with the default script path.
- `scripts/load-test-critical-matrix.ps1` delegates to the script without passing scenario selection, so default selection must stay non-destructive.
- `RG-015` applies because the new backend test name is script-related and must be registered in the quality ownership registry.

## Selected Approach

- Add a single PowerShell manifest function `Get-CriticalLoadScenarioManifest`.
- Add `-ScenarioGroups` with default `smoke`, `llm`, `b2b`.
- Keep `destructive-privacy` and `stress-incidents` available only by explicit group selection.
- Preserve report generation and B2B skip behavior through the existing report fields.

## Files To Modify

- `scripts/load-test-critical.ps1`
- `backend/app/tests/unit/test_load_test_critical_script.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `_condamad/stories/classify-critical-load-scenarios/*`

## Tests

- Static pytest guard parses the PowerShell manifest and default groups.
- Ownership guard validates `RG-015`.
- PowerShell parser validates script syntax without calling backend endpoints.

## No Legacy Stance

- No compatibility wrapper or alias is introduced.
- Old story-numbered and legacy labels are removed from active script comments.
- The destructive privacy scenario is retained only as an explicit allowlisted group.

## Rollback

- Revert the manifest change and test/ownership rows together if review rejects the grouping contract.
