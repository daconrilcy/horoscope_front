# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The taxonomy exposes a version. | `NATAL_NARRATIVE_THEME_TAXONOMY_VERSION` and `NatalNarrativeThemeTaxonomy.version` in `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py`. | `pytest -q tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py` and `evidence/theme-taxonomy-after.json`. | PASS |
| AC2 | The catalog contains the ten Basic codes. | `BasicThemeCode` and `_default_theme_definitions()` define the ten canonical codes in one owner. | `test_taxonomy_exposes_version_and_ten_canonical_basic_codes`. | PASS |
| AC3 | Active themes expose selected fact IDs. | `ThemeModel.selected_fact_ids` merges resources, constraints, tensions and mention lists. | `test_identity_and_functional_themes_activate_with_selected_fact_ids`. | PASS |
| AC4 | Active themes expose activation metadata. | `ThemeModel.activation_metadata` records matched count, salience levels and reason codes. | `test_identity_and_functional_themes_activate_with_selected_fact_ids`. | PASS |
| AC5 | Identity themes activate. | `core_identity` and `emotional_pattern` definitions consume luminary material. | `test_identity_and_functional_themes_activate_with_selected_fact_ids`. | PASS |
| AC6 | Functional themes activate. | Functional definitions cover relationship, mental, resources and action themes. | `test_identity_and_functional_themes_activate_with_selected_fact_ids`. | PASS |
| AC7 | House themes respect availability. | `PUBLIC_VOCATION` is timed-only and requires houses/angles. | `test_house_and_angle_themes_respect_birth_time_availability`. | PASS |
| AC8 | Date-only themes omit angle material. | `_definition_available()` blocks unavailable timed surfaces from `EligibilityContext`. | `test_house_and_angle_themes_respect_birth_time_availability`. | PASS |
| AC9 | Compatible sections are declared. | Every `ThemeDefinition` declares `compatible_sections`. | `test_each_theme_declares_contractual_sections_vocabulary_and_availability`. | PASS |
| AC10 | Redundant themes are hierarchized. | `TALENTS_AND_SUPPORTS` has `hierarchy_parent=TENSION_TO_INTEGRATE`; `_drop_redundant_children()` removes redundant child themes. | `test_redundant_support_theme_is_hierarchized_below_tension_theme`. | PASS |
| AC11 | Tension themes preserve tension facts. | Constraints/tensions are included in `must_mention` and unsupported nearby facts in `do_not_mention`. | `test_tension_theme_preserves_tension_and_do_not_mention_facts`. | PASS |
| AC12 | Weak signals stay section-ineligible. | Activation requires enough included salience material and reuses CS-412 exclusions. | `test_growth_theme_requires_repeated_or_high_node_material`. | PASS |
| AC13 | Advised vocabulary is documented. | Every `ThemeDefinition` declares `advised_vocabulary`. | `test_each_theme_declares_contractual_sections_vocabulary_and_availability`. | PASS |
| AC14 | Forbidden formulations are guarded. | Every `ThemeDefinition` declares `forbidden_formulations`; app scan uses standalone forbidden wording boundaries. | `rg -n "\b(spirituel\|creatif\|harmonieux\|profond)\b" ...` returned no matches. | PASS |
| AC15 | Public boundaries expose no raw theme internals. | No changes to `llm_astrology_input_v1.py` or `narrative_natal_reading_builder.py`; AST/public-boundary tests cover raw internal field absence. | `pytest -q tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py`; bounded `rg` raw field scan PASS. | PASS |
| AC16 | `RG-162` protects versioned Basic theme activation contracts. | Registry already contains `RG-162` for CS-413 and story cites it. | `rg -n "RG-162" _condamad/stories/regression-guardrails.md`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
