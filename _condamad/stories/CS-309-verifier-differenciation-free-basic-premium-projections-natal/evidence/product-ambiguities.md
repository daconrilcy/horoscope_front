# Product ambiguity ledger - CS-309

audit_date: 2026-05-26
route: /natal

| topic | status | decision |
|---|---|---|
| Exact commercial boundary between free, basic, and premium projection access | documented limitation | The UI does not encode plan entitlement policy. The visible matrix is QA evidence only and follows backend success or 403 responses. |
| Subscription destination for projection upgrade states | resolved | Reuse the existing supported `/settings/subscription` path. |
| Partial success plus 403 rendering | resolved | Keep authorized projection content visible and show a locked upgrade state for the refused projection. |
