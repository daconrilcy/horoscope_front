# CS-221 Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `house_position` expose une forme typee complete. | `ChartObjectHousePositionPayload` porte `house_number`, `house_modality`, `source`, `house_cusp_code`, `house_cusp_longitude`. | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_house_position_rulership_runtime.py`; backend full suite. | PASS |
| AC2 | La modalite reutilise le helper canonique. | `build_house_position_payload()` appelle `resolve_house_kind`. | Test `modality` + scan modalite sans constante locale dans builders/dignities/dominance. | PASS |
| AC3 | `RulershipRuntimePayload` expose une projection calculatoire stable. | Nouveau dataclass `RulershipRuntimePayload`. | Tests `rulership_payload`, `rules_houses`, `angles`, `dispositor`, `missing_sign`. | PASS |
| AC4 | `ChartObjectPayloads` expose `rulership` sans dictionnaire libre. | `ChartObjectPayloads.rulership: RulershipRuntimePayload | None`. | Test `payload_shape`; `ruff check .`. | PASS |
| AC5 | Les planetes/luminaires qui gouvernent des maisons portent `rules_houses`. | `RulershipPayloadEnricher` indexe les `HouseRulerResult` par code objet. | Test `rules_houses`. | PASS |
| AC6 | Les flags rulers angulaires ciblent les maisons attendues. | `RulershipPayloadProjector` derive `is_ascendant_ruler` et `is_midheaven_ruler`. | Test `angles`. | PASS |
| AC7 | `dispositor_code` vient des rulerships canoniques. | `_dispositor_for()` lit `sign_rulerships` fourni par le runtime. | Test `dispositor`; scan anti table locale. | PASS |
| AC8 | Sans signe exploitable, `dispositor_code` reste `None`. | `_dispositor_for()` retourne `None` si `zodiac_position` manque. | Test `missing_sign`. | PASS |
| AC9 | Les objets non eligibles ne recoivent pas de payload rulership incoherent. | Selection par `supports_rulership`; validation payload/capacite. | Test `non_eligible` et `rulership_payload_rejects_non_capable_object`. | PASS |
| AC10 | L'orchestrateur natal renseigne `chart_objects` avec house/rulership runtime. | `natal_calculation.py` appelle `RulershipPayloadEnricher` apres construction des chart objects. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`. | PASS |
| AC11 | Les sorties historiques restent disponibles. | Aucun champ historique supprime; `house_rulers`, `houses`, `planet_positions`, `dignities`, `dominant_planets` preserves. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py -k replacing_collections`; `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`; full backend suite. | PASS |
| AC12 | Les cas golden lies aux rulers restent stables. | Dominance/dignity non modifies hors consommation payload existante. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`. | PASS |
| AC13 | Aucun nouveau consommateur ne selectionne house/rulership par `object_type`. | `RulershipChartObjectSelector` selectionne par capacite. | Architecture test + scan `object_type`; seul hit classe: construction existante luminary/planet dans le builder. | PASS |
| AC14 | Aucun second resolver ou table locale de sign rulerships n'est cree. | L'enricher consomme `HouseRulerResult` et `sign_rulerships` en entree. | Scan zero-hit resolver/table + architecture test. | PASS |
| AC15 | Les payloads restent non narratifs. | Payloads limités a codes, flags, maisons, signes et sources techniques. | Scan anti interpretation: seuls hits preexistants hors nouveau payload, classes dans `evidence/validation.md`. | PASS |
| AC16 | Le schema public reste stable. | Aucun changement API/json_builder/frontend; `chart_objects` reste `SkipJsonSchema` et `exclude=True`. | `test_chart_objects_stay_out_of_public_dump_and_openapi_schema`; diff adjacent vide. | PASS |
| AC17 | L'evidence finale CS-221 est persistee. | `evidence/validation.md` cree. | `rg -n "CS-221 Final Evidence" _condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md`. | PASS |
| AC18 | Le guardrail `RG-148` est enregistre. | `RG-148` deja present dans le registre. | `rg -n "RG-148" _condamad/stories/regression-guardrails.md`. | PASS |
