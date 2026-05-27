# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Dedicated document exists. | `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` created. | `evidence/validation.txt` VC1 PASS; `evidence/docs-baseline.txt` and `evidence/docs-after.txt`. | PASS |
| AC2 | All mandatory sections are present. | The document contains the 15 required `##` sections from `00-story.md`. | `evidence/validation.txt` VC2 rerun PASS. Initial VC2 failed only because the PowerShell command escaped the apostrophe incorrectly. | PASS |
| AC3 | Each plan has a clear section. | Plan matrices cover `free`, `basic`, `premium` in injected data and differences sections. | `evidence/validation.txt` VC3 PASS. | PASS |
| AC4 | The prompt journey is complete. | Sections cover service input, `llm_astrology_input_v1`, assembly, renderer, messages, provider boundary, repair and rejection. | `evidence/validation.txt` VC3b, VC4, VC6 PASS. | PASS |
| AC5 | Injected data is classified. | Matrix classifies `facts`, `signals`, `limits`, `shaping`, `evidence`, `provenance`. | `evidence/validation.txt` VC3a, VC4, VC5 PASS. | PASS |
| AC6 | Persona assembly is explained. | Persona section cites `resolve_assembly`, `compose_persona_block`, `assemble_developer_prompt`, `compose_structured_messages`. | `evidence/validation.txt` VC3, VC6 PASS. | PASS |
| AC7 | Safety controls are separated. | Safety section separates hard policy, non-invention, validation, repair and rejection. | `evidence/validation.txt` VC3, VC5 PASS. | PASS |
| AC8 | Prompt exclusions are explicit. | Document excludes `evidence`, `provenance`, hashes, provider response, observability, `chart_json`, `natal_data` from modern natal prompt visibility. | `evidence/validation.txt` VC4, VC5 PASS. | PASS |
| AC9 | Important claims cite sources. | Document cites CS-350, CS-343 to CS-347 audits, CS-320/CS-330/CS-335, CS-330 to CS-342 stories and backend owner paths. | `evidence/source-coverage.md`; `evidence/validation.txt` VC3b, VC6 PASS. | PASS |
| AC10 | No real LLM call is claimed. | Executive summary and verification section state no provider LLM call was performed. | `evidence/validation.txt` VC3b and VC5 content scans; manual review recorded in final evidence. | PASS |
| AC11 | Application code remains unchanged. | No backend/app, backend/tests or frontend/src file was edited. | `evidence/validation.txt` VC8 PASS; `evidence/docs-after.txt` bounded status. | PASS |
| AC12 | Persistent evidence is stored. | Evidence directory contains baseline, after scan, guardrails, source coverage and validation output. | `evidence/validation.txt` VC7 PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
