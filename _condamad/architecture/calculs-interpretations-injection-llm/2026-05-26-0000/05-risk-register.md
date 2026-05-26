# Risk Register

| Risk | Type | Severity | Probability | Mitigation | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| `chart_json` remains de facto source of truth after architecture decision | product/technical | high | high | declare `llm_astrology_input_v1`, confine `chart_json` to transition-condition, add scans/tests | architecture owner + LLM runtime owner | CS-324 F-001/F-002; CS-327 F-001 |
| `client_interpretation_projection_v1` is mistaken for factual prompt input | product | high | medium | keep B2C projection as shaping-only; facts come from `structured_facts_v1` | product projection owner | CS-326 F-002 |
| prompt runtime becomes hidden astrology source | technical | high | medium | guard prompt-visible/runtime-only fields; no prompt copy change in migration stories | LLM configuration owner | CS-325 F-002; CS-327 F-003 |
| narrative audit stores hashes that do not match future LLM input | auditability | high | medium | define `llm_input_hash` over all target injection blocks | observability/data owner | CS-326 F-003 |
| `evidence_catalog` role remains ambiguous | auditability | medium | high | owner decision: refs visible, detailed catalog validation/audit-only | observability owner | CS-325 F-003; CS-324 F-003 |
| duplicate `chart_json` / `natal_data` drifts | technical | medium | high | remove or classify one as compatibility after target mapping | backend LLM owner | CS-324 F-002; CS-327 F-002 |
| legacy branches break unexpectedly | product | medium | medium | branch register before removal | product owner | CS-325 F-004 |
| raw runtime objects leak into prompt/provider/public payloads | security/product | high | low | negative scan and tests for `ChartObjectRuntimeData` in prompt/provider surfaces | architecture owner | CS-324 E-005; CS-245 |

## Risk Decisions

- decision: highest implementation risk is sequencing. Registry/schema and hash/evidence rules must precede prompt/runtime changes.
- blocker: unresolved product compatibility must remain visible until `/users`, `free_short`, schema and fallback branches are classified.
- open question: the detailed privacy/retention policy for persisted raw LLM input payload is not decided here; default is hash/audit metadata only unless data owner approves storage.
