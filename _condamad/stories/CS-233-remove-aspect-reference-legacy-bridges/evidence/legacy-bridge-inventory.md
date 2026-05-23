# CS-233 Legacy Bridge Inventory

Story: `_condamad/stories/CS-233-remove-aspect-reference-legacy-bridges/00-story.md`

## Capsule

- Story/status alignment verified in `_condamad/stories/story-status.md`: CS-233 path and brief source match.
- Story header status is aligned with tracker status: `done`.
- Local requested skill path `.agents/skills/condamad-review-fix-story/SKILL.md` is absent; review/fix workflow was applied from the user brief.
- Capsule has no `generated/` directory; requested prepare/validate scripts are absent.

## Inventory

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `AspectDefinitionRuntimeData` | class | dead | none in active backend/tests architecture after migration | `AspectStructuralDefinitionRuntimeData` + `AspectInterpretiveProfileRuntimeData` | delete | `rg -n "\bAspectDefinitionRuntimeData\b|\b_aspect_definition\b" backend/app/domain/astrology backend/app/services/chart backend/tests/architecture -g "*.py"` => PASS: no matches | tests using old helper needed migration |
| `_aspect_definition` | helper | dead | none in active runtime after migration | `_aspect_structural_definition` over `AspectReferenceSet.structural_definitions` | delete | same scan => PASS: no matches | graph must still validate legacy orb fields |
| `AspectReferenceData.default_valence` | field | dead | no active reference payload | `AspectReferenceSet.interpretive_profiles` | delete | `test_structural_reference_contracts_do_not_require_interpretive_fields` | mapper must require profile fields explicitly |
| `AspectReferenceData.interpretive_valence` | field | dead | no active reference payload | `AspectReferenceSet.interpretive_profiles` | delete | same AST guard | public JSON field remains via hints |
| `AspectReferenceData.energy_type` | field | dead | no active reference payload | `AspectReferenceSet.interpretive_profiles` | delete | same AST guard | public JSON field remains via hints |
| `AspectResult.default_valence` | field | dead | none in public schema or model dump | `AspectResult.aspect_interpretive_hints.default_valence` | delete | `test_aspect_public_result_schema_does_not_expose_legacy_interpretive_fields`; `pytest -q backend/tests` | fixtures needed explicit hints |
| `AspectResult.interpretive_valence` | field | external-active public key only through serializer | `AspectResult.aspect_interpretive_hints.interpretive_valence` | keep-public-contract | `app.openapi()` keeps schema clean; chart JSON test keeps public key | missing hints must raise |
| `AspectResult.energy_type` | field | external-active public key only through serializer | `AspectResult.aspect_interpretive_hints.energy_type` | keep-public-contract | `TestClient` OpenAPI smoke and chart JSON test | frontend has no direct hit |
| `json_builder` flat fallback | fallback | dead | none after migration | `_public_aspect_interpretive_fields` requires hints | delete | `rg -n 'getattr\(aspect, "interpretive_valence"|getattr\(aspect, "energy_type"|aspect\.interpretive_valence|aspect\.energy_type' ...` => PASS: no matches | explicit error can surface bad fixtures |
| `AspectRuntimeWeightTaxonomy.interpretive_hints` | field | dead | test-only legacy expectation | no runtime structural owner | delete | `test_weight_taxonomy_separates_owners` | none |

## Guardrail Mapping

- RG-098: aspect runtime still produced by dedicated runtime/evaluator.
- RG-099: public aspect fields remain present through hints.
- RG-106: structural contracts do not carry valence/energy fields.
- RG-107: DB payload is parsed into immutable contracts by mapper.
- RG-145: aspect engine remains on chart-object inputs and structural definitions.
