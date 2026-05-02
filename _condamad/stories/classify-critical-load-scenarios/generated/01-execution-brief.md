# Execution Brief

- Story key: `classify-critical-load-scenarios`
- Objective: classify scenarios in `scripts/load-test-critical.ps1` into explicit groups and remove destructive privacy delete from the default selection.
- Boundaries: modify only the critical load script, targeted pytest guard, CONDAMAD evidence files, and ownership registry if required by `RG-015`.
- Non-goals: no API endpoint changes, no new functional scenarios, no frontend changes, no dependency changes, no matrix behavior change beyond the preserved script contract.
- Preflight checks: read `AGENTS.md`, story source, regression guardrails, target scripts, current ownership registries, and current script scenario inventory.
- Write rules: keep one manifest/source of truth for scenarios, do not add compatibility aliases or parallel lists, keep JSON and Markdown report generation through the existing code path.
- Done conditions: all ACs have code and validation evidence, targeted pytest guard passes, forbidden marker scan is clean, story validators pass or limitations are recorded, final evidence is complete.
- Halt conditions: user decision is required if `privacy_delete_request` must remain in the default smoke path or if endpoint changes become necessary.
