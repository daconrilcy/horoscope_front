# Evidence Log - prompt-generation-cartography - 2026-05-27-1800

| ID | Evidence type | Command / Source | Inspected path / surface | Result | Summary |
|---|---|---|---|---|---|
| E-001 | story-source | Read story `CS-343-prompt-generation-surface-inventory/00-story.md` and source brief | `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md`, `_story_briefs/cs-343-audit-inventaire-surfaces-generation-prompt-llm.md` | PASS | Scope is audit-only inventory for backend LLM prompt-generation surfaces. |
| E-002 | guardrail-source | Read regression guardrail registry | `_condamad/stories/regression-guardrails.md` | PASS | Applicable guardrails include RG-002 and RG-022; prompt fallback guardrails RG-016 to RG-022 remain relevant context. |
| E-003 | prior-audit-source | Read latest same-domain and adjacent audit summaries | `_condamad/audits/prompt-generation/2026-05-02-1452`, CS-324, CS-325, CS-326, CS-327 audit folders | PASS | Prior findings around fallback prompts, `chart_json`, evidence boundary and canonical input were consulted. |
| E-004 | file-inventory-scan | `rg --files` filtered for llm, prompt, assembly, persona, provider, astrology input and test guard names | `backend/app/domain/llm`, `backend/app/services/llm_generation`, `backend/app/ops/llm/bootstrap`, `backend/app/api`, `backend/tests` | PASS | Inventory found runtime, config, service, bootstrap, router and guard surfaces used in this audit. |
| E-005 | source-symbol-scan | Targeted `rg -n` for definitions and LLM prompt-generation symbols | Priority backend files from CS-343 | PASS | Key owners and symbols were found for gateway, assembly resolver, use-case registry, renderer, natal service and astrology input. |
| E-006 | ast-guard | Activated venv, then `python -S -B -c` AST symbol extraction | Six priority Python owners | PASS | AST parse succeeded and listed canonical classes/functions without modifying code. |
| E-007 | runtime-boundary-tests | Activated venv, `cd backend`, targeted pytest for LLM astrology input boundaries | `backend/tests/architecture`, `backend/tests/llm_orchestration`, `backend/tests/unit/domain/llm` | PASS | 22 tests passed in 3.46s, including prompt/audit payload boundary guards. |
| E-008 | no-runtime-delta-scan | `git status --short -- backend/app backend/tests backend/migrations frontend/src` | Runtime, test, migration and frontend source roots | PASS | No application, test, migration or frontend source delta was present after read-only evidence collection. |
| E-009 | dependency-direction-scan | Targeted scan for API and FastAPI imports in domain/service LLM paths | `backend/app/domain/llm`, `backend/app/services/llm_generation`, `llm_astrology_input_v1.py` | PASS | No forbidden API/FastAPI dependency hit was returned. |
| E-010 | archival-carrier-scan | Targeted scan for `chart_json`, `natal_data`, `evidence`, `evidence_refs`, `prompt_visible`, `provider` | `backend/app`, `backend/tests`, `_condamad`, `_story_briefs` | PASS | Hits exist across runtime, tests and archives; classification separates executable influence from historical/audit text. |
| E-011 | route-surface-scan | Targeted scan for router registration and LLM router symbols | `backend/app/api/v1/routers` | PASS | LLM admin, internal QA and public generation routers were identified as trigger/exposure surfaces, not prompt owners. |
| E-012 | migration-seed-model-scan | Targeted scan for LLM DB models, migrations and bootstrap symbols | `backend/app/infra/db/models`, `backend/migrations`, `backend/app/ops/llm/bootstrap` | PASS | Prompt, use-case, assembly, persona, provider and audit persistence carriers were found and classified by role. |

## Limitations

- This is a source and targeted-test audit, not a live provider execution run.
- Broad archival scans include CONDAMAD history by design; execution influence is assigned only when a source trace or test guard supports it.
