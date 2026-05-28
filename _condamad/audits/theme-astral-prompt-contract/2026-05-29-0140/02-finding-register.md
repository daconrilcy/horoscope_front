# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | runtime-contract-drift | theme-astral-prompt-contract | E-011, E-013 | Official example payloads can mislead implementers and reviewers into accepting a `birth_context` that is structurally present but semantically empty and still dependent on `chart_id` for the actual Paris scenario. | Regenerate or correct the target provider examples so structured birth fields carry the scenario values, and add validation that fails if `chart_id` is the only carrier of birth date, time, place, timezone, or coordinates. | yes |
| F-002 | Info | High | observability-gap | theme-astral-prompt-contract | E-010, E-013 | The audit proves local builder, schema, tests and smoke gating, but not real provider acceptance. | Keep as accepted risk unless product explicitly opts in to a credentialed provider smoke run. | no |
| F-003 | Info | High | runtime-contract-drift | theme-astral-prompt-contract | E-012 | Some interpretation material remains fixture-backed, but the source nature is explicitly disclosed and the payloads contain sourced non-empty material. | Accept current disclosure; future product work may add dedicated DB tables for fixture-owned families. | no |

## F-001 Example Payloads Keep Birth Context Empty

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: theme-astral-prompt-contract
- Evidence: E-011, E-013
- Expected rule: Final `theme_astral` provider examples for `1973-04-24 11:00 Paris France` must expose structured `input_data.birth_context` values and must not rely on `chart_id` as the only carrier of date, time, place, timezone, or coordinates.
- Actual state: `free-provider-payload.json`, `basic-provider-payload.json`, and `premium-provider-payload.json` all include `chart_id` with the scenario, but `birth_date`, `birth_time_local`, `birth_place.city`, `birth_place.country`, `birth_place.timezone`, `birth_place.latitude`, and `birth_place.longitude` are null.
- Impact: Official example payloads can mislead implementers and reviewers into accepting a `birth_context` that is structurally present but semantically empty and still dependent on `chart_id` for the actual Paris scenario.
- Recommended action: Regenerate or correct the target provider examples so structured birth fields carry the scenario values, and add validation that fails if `chart_id` is the only carrier of birth date, time, place, timezone, or coordinates.
- Story candidate: yes
- Suggested archetype: contract-shape-audit

## F-002 Provider Smoke External Call Not Executed

- Severity: Info
- Confidence: High
- Category: observability-gap
- Domain: theme-astral-prompt-contract
- Evidence: E-010, E-013
- Expected rule: The audit must explicitly state whether CS-376 provider smoke ran, skipped by missing opt-in, or was not implemented.
- Actual state: CS-376 smoke exists and is registered, but the provider-marked run skips without explicit external-call prerequisites.
- Impact: The audit proves local builder, schema, tests and smoke gating, but not real provider acceptance.
- Recommended action: Keep as accepted risk unless product explicitly opts in to a credentialed provider smoke run.
- Story candidate: no
- Suggested archetype: observability-audit

## F-003 Example Source Material Is Mixed But Disclosed

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: theme-astral-prompt-contract
- Evidence: E-012
- Expected rule: Examples should use representative sourced interpretive material or clearly warn when production-like fixtures remain.
- Actual state: Provider payloads contain non-empty `interpretive_text` with `source_ref`; README states that planet, house and aspect families are DB-seeded production-like profiles while other families are explicit `theme_astral_production_like_fixture` material.
- Impact: Some interpretation material remains fixture-backed, but the source nature is explicitly disclosed and the payloads contain sourced non-empty material.
- Recommended action: Accept current disclosure; future product work may add dedicated DB tables for fixture-owned families.
- Story candidate: no
- Suggested archetype: contract-shape-audit
