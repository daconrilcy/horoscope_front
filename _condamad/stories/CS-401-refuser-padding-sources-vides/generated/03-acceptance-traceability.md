# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Missing chapter source raises an explicit projection error. | `narrative_natal_reading_builder.py` raises `NarrativeChapterSourceMissingError`; `interpretation_service.py` routes it to `chapter_source_missing`. | `python -B -m pytest -q tests/unit/test_narrative_natal_reading_v1.py --tb=short` PASS. | PASS |
| AC2 | Chapter key order is exactly canonical. | Builder iterates `NARRATIVE_CHAPTER_ORDER`; public validator rejects reordered chapters. | Unit tests PASS; `test_public_validator_rejects_non_canonical_chapter_order`. | PASS |
| AC3 | Normalized chapter narratives are unique. | `validate_narrative_semantic_integrity` rejects duplicate normalized narratives. | Unit tests PASS; integration `--long` public boundary PASS. | PASS |
| AC4 | Normalized chapter titles are unique. | `validate_narrative_reading_public_text` delegates to semantic integrity title duplicate detection. | Unit tests PASS; `test_duplicate_chapter_titles_are_rejected`. | PASS |
| AC5 | Basic/Premium public sources are non-empty. | Semantic integrity rejects `basic`/`premium` readings without `used_astrological_elements`. | Unit tests PASS; `test_public_validator_rejects_basic_empty_sources`. | PASS |
| AC6 | Rejected semantic payloads stay private. | `NatalInterpretationService` hides/deletes invalid complete public rows and keeps audit rows private. | `python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short` PASS. | PASS |
| AC7 | Forbidden source padding stays absent. | Architecture guard `test_narrative_semantic_integrity_guard.py` scans natal generation sources. | `rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal` exit 1 = PASS no matches; architecture tests PASS. | PASS |
| AC8 | Contract documentation states the integrity rule. | `backend/docs/narrative-natal-reading-v1-contract.md` documents no padding, distinct chapters and non-empty sources for Basic/Premium. | `rg -n "padding\|used_astrological_elements\|RG-155" backend/docs/narrative-natal-reading-v1-contract.md` PASS. | PASS |
| AC9 | Story evidence artifacts are persisted. | Evidence directory contains before/after, removal audit, validation output and final evidence. | `condamad_validate.py <capsule> --final` PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
