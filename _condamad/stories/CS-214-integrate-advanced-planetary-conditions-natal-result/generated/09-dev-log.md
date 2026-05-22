# CS-214 Dev Log

## 2026-05-22

- Preflight: story suffisante, RG-141 present, scope ferme.
- Implementation:
  - ajout de `advanced_planetary_conditions_runtime.py`;
  - ajout de `signal_factory.py`;
  - exports publics `calculate_advanced_planetary_conditions` et helpers de
    signaux;
  - ajout de `NatalResult.advanced_planetary_conditions` optionnel exclu du
    dump JSON;
  - branchement minimal dans `build_natal_result`.
- Validation initiale:
  - tests cibles CS-214: PASS;
  - tests CS-209 a CS-213: PASS;
  - `ruff format .`: PASS;
  - `ruff check .`: PASS.
- Regression detectee puis corrigee:
  - `pytest -q` initial echouait sur la serialisation JSON de `mappingproxy`
    dans la persistance;
  - correction: `SkipJsonSchema[...]` et `Field(default=None, exclude=True)`
    sur le champ runtime;
  - tests de persistance concernes: PASS;
  - `pytest -q` final: PASS.
- Review/fix iteration 1:
  - finding schema/API: accepte et corrige par `SkipJsonSchema[...]` plus test
    `model_json_schema` et OpenAPI;
  - finding signature factory: accepte et corrige par argument keyword-only
    `bundle=`;
  - validations finales: `ruff`, tests cibles, tests CS-209 a CS-213,
    persistance, `pytest -q`, scans RG-141 et story lint/validate PASS.
- Feedback loop: no-propagation, correction locale couverte par test
  `model_dump(mode="json")`, schema et OpenAPI.
