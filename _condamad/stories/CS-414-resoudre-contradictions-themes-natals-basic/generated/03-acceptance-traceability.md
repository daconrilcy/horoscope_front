# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The resolver consumes active themes. | `SynthesisResolver.resolve()` accepts `Sequence[ThemeModel]` and does not rebuild activation. | `python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py --tb=short` | PASS |
| AC2 | The resolver returns resolved themes. | `ResolvedThemeSynthesis` contract in `natal_synthesis_resolver.py`. | Same targeted pytest; payload assertions in resolver tests. | PASS |
| AC3 | Resource facts drive resource synthesis. | `_fact_statement(..., "ressource")` maps `ThemeModel.resources`. | `test_resolver_consumes_active_themes_and_emits_contract_fields`. | PASS |
| AC4 | Constraint facts drive synthesis. | `_fact_statement(..., "contrainte")` maps `ThemeModel.constraints`. | `test_resolver_consumes_active_themes_and_emits_contract_fields`. | PASS |
| AC5 | Tension facts drive integration. | `_integration_statement()` links tensions and mixed signals. | Resolver and contradiction tests. | PASS |
| AC6 | Each synthesis has a core statement. | Required dataclass field and internal payload field. | Payload shape assertion. | PASS |
| AC7 | Each synthesis has a resource statement. | Required dataclass field and internal payload field. | Payload shape assertion. | PASS |
| AC8 | Each synthesis has a constraint statement. | Required dataclass field and internal payload field. | Payload shape assertion. | PASS |
| AC9 | Each synthesis has integration. | Required dataclass field and internal payload field. | Payload shape assertion. | PASS |
| AC10 | Each synthesis has confidence. | `_confidence_for_theme()` emits `low`, `medium` or `high`, not raw scores. | Payload and contradiction assertions. | PASS |
| AC11 | Strong mixed signals force nuance. | Strong resource plus strong constraint emits `nuance explicite`. | Contradiction pytest. | PASS |
| AC12 | One weak fact stays ineligible. | `_omission_reason()` returns `weak_single_fact`; AST guard keeps resolver in domain. | `test_one_weak_fact_cannot_be_autonomous_section_candidate`; AST guard test. | PASS |
| AC13 | Redundant themes are merged. | `_shared_fact_merge_groups()` links identical selected fact sets. | `test_redundant_themes_are_linked_by_shared_facts`. | PASS |
| AC14 | Unavailable house themes are downgraded. | `_uses_unavailable_birth_time_surface()` checks house, ASC, MC surfaces. | `test_date_only_context_downgrades_house_angle_and_mc_surfaces`. | PASS |
| AC15 | Date-only synthesis excludes houses. | Date-only omission statement recenters on signs, luminaries, aspects and balances. | Same date-only pytest. | PASS |
| AC16 | Venus combust case is nuanced. | Strong Venus resource plus combust constraint covered. | `test_venus_strong_but_combust_is_nuanced`. | PASS |
| AC17 | Constrained Moon case is nuanced. | Moon resource and constraint remain separate. | `test_constrained_moon_keeps_resource_and_constraint_separate`. | PASS |
| AC18 | Jupiter square case is nuanced. | Jupiter resource plus luminary square tension covered. | `test_jupiter_square_luminaires_is_integrated_without_absolute_tone`. | PASS |
| AC19 | Mixed relationship case is nuanced. | Relationship support and tension emit explicit integration. | `test_mixed_relationship_theme_links_support_and_tension`. | PASS |
| AC20 | Forbidden formulations are denied. | `_ensure_controlled_wording()` rejects absolute/prescriptive wording before downstream use. | Pytest denylist case; `rg` wording scan returned no matches. | PASS |
| AC21 | Resolved syntheses remain non-public. | Resolver lives under domain and is not imported by frontend, API, or LLM narrative services. | AST guard pytest; `rg` boundary scan returned no matches. | PASS |
