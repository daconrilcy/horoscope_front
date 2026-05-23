## CS-230 Aspect Hints Boundary Evidence

### Structural Runtime
- `AspectCalculationResult` now serializes only structural facts: aspect code, participants, angle, orb, orb limits, family and major/minor flags.
- `calculate_major_aspects` and `calculate_interchart_aspects` consume `AspectStructuralDefinitionRuntimeData` and do not emit valence or energy fields.
- `build_aspect_structural_runtime_data` builds `AspectStructuralRuntimeData` without interpretive fields.

### Interpretive Hints
- `AspectInterpretiveHintResolver` resolves typed `AspectInterpretiveHintsRuntimeData` from `AspectStructuralRuntimeData` plus `AspectInterpretiveProfileRuntimeData`.
- Resolver test proves it does not implement angular distance, orb threshold, orb-used or strength evaluation logic.
- `natal_calculation_nodes` splits legacy aspect reference rows into structural definitions for calculators and interpretive profiles for hint resolution.

### Compatibility
- `AspectResult` keeps optional historical flat fields as a bounded legacy input surface.
- `AspectRuntimeData.interpretation` remains a bounded legacy projection and is now populated from hints when graph execution supplies profiles.
- `json_builder` still exposes public `interpretive_valence` and `energy_type`.
- `ChartInterpretationInputBuilder` marks aspect input source as `aspect_interpretive_hints` when hints are present.

### AC Traceability
- AC1: `test_aspect_calculation_contracts.py`, `test_aspect_runtime_boundary.py`.
- AC2: `test_aspect_runtime_builder.py`, `test_aspect_runtime_contracts.py`.
- AC3: `test_aspect_interpretive_hint_resolver.py`.
- AC4: `backend/app/tests/unit/test_chart_json_builder.py`, `test_api_contract_neutrality.py`.
- AC5: `test_chart_interpretation_input_builder.py`.
- AC6: `test_aspect_runtime_boundary.py`.
- AC7: prediction scan confirms remaining valence usage is profile/projection-owned, not structural runtime.
- AC8: `test_natal_calculation_graph_execution.py` and graph node split of structural definitions vs interpretive profiles.
