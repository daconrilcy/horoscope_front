# Validation Output - Pipeline Prompt LLM Natal

All Python, pytest and ruff commands below were run after activating `.\.venv\Scripts\Activate.ps1`.

| Command | Result |
|---|---|
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - CONDAMAD domain audit validation passed. |
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - CONDAMAD domain audit lint passed. |
| `rg -n "NatalInterpretationService\|NatalExecutionInput\|AIEngineAdapter\|generate_natal_interpretation\|LLMGateway._build_messages\|build_user_payload" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - required runtime flow symbols are present in audit artifacts. |
| `rg -n "chart_json\|natal_data\|evidence_catalog\|astro_context\|plan\|level\|variant_code\|module" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - required field vocabulary is present in audit artifacts. |
| `rg -n "prompt-visible\|runtime-only\|validation-only\|not-used\|lost-or-flattened" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - required visibility/classification vocabulary is present. |
| `rg -n "/users\|simplified legacy payload\|fallback\|schema v1\|schema v2\|schema v3" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - legacy vocabulary is present. |
| `python -S -B -c "... required audit files exist ..."` | PASS - story-specific and CONDAMAD standard files exist. |
| `python -S -B -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend'], text=True); assert out.strip() == '', out"` | PASS - no application, backend test or frontend files changed. |
| `rg -n "NatalExecutionInput\|generate_natal_interpretation\|LLMExecutionRequest\|build_user_payload\|chart_json_in_prompt\|Technical Data\|astro_context\|evidence_catalog\|variant_code\|module" .\backend\app .\backend\tests` | PASS - source evidence surfaces are reproducible. |
| `pytest -q backend/tests/llm_orchestration` | PASS - 221 passed in 18.29s. |
| `ruff format --check .` | PASS - 1686 files already formatted. |
| `ruff check .` | PASS - all checks passed. |

## Worktree Note

Pre-existing untracked file before audit writes: `_condamad/run-state.json`.

Expected new audit artifact directory:

- `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/`

## Targeted Audit Review - 2026-05-27

Review correction: added missing mandatory-source evidence and classification for
`backend/app/domain/llm/prompting/prompt_renderer.py` and
`backend/app/domain/llm/configuration/assembly_resolver.py`, then propagated the
evidence into findings, sequence, field/branch matrices and story candidates.

| Command | Result |
|---|---|
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - CONDAMAD domain audit validation passed. |
| `python -S -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - CONDAMAD domain audit lint passed. |
| `python -S -B -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend'], text=True); assert out.strip() == '', out"` | PASS - no application, backend test or frontend files changed. |
| `rg -n "prompt_renderer.py\|assembly_resolver.py\|E-023\|E-024\|E-025\|PromptRenderer\|assembly_resolver" _condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | PASS - review-added mandatory source evidence is present across audit artifacts. |
