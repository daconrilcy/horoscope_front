# Static guards - CS-309

audit_date: 2026-05-26

| Guard | Command | Result | Evidence |
|---|---|---|---|
| Hardcoded entitlement matrix | `rg -n "free.*basic.*premium\|basic.*premium\|plan_code.*===" frontend/src/features/natal-chart frontend/src/components/natal-interpretation` | PASS_WITH_REVIEW | One hit in `NatalInterpretation.tsx` dependency array for upgrade path variable names; no plan policy table or `plan_code ===` branch. |
| Direct projection HTTP bypass | `rg -n "fetch\\(.*/v1/astrology/projections\|axios\\(.*/v1/astrology/projections" frontend/src` | PASS | Exit 1 means no matches. Projection calls remain in the API client. |
| Inline style guard | `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation -g "*.tsx"` | PASS | Exit 1 means no matches. |
| Diff hygiene | `git diff --check` | PASS | Only line-ending warnings from Git autocrlf, no whitespace errors. |
