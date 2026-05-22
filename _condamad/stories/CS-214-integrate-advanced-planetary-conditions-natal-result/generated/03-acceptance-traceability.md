# CS-214 Acceptance Traceability

| AC | Statut | Evidence code | Evidence validation |
|---|---|---|---|
| AC1-AC3 | PASS | `advanced_planetary_conditions_runtime.py`, `signal_factory.py` | `test_advanced_planetary_conditions_runtime.py` |
| AC4-AC9 | PASS | Reutilisation des calculateurs CS-209 a CS-213 | Tests CS-209 a CS-213 passes |
| AC10-AC13 | PASS | Bundles par planete, signaux locaux et globaux | Tests runtime: bundles, signaux, phase lunaire |
| AC14 | PASS | `_supported_speeds` filtre les vitesses absentes/non finies | Test runtime `missing_motion_speed` |
| AC15-AC16 | PASS | Champ optionnel `NatalResult.advanced_planetary_conditions` et appel dans `build_natal_result` | `test_natal_result_conditions_integration.py` |
| AC17-AC22 | PASS | Pas de logique detaillee dans `natal_calculation.py`, pas de scoring/API/DB/frontend dans les nouveaux modules | Scans RG-141 et diff adjacent |
| AC23 | PASS | Capsule evidence + validation story | `condamad_story_validate.py`, `condamad_story_lint.py` |

## Note JSON public

Le champ runtime est declare avec `SkipJsonSchema[...]` et
`Field(default=None, exclude=True)`.
Il reste accessible sur l'objet `NatalResult`, mais ne modifie pas
`model_dump(mode="json")`, `NatalResult.model_json_schema()` ou OpenAPI, ce
qui respecte le non-goal de projection JSON/API publique.
