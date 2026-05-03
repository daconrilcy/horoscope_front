# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Bash listener removal follows `removal-audit.md` classification. | Deleted `scripts/stripe-listen-webhook.sh`; added removal audit. | `removal-audit.md`; `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` no hit. | PASS |
| AC2 | `scripts/ownership-index.md` covers root scripts without the Bash row. | Removed Bash row and stale decision value; kept exact inventory coverage. | Targeted pytest passed; `rg --files scripts` excludes Bash listener. | PASS |
| AC3 | The local Stripe runbook states dev-only Windows / PowerShell support. | Updated `docs/billing-webhook-local-testing.md`; test forbids Bash/Git Bash/WSL support. | Targeted pytest passed; active docs/scripts/tests scan has no forbidden hit. | PASS |
| AC4 | PowerShell listener command remains canonical local target. | Kept `.ps1` event list and forward target; test asserts Bash absence. | Targeted pytest passed; `scripts/stripe-listen-webhook.ps1` remains in inventory. | PASS |
| AC5 | `start-dev-stack.ps1 -WithStripe` targets PowerShell. | Tightened `test_start_dev_stack_script.py` to assert `.ps1` and reject `.sh`. | Targeted pytest passed. | PASS |
| AC6 | Persistent after-scan proves no compatibility path remains. | Added `reference-baseline.txt`, `reference-after.txt`, and final evidence. | Same before/after scan persisted; final negative scan no hit. | PASS |
