## CS-226 Natal Graph Dependency Proof

### Critical Dependencies
- `houses_runtime` depends on `julian_day`, `coordinates`, `house_system`, and `houses_raw`.
- `house_rulerships` depends on `houses_runtime`, `chart_objects`, and `runtime_reference`.
- `dignities` depends on `chart_objects`, `houses_runtime`, `aspects_runtime`, and `runtime_reference`.
- `chart_signature` depends on `chart_objects`, `signs_runtime`, `houses_runtime`, and `aspects_runtime`.
- `dominance` may depend on `dignities`; `dignities` does not depend on `dominance`.
- `chart_signature` stays independent from `dominance`, matching the current procedural pipeline order.

### Canonical Runtime Nodes
- `prepare_birth_data`
- `planet_positions`
- `astral_points`
- `houses_raw`
- `houses_runtime`
- `signs_runtime`
- `chart_objects`
- `aspects_runtime`
- `house_positions`
- `house_rulerships`
- `fixed_star_conjunctions`
- `advanced_conditions`
- `motion_visibility_payloads`
- `dignities`
- `dominance`
- `chart_signature`
- `interpretation_input`

### Projection Nodes
- `planet_positions_projection`
- `astral_points_projection`
- `houses_projection`
- `aspects_projection`
- `dignity_results_projection`
- `advanced_conditions_projection`
- `fixed_star_conjunctions_projection`
- `public_natal_result`

### Guard Result
- Canonical runtime nodes are tagged `canonical_runtime`.
- Compatibility nodes are tagged `compatibility_projection`.
- The public terminal projection is tagged `public_projection`.
- Tests assert no canonical runtime node depends on any compatibility or public projection output.
