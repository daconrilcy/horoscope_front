<!-- Commentaire global: journal de preuves reproductibles pour l'audit CS-346. -->

# Evidence Log

| ID | Evidence type | Command / Source | Inspected path or surface | Result | Notes |
|---|---|---|---|---|---|
| E-001 | story-source | `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md` | CS-346 scope and ACs | PASS | Story confirms audit-only delivery. |
| E-002 | prior-history | `Get-ChildItem _condamad/audits/prompt-generation-cartography` plus prior reports | CS-343 to CS-345 audit folders | PASS | Latest same-domain audits consulted. |
| E-003 | guardrail-source | `_condamad/stories/regression-guardrails.md` | RG registry | PASS | RG-002 applicable; exact natal input guardrail is a registry gap. |
| E-004 | source-scan | `rg` role and hash constants in `llm_astrology_input_v1.py` | role/hash constants | PASS | Shows prompt-visible blocks and role buckets. |
| E-005 | source-scan | `rg` builder and block names in `llm_astrology_input_v1.py` | LLM input builder | PASS | Shows all required blocks emitted by one owner. |
| E-006 | source-scan | `rg` narrative input symbols in `backend/app/domain/astrology/interpretation` | signal builder and contract | PASS | Shows signal source ownership. |
| E-007 | source-scan | `rg` facts, shaping, and hash symbols in astrology domain paths | facts, shaping, hash owners | PASS | Shows canonical facts, shaping, and hash helpers. |
| E-008 | source-scan | `rg` builder, hash, and evidence symbols in natal interpretation service | natal service branch and audit helpers | PASS | Shows runtime assembly and audit persistence reads. |
| E-009 | source-scan | `rg` natal adapter, gateway, and legacy carrier symbols in LLM runtime | adapter and gateway branch | PASS | Shows gateway handoff and removal of legacy render vars. |
| E-010 | ast-guard | `python -S -B -c "<AST symbol inventory>"` after venv activation | audited source files | PASS | Found builder, hash helper, service branch, adapter branch, and gateway filters. |
| E-011 | pytest | `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py --tb=short` | hash and evidence tests | PASS | 5 passed. |
| E-012 | pytest | `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short` | prompt boundary tests | PASS | 10 passed. |
| E-013 | pytest | `pytest -q tests/integration/test_llm_legacy_extinction.py --long --tb=short` | legacy carrier guards | PASS | 7 passed; without `--long`, pytest deselects integration tests. |
| E-014 | pytest | `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py --tb=short` | contract shape tests | PASS | 9 passed. |
| E-015 | read-only-guard | `python -S -B -c "git diff --quiet -- backend/app backend/tests frontend/src"` after venv activation | runtime/test/frontend delta | PASS | No application, backend test, or frontend source delta. |

## Explicit Limitations

- No external LLM provider call was executed; local doubles and source/AST guards are sufficient for this audit scope.
- Integration legacy guards require `--long`; the default fast pytest run deselects `tests/integration/**`.
