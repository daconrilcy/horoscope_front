# Evidence Map

This file maps audit evidence to CS-328 architecture decisions. The audits are treated as source of truth; this file does not redo them.

| Decision | Evidence status | Source audits / findings | Evidence IDs | Story candidates | Result |
| --- | --- | --- | --- | --- | --- |
| Use `AINarrativeInputContract` as canonical internal LLM input owner | observed + decision | CS-326 F-001; CS-324 F-001; CS-325 F-001 | CS-326 E-009/E-010/E-016/E-020; CS-324 E-008/E-009/E-016; CS-325 E-019 | CS-326 SC-001; CS-324 SC-001; CS-325 SC-001 | decision: target owner, with implementation gated by schema story |
| Create `llm_astrology_input_v1` as LLM schema-facing wrapper | inferred + decision | CS-327 F-001/F-003; CS-326 F-001 | CS-327 E-013/E-017/E-019/E-020/E-023; CS-326 E-009/E-020 | CS-327 SC-001/SC-003 | decision: wrapper needed because LLM config currently has no modern structured schema |
| Keep `structured_facts_v1` as facts block source | observed + decision | CS-326 F-002; CS-324 F-003 | CS-326 E-006/E-017; CS-324 E-010/E-012/E-013 | CS-326 SC-002; CS-324 SC-003 | decision: fact source, not complete prompt contract |
| Prevent `client_interpretation_projection_v1` from becoming factual prompt source | observed + decision | CS-326 F-002 | CS-326 E-008/E-019; brief CS-258; brief CS-287 | CS-326 SC-002 | decision: B2C shaping only |
| Treat `narrative_answer_audit_v1` as audit-only | observed + decision | CS-326 F-003 | CS-326 E-011/E-012/E-013/E-015/E-021/E-022; brief CS-259 | none direct | decision: audit storage, not injection context |
| Confine `chart_json` and `natal_data` | observed + decision | CS-324 F-002; CS-327 F-002; CS-325 F-001 | CS-324 E-012/E-013/E-014; CS-327 E-012/E-016; CS-325 E-006/E-008/E-013 | CS-324 SC-002; CS-327 SC-002 | decision: transition-condition compatibility only |
| Keep prompt runtime from becoming source of truth | observed + decision | CS-325 F-002; CS-327 F-003 | CS-325 E-010/E-011/E-023; CS-327 E-014/E-017/E-023 | CS-325 SC-002; CS-327 SC-003 | decision: prompt-visible/runtime-only guard required |
| Decide role of `evidence_catalog` and `evidence_refs` | blocker | CS-325 F-003; CS-324 F-003; CS-326 F-003 | CS-325 E-008/E-011/E-017; CS-324 E-010/E-012/E-013; CS-326 E-011/E-012/E-013 | CS-325 SC-003; CS-324 SC-003 | blocker: owner decision required |
| Classify `/users`, `free_short`, schemas and fallbacks | blocker | CS-325 F-004; CS-327 F-004 | CS-325 E-003/E-005/E-006/E-020/E-024/E-025; CS-327 E-007/E-008/E-021/E-022 | CS-325 SC-004 | blocker: product compatibility decision required |

## Source Brief Alignment

| Brief | Architecture use | Cited decision |
| --- | --- | --- |
| `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md` | Runtime calculation boundary | `CalculationGraph` and `ChartObjectRuntimeData` feed interpretation but are not raw prompt/public payload |
| `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` | AI/narrative contract shape | facts, signals, readiness flags, source versions, masking policy and projection links are separate from prompt output |
| `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md` | Hashable fact source | `structured_facts_v1` owns stable non-narrative facts and `projection_hash` material |
| `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md` | B2C shaping boundary | client projection differs by plan but must not expose runtime technical facts |
| `_story_briefs/cs-259-define-narrative-answer-audit-v1.md` | Audit trace | `projection_hash`, `llm_input_hash`, `prompt_version`, provider/model and `evidence_refs` are required audit metadata |
| `_story_briefs/cs-287-implement-client-interpretation-projection-v1-builder-by-plan.md` | Implemented projection context | builder prepares plan sections, not provider narrative |
| `_story_briefs/cs-291-implement-generic-projection-endpoint.md` | Public endpoint boundary | public projection endpoint must refuse internal surfaces |

## Missing Evidence

No required audit folder is missing. Implementation evidence remains intentionally absent because CS-328 forbids application changes.
