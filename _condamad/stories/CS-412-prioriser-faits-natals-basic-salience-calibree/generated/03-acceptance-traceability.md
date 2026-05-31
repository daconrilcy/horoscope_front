# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Each included fact has `salience_score`. | `NatalSalienceDecision.to_internal_payload`; model tests assert all included payloads contain the field. | `python -B -m pytest -q backend\tests\unit\domain\astrology\test_basic_natal_salience_model.py --tb=short` | PASS |
| AC2 | Each included fact has `salience_level`. | `NatalSalienceLevel` and decision payload contract. | same pytest command; contract-shape assertion. | PASS |
| AC3 | Each included fact has stable `reason_codes`. | `_reason_codes` emits named reason codes from graph facts only. | same pytest command; stable Sun/Moon/exact aspect assertions. | PASS |
| AC4 | Exclusions have a reason. | `NatalSalienceExclusionReason` and `_exclusion_reason`. | same pytest command; unavailable, minor and weak-signal exclusions asserted. | PASS |
| AC5 | Eligible Sun remains a pillar. | `pillar_sun` scoring in `natal_salience_model.py`. | salience model pytest. | PASS |
| AC6 | Eligible Moon remains a pillar. | `pillar_moon` scoring in `natal_salience_model.py`. | salience model pytest. | PASS |
| AC7 | Eligible Ascendant remains a pillar. | `pillar_ascendant` scoring plus birth-time eligibility check. | salience model pytest and date-only archetype pytest. | PASS |
| AC8 | Minor facts stay below pillars. | `_MINOR_OR_TECHNICAL_CODES` exclusion and RG-161 tests. | `test_contrasted_archetypes_keep_pillars_above_minor_or_technical_facts` + forbidden-signal scan PASS. | PASS |
| AC9 | Exact luminary aspect ranks higher. | `exact_aspect` marker consumed from runtime source path, no orb recalculation. | `test_exact_luminary_aspect_ranks_above_wide_transpersonal_aspect`. | PASS |
| AC10 | Dominant house stays thematic. | `dominant_house` reason and `thematic` level threshold. | `test_dominant_house_is_thematic_without_becoming_fixed_global_priority`. | PASS |
| AC11 | Single weak signal is blocked. | `SINGLE_WEAK_SIGNAL` exclusion. | `test_single_weak_signal_is_blocked_from_autonomous_section_material`. | PASS |
| AC12 | Required profiles are covered. | `basic_natal_salience_archetypes.json` declares ten required archetypes. | `test_required_archetype_corpus_and_golden_metadata_are_declared`. | PASS |
| AC13 | Golden metadata is declared. | Fixture declares expected facts, themes, sections, forbidden facts and quality assertions. | archetype pytest + `evidence/salience-after.json`. | PASS |
| AC14 | Public contracts expose no salience score. | Salience remains in internal domain model only; public projection builder unchanged. | AST public projection test + bounded public negative scan PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
