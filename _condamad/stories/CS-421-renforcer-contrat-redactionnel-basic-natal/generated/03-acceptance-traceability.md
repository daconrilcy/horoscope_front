# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic payload contains section editorial briefs. | `build_basic_natal_editorial_briefs`; `section_editorial_briefs` in provider payload. | `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short` PASS. | PASS |
| AC2 | Public evidence labels are localized for non-initiated readers. | `basic_natal_reading_plan._public_label/_public_explanation`. | `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py --tb=short` PASS. | PASS |
| AC3 | Each section brief carries controlled human meaning. | `BasicNatalEditorialBrief.reader_meaning/possible_manifestation/nuance`. | Prompt payload tests PASS. | PASS |
| AC4 | Provider payload prevents model-only interpretation from codes. | `report_arc`, `plain_language_glossary`, `source_usage_policy`, no fact IDs in prompt payload. | Prompt payload tests and provider payload tests PASS. | PASS |
| AC5 | Accepted Basic drafts explain facts instead of listing them. | `_looks_like_source_listing`; fallback no longer lists labels as body content. | Validator tests PASS. | PASS |
| AC6 | `summary` cannot replace the introduction. | `_basic_natal_contract_from_draft` uses `NatalSynthesis.introduction`. | Reading contracts and validator projection tests PASS. | PASS |
| AC7 | `Fil conducteur` is not rendered as an ordinary duplicate theme. | `_basic_natal_contract_from_draft` consumes `synthesis` as introduction and skips theme append. | `test_basic_public_contract_uses_synthesis_as_introduction_not_duplicate_theme` PASS. | PASS |
| AC8 | Each accepted theme contains at least two informative sentences. | `_informative_sentence_count` and `weak_editorial_section`. | Validator tests PASS. | PASS |
| AC9 | Observed mechanical template phrases are rejected. | `_BASIC_NATAL_FORBIDDEN_PATTERNS`; provider denylist. | Validator tests PASS; denylist scan hits only validator, denylist, and negative tests. | PASS |
| AC10 | Raw English astrology labels are rejected from public text. | Raw label regexes and localized public evidence. | Validator and public evidence tests PASS; denylist scan classified. | PASS |
| AC11 | Unaccented French public forms are rejected. | Regexes for `Synthese`, `theme`, `repere`, `planetaire`, `a integrer`. | Validator tests PASS. | PASS |
| AC12 | Deterministic fallback cannot publish mechanical text. | `_fallback_section_text` now writes two explanatory sentences and no source inventory. | Validator fallback test PASS; integration pipeline PASS with `--long`. | PASS |
| AC13 | Disclaimers do not count as editorial content. | `_is_disclaimer_only`. | Validator tests PASS. | PASS |
| AC14 | The user fixture produces readable plan-bounded Basic public text. | Integration helper fallback and public contract projection. | `python -B -m pytest -q --long tests/integration/test_basic_natal_v2_pipeline.py --tb=short` PASS. | PASS |
| AC15 | CS-409 to CS-418 regression guards remain green. | Existing Basic contract, validation and engine fields preserved. | Reading contracts, prompt payload, provider payload, translation resolver, scans PASS/classified. | PASS |
| AC16 | Story evidence artifacts are persisted. | `evidence/basic-*-before.json` and `evidence/basic-*-after.json`. | `python -B -c` evidence check PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
