# CS-232 Legacy Surface Inventory

## Capsule et mapping

- Story cible: `_condamad/stories/CS-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases/00-story.md`.
- Brief source vérifié dans `story-status.md`: `_story_briefs/cs-232-remove-legacy-runtime-surfaces-and-aspect-compatibility-aliases.md`.
- Statut tracker vérifié: `done` au 2026-05-23.
- Capsule `generated/`: absente.
- Scripts demandés absents: `.agents/skills/condamad-dev-story/scripts/condamad_prepare.py` et `condamad_validate.py`.
- Skill demandé absent: `.agents/skills/condamad-dev-story/SKILL.md`; fallback appliqué avec la story et les guardrails scopeés.

## Audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `AspectRuntimeData.interpretation` | alias | dead | ancien builder runtime et tests unitaires | `AspectInterpretiveHintsRuntimeData` + projection publique dans `json_builder` | delete | scan ciblé `rg -n "AspectRuntimeData\.interpretation" backend/app backend/tests -g "*.py"`: PASS no matches | faible, couvert par tests de projection publique |
| `AspectInterpretationRuntimeData` dans `runtime/aspect_runtime_data.py` | class | dead | ancien alias interne d'indices aspectuels | `AspectInterpretiveHintsRuntimeData` et `AspectInterpretiveProfileRuntimeData` | delete | scan ciblé runtime/builders/json/tests runtime: PASS no matches; le contrat homonyme conservé sous `domain/astrology/interpretation` est classé interpretive runtime | faible |
| `AspectCalculationResult.default_valence` | field | dead | aucun contrat structurel actuel | profil interpretatif dédié | delete | `test_structural_runtime_boundary.py` | faible |
| `AspectCalculationResult.interpretive_valence` | field | dead | aucun contrat structurel actuel | profil interpretatif dédié | delete | `test_structural_runtime_boundary.py` | faible |
| `AspectCalculationResult.energy_type` | field | dead | aucun contrat structurel actuel | profil interpretatif dédié | delete | `test_structural_runtime_boundary.py` | faible |
| `AspectModifierRuntimeData.interpretive_weight` | field | canonical-active | aucun champ sur modifier structurel | `AspectInterpretiveHintsRuntimeData.interpretive_weight` | keep-public-contract | `test_structural_runtime_boundary.py`; `test_astrology_runtime_boundary.py`; scan champs interprétatifs | faible |
| `NatalResult.planet_positions` | field | external-active | API/front, tests, projection publique | `NatalResult.chart_objects` pour logique interne | keep-public-contract | scan frontend ciblé; `test_chart_runtime_surface_guardrails.py` | moyen si suppression publique non décidée |
| `NatalResult.houses` | field | external-active | API/front, projection `json_builder`, prediction chart-json | `HouseRuntimeData` / `chart_objects` | keep-public-contract | scan frontend ciblé; `test_chart_runtime_surface_guardrails.py` | moyen |
| `NatalResult.advanced_conditions` | field | external-active | API/front expert panel, projection publique | payloads/facts dédiés | keep-public-contract | scan frontend ciblé; `test_chart_runtime_surface_guardrails.py` | moyen |
| `NatalResult.dignities` | field | external-active | API/front expert panel, audits, projection publique | `payloads.dignity` pour logique objet | keep-public-contract | scan frontend ciblé; doc architecture | moyen |
| `fixed_star_conjunctions` top-level | field | historical-facade | pas de champ public top-level ajouté; payloads objet | `ChartObjectRuntimeData.payloads.fixed_star_conjunctions` | confine-public-adapter | scan backend/front; doc architecture | faible |
| champs publics aspect `interpretive_valence` / `energy_type` | JSON keys | external-active | API/front potentiel, tests JSON | `_public_aspect_interpretive_fields` depuis hints ou champs plats | keep-public-contract | `backend/app/tests/unit/test_chart_json_builder.py`; OpenAPI smoke | moyen |
| `AspectResult.default_valence` / `interpretive_valence` / `energy_type` | public schema fields | historical-facade | réponses natal chart via `NatalResult` | hints interpretatifs + projection publique `json_builder` | confine-public-adapter | `test_api_contract_neutrality.py`; `AspectResult` OpenAPI sans champs legacy | faible |
| valence prediction | contract | canonical-active | `backend/app/domain/prediction`, `backend/app/services/prediction` | contrats prediction / profils dédiés | keep-public-contract | scans ciblés; `test_chart_interpretation_input_boundary.py` | faible |

## AC Traceability

| AC | Preuve |
|---|---|
| AC1 | `test_chart_runtime_surface_guardrails.py`; inventaire ci-dessus; scans legacy ciblés. |
| AC2 | suppression de `AspectRuntimeData.interpretation`; `test_structural_runtime_boundary.py` couvre aussi les modifiers. |
| AC3 | `test_aspect_interpretive_hint_resolver.py`; projection publique lit les hints avant les champs plats. |
| AC4 | `test_chart_json_builder.py`; `json_builder` conserve les champs publics via serializer nommé. |
| AC5 | allowlists docs mises à jour; aucune allowlist temporaire restante pour `AspectRuntimeData.interpretation`. |
| AC6 | `test_api_contract_neutrality.py`; `app.routes`, `app.openapi()`, `TestClient`; scan frontend ciblé. |
| AC7 | `test_structural_runtime_boundary.py`; `test_astrology_runtime_boundary.py`. |
| AC8 | `test_chart_interpretation_input_boundary.py`; scans prediction sur valence dédiée. |
