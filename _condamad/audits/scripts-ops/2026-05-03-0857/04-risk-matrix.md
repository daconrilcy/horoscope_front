# Risk Matrix - scripts-ops

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Local Stripe webhook development docs and scripts | Medium: future edits may keep dual shell parity accidentally instead of by policy | Low | P1 user decision |
| F-002 | Info | Low | Future root script additions | Low: exact registry coverage and tests already protect it | Low | monitor |
| F-003 | Info | Low | Historical route-removal story evidence only | Low: root file is absent and guarded | Low | monitor |
| F-004 | Info | Low | Local developer startup | Low: optional Stripe behavior is documented and guarded | Low | monitor |
| F-005 | Info | Low | LLM release readiness portability | Low: repo-relative cache is guarded | Low | monitor |
| F-006 | Info | Low | Performance/load validation | Low: scenario grouping and destructive opt-in are guarded | Low | monitor |
| F-007 | Info | Low | Dev-only natal diagnostics | Low: CI refusal and import boundaries are guarded | Low | monitor |

## Top Risks

1. `F-001` is the only unresolved operational decision. It does not currently break tests, but it leaves support policy ambiguous for a non-Windows script in a Windows / PowerShell-targeted repository.
2. Future scripts should continue to enter through `scripts/ownership-index.md`; otherwise `RG-023` should fail before the drift becomes silent.
3. Future local stack changes must preserve the `-WithStripe` opt-in contract protected by `RG-024`.
