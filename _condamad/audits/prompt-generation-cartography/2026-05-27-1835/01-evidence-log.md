<!-- Commentaire global: journal de preuves reproductibles pour l'audit CS-346. -->

# Evidence Log

| ID | Evidence type | Command / Source | Inspected path or surface | Result | Notes |
|---|---|---|---|---|---|
| E-001 | story-source | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md` | CS-346 scope and ACs | PASS | Story confirms audit-only delivery. |
| E-002 | prior-history | `Get-ChildItem -LiteralPath _condamad/audits/prompt-generation-cartography -Directory` plus prior reports | CS-343 to CS-345 audit folders | PASS | Latest same-domain audits consulted. |
| E-003 | guardrail-source | `_condamad/stories/regression-guardrails.md` | RG registry | PASS | RG-002 applicable; exact natal input guardrail is a registry gap. |
| E-004 | source-scan | `rg -n -e "LLMAstrologyInputV1Builder" -e "build_llm_input_hash_material" -e "PROMPT_INFLUENCING_BLOCKS" -e "LLM_ASTROLOGY_INPUT_DATA_ROLES" -e "EXCLUDED_SURFACES" backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | role/hash constants and builder entrypoint | PASS | Shows prompt-visible blocks, role buckets, excluded surfaces, and hash helper. |
| E-005 | source-scan | `rg -n -e "_facts_block" -e "_signals_block" -e "_limits_block" -e "_shaping_block" -e "_evidence_block" -e "_provenance_block" -e "structured_facts_v1" -e "client_interpretation_projection_v1" backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | `LLMAstrologyInputV1Builder` block assembly | PASS | Shows all required blocks emitted by one owner. |
| E-006 | source-scan | `rg -n -e "AINarrativeInputBuilder" -e "AINarrativeInputContract" -e "_signals_block" backend/app/domain/astrology/interpretation` | signal builder and contract | PASS | Shows signal source ownership. |
| E-007 | source-scan | `rg -n -e "StructuredFactsV1Builder" -e "ClientInterpretationProjectionV1Builder" -e "structured_facts_v1" -e "client_interpretation_projection_v1" -e "compute_projection_hash" backend/app/domain/astrology/interpretation backend/app/domain/astrology/projections/projection_hash.py` | facts, shaping, hash owners | PASS | Shows canonical facts, shaping source, and hash helper ownership. |
| E-008 | source-scan | `rg -n -e "_build_llm_astrology_input_v1" -e "llm_astrology_input_v1" -e "projection_hash" -e "llm_input_hash" -e "evidence_refs" -e "grounding_status" backend/app/services/llm_generation/natal/interpretation_service.py` | natal service branch and audit helpers | PASS | Shows runtime assembly and audit persistence reads. |
| E-009 | source-scan | `rg -n -e "generate_natal_interpretation" -e "_prompt_visible_llm_astrology_input" -e "_without_prompt_excluded_keys" -e "chart_json" -e "natal_data" -e "LLM_ASTROLOGY_INPUT_DATA_ROLES" backend/app/domain/llm/runtime` | adapter, gateway branch, and legacy carrier handling | PASS | Shows modern gateway filtering and legacy carrier handling in runtime context. |
| E-010 | ast-guard | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/evidence/natal-astrology-input-symbol-map.md` | audited source files and symbols listed in the symbol map | PASS | Source-backed AST inventory records builder, hash helper, service branch, adapter branch, and gateway filters. |
| E-011 | pytest | `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short` | hash and evidence tests | PASS | 5 passed. |
| E-012 | pytest | `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short` | prompt boundary tests | PASS | 10 passed. |
| E-013 | pytest | `pytest -q tests/integration/test_llm_legacy_extinction.py --long --tb=short` | legacy carrier guards | PASS | 7 passed; without `--long`, pytest deselects integration tests. |
| E-014 | pytest | `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py --tb=short` | contract shape tests | PASS | 9 passed. |
| E-015 | read-only-guard | `python -S -B -c "git diff --quiet -- backend/app backend/tests frontend/src"` after venv activation | runtime/test/frontend delta | PASS | No application, backend test, or frontend source delta. |

## Explicit Limitations

- No external LLM provider call was executed; local doubles and source/AST guards are sufficient for this audit scope.
- Integration legacy guards require `--long`; the default fast pytest run deselects `tests/integration/**`.
