# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `admin_prompts.py` stops exposing `natal_long_free`. | `_derive_admin_runtime_use_case_key` now returns the template key without free-plan derivation. | Architecture suite PASS; `evidence/legacy-source-hits-after.txt` has no `natal_long_free` hit in `admin_prompts.py`. | PASS |
| AC2 | `natal_interpretation_short` is not seedable. | Deleted old seed scripts/wrappers; architecture guard asserts removed paths. | Orchestration, architecture, admin and script tests PASS. | PASS |
| AC3 | `natal_long_free` is not seedable. | Removed from admin derivation, scripts, and assembly convergence seeds. | Orchestration/architecture/admin tests PASS; after scan has only classified residuals. | PASS |
| AC4 | Basic/Free taxonomy does not map `natal_interpretation`. | Removed from canonical contracts and taxonomy; old assembly test now proves non-nominal resolution. | `tests/llm_orchestration/test_assembly_resolution.py` PASS. | PASS |
| AC5 | Prompt catalogues exclude old natal fallbacks. | Removed `natal_interpretation` runtime catalogue entry; fallback catalogue remains test-only. | Governance and legacy-extinction orchestration tests PASS. | PASS |
| AC6 | Admin/catalogue positive fixtures use modern keys. | Admin resolved-detail fixture now uses `theme_natal_reading_free_preview_*`, not `natal_long_free`. | Admin integration suite with `--long` PASS. | PASS |
| AC7 | `basic_natal_prompt_payload` keeps its modern owner. | Theme astral test now imports `THEME_ASTRAL_PROMPT_TEMPLATE`; prompt-contract guard remains owner proof. | Theme astral architecture guard PASS. | PASS |
| AC8 | Prompt-generation cartography reflects `theme_natal`. | Cartography no longer documents `AIEngineAdapter.generate_natal_interpretation` as provider chain. | Cartography scan recorded in `evidence/validation.txt`. | PASS |
| AC9 | CS-440 prompt-source blockers are refreshed. | Architecture guard asserts physical removal of old seed files and no admin prompt runtime exception. | Architecture suite PASS; removal audit persisted. | PASS |
| AC10 | Residual old-key hits are classified. | `evidence/legacy-source-allowlist.md` classifies residual readonly, action-token, and test guard hits. | After scan persisted and classified. | PASS |
| AC11 | Story evidence artifacts are persisted. | Required evidence files exist under `evidence/`. | Persistent evidence check recorded in `evidence/validation.txt`. | PASS |

All listed acceptance criteria are complete for implementation handoff.
