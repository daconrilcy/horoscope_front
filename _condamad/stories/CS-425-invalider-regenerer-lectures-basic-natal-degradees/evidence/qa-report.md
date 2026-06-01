# QA Report - CS-425

- Compatible Basic cache: served without gateway call when schema, engine and `basic_editorial_contract_version` match.
- Missing/old editorial version: classified as incompatible and regenerated when corrective generation is eligible.
- Degraded baseline tokens: detected centrally through `BASIC_NATAL_DEGRADED_BASELINE_TOKENS` and rejected for cache reuse.
- Non-regenerable state: rejected/degraded rows remain hidden from public list/get; exhausted quota keeps the controlled `natal_chart_long_quota_exceeded` path.
- No batch migration path was added; this story only changes runtime compatibility and tests.
