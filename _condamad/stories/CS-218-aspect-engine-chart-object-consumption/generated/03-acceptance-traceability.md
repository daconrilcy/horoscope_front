# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Selector filtre `supports_aspects=True`. | `aspect_inputs.py` selector. | `pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py` | PASS |
| AC2 | Non-aspectable sans longitude ignore. | Selector ignore les objets sans capacite. | Meme test cible. | PASS |
| AC3 | Aspectable sans longitude erreur explicite. | `ValueError` selector. | Meme test cible. | PASS |
| AC4 | Code aspectable duplique erreur explicite. | Detection de code normalise duplique. | Meme test cible. | PASS |
| AC5 | Projection unique vers `AspectBodyRuntimeData`. | `AspectBodyProjector`. | Test projector + scan builders specialises. | PASS |
| AC6 | Sun/Moon/Mars aspectent depuis `chart_objects`. | Flux natal projete depuis `chart_objects`. | Tests selector et flux natal avec spy. | PASS |
| AC7 | Angle aspectable inclus. | Projector/calcul accepte un angle aspectable. | Test `test_calculation_consumes_projected_chart_objects_with_angle`. | PASS |
| AC8 | Orchestrateur natal consomme `chart_objects`. | `build_natal_result` construit `chart_objects` avant aspects. | `test_natal_aspects_include_points.py`. | PASS |
| AC9 | Aspects planetaires existants equivalents. | Flux conserve les planetes et flag points existant. | Baseline cible + suite backend. | PASS |
| AC10 | `NatalResult` garde ses collections. | `planet_positions`, `astral_points`, `houses`, `chart_objects` conserves. | `test_natal_result_chart_objects.py`. | PASS |
| AC11 | Aucune branche `object_type` dans aspects. | Pas de branche `object_type` dans `aspect_inputs.py`/`aspects.py`. | Guard AST + scan `rg`. | PASS |
| AC12 | Aucun usage direct des collections historiques dans les calculateurs d'aspects. | Flux aspect n'utilise plus `positions_raw`/`points_raw`. | Guard AST + scan classe. | PASS |
| AC13 | Regles d'orbes stables. | `calculate_major_aspects` et contrats d'orbes inchanges. | `test_aspect_runtime_builder.py` + suite backend. | PASS |
| AC14 | `RG-145` est enregistre. | Registre garde la ligne `RG-145`. | `rg -n "RG-145" _condamad/stories/regression-guardrails.md`. | PASS |
