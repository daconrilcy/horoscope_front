# Executive Summary - Astro Runtime Surface Exposure

## Conclusion

The current implementation correctly keeps raw runtime surfaces internal. `chart_objects`, `ChartObjectRuntimeData` and `advanced_planetary_conditions` are excluded from public schema/payload evidence, while runtime graph nodes and tests prove they are active internal sources.

## Decisions

- Public: expose only controlled projections. Priority is `chart_facts`, then a reduced fixed-star contact projection.
- Internal: keep raw `chart_objects`, `ChartObjectRuntimeData`, full advanced condition objects, runtime payloads and graph internals non-public.
- Interpretation/LLM: keep `interpretation_input`, aspect hints, sign profiles, condition profiles, fixed-star contacts, dignity and dominance details as interpretation inputs unless a later product story selects a public subset.
- Admin/debug: useful but blocked until a protected access model is selected.
- Deferred: frontend UI, API route creation, auth/admin design and serializer implementation are outside this audit.

## Findings By Severity

- High: 1 finding, raw `chart_objects` exposure pressure must be handled through a controlled projection.
- Medium: 2 findings, fixed-star public projection and protected graph trace decisions.
- Low: 1 finding, exact guardrail vocabulary gap.
- Info: 1 observation, secondary payload granularity needs product selection.

## Next Story Ranking

1. CS-237 / SC-001: define public `chart_facts` projection contract.
2. CS-238 / SC-002: expose fixed-star contacts through a stable public projection.
3. CS-239 / SC-003: add protected admin/debug graph trace only after an authorization decision.

## Validation Summary

Targeted source scans, architecture docs, public contract tests and domain tests support the recommendations. No application code change is part of the audit deliverable.
