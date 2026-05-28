# Story Candidates

No remediation story candidate is emitted for the audited implementation domain.

## Candidate Decisions

| Finding | Decision | Reason |
|---|---|---|
| F-001 | no | Provider invocation is outside the user-authorized audit scope and outside the original story non-goal. The implementation-facing contract is already covered by source, runtime tests, persistence tests, examples, and scans. |

## Exhaustive Files To Modify

None. No application, migration, seed, test, frontend, example, architecture, story, or guardrail file is recommended for modification by this audit.

## Deferred Non-Domain Context

- Real LLM provider quality/eval behavior is deferred non-domain context. It would require a separate provider smoke/evaluation story and credentials/environment decisions.
- Broad `chart_json`, `natal_data`, `legacy`, `free`, `basic`, and `premium` hits in non-theme natal/admin/test/billing/evaluation flows are out of this audit domain. They must not be treated as active `theme_astral` carriers without new evidence.

## Guardrail Recommendation

No `_condamad/stories/regression-guardrails.md` update is made. Current guardrails plus targeted tests already protect the durable invariant: `theme_astral` provider handoff requires `theme_astral_llm_input_v1`, keeps commercial labels backend-only, and rejects old carriers.
