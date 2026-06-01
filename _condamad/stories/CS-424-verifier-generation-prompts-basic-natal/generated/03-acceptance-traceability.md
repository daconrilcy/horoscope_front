# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic final prompt renders from the published assembly. | `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`; runtime render from `theme_astral/prompt_contract/expanded`. | `python -B -m pytest -q --long tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short` PASS. | PASS |
| AC2 | Basic final prompt tells how to use enriched payload sections. | Prompt condition for `input_data.basic_natal_prompt_payload`, `sections`, `section_editorial_briefs`, `report_arc`, `plain_language_glossary`. | Same bigbang pytest PASS; `basic-final-prompt-after.txt` snapshot. | PASS |
| AC3 | Basic final prompt asks for a human report. | Prompt requires a readable human natal report with introduction, explanatory themes, conclusion. | Same bigbang pytest PASS. | PASS |
| AC4 | Basic final prompt imposes source annex usage. | Prompt requires `editorial_evidence` as annex source material, not main prose. | Same bigbang pytest PASS. | PASS |
| AC5 | User payload keeps Basic enriched data private. | `test_theme_astral_provider_payload_handoff.py` verifies `basic_natal_prompt_payload` handoff and carrier absence. | `python -B -m pytest -q --long tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short` PASS. | PASS |
| AC6 | Baseline mechanical phrases are blocked. | Prompt denies `forbidden_template_phrases` and the three observed baseline phrases. | Bigbang pytest PASS; scan hits only guarded denylist/evidence contexts. | PASS |
| AC7 | Safety constraints stay explicit in the final prompt. | Prompt preserves no extra facts, non-fatalism, no firm prediction, no prescriptive advice, limitations and disclaimers. | Bigbang pytest PASS. | PASS |
| AC8 | Forbidden carriers stay absent from final prompt. | Prompt snapshot after has no `natal_interpretation`, `natal_interpretation_short`, `chart_json`, `natal_data`; payload tests deny raw carriers. | Zero-hit `rg` carrier scan on `basic-final-prompt-after.txt` PASS/no matches; builder pytest PASS. | PASS |
| AC9 | Published assemblies stay unique by depth. | `test_theme_astral_basic_uses_published_prompt_contract_not_legacy_natal_keys` asserts exactly essential/expanded/complete. | `python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short` PASS. | PASS |
| AC10 | Basic active path does not use old prompt keys. | Same assembly test asserts expanded prompt uses `theme_astral_prompt_v1` and excludes old natal prompt keys. | Same assembly pytest PASS. | PASS |
| AC11 | Prompt evidence artifacts are persisted. | `evidence/basic-final-prompt-before.txt`, `evidence/basic-final-prompt-after.txt`, `evidence/basic-user-payload-after.json`. | `python -B -c` evidence-file check PASS. | PASS |
| AC12 | Non-Basic handoff contracts remain unchanged. | Existing free/premium skeleton and builder assertions preserved. | `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short` PASS. | PASS |
| AC13 | Durable Basic final-prompt guard creates `RG-171`. | `_condamad/stories/regression-guardrails.md` contains new `RG-171`. | `Select-String -Path _condamad/stories/regression-guardrails.md -Pattern 'RG-171'` PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
