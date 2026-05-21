# Traditional Advanced Regression Matrix

| Capability | Owner | Public / audit path | Regression evidence | Status |
|---|---|---|---|---|
| Chart sect contract | Dignities domain | `dignities.sect` | `test_sect_calculator.py`, `test_natal_result_contract.py`, `test_chart_json_builder.py`, `RG-124` | OK |
| Planet sect condition | Dignities domain | `dignities.planets[*].sect_condition` | `test_planet_dignity_scoring_service.py`, `test_chart_json_builder.py`, `RG-125` | OK |
| Advanced sect scoring | Advanced conditions | `advanced_conditions`, downstream scoring | `test_advanced_condition_engine.py`, `RG-126` | OK |
| Traditional golden cases | Backend tests/evidence | Golden case snapshots | `test_traditional_golden_cases.py`, `RG-127` | OK |
| Public JSON projection | Chart JSON builder | Public natal payload | `test_chart_json_builder.py`, `test_natal_result_contract.py`, `RG-128` | OK |
| Frontend expert panel | Frontend natal chart feature | Display from public payload | `npm --prefix frontend test -- NatalExpertPanel`, frontend scans, `RG-129` | OK |
| Dignity audit persistence | Chart result service / DB repositories | `astral_chart_planet_dignity_results` | `test_chart_result_service.py`, calculator leakage scan, `RG-130` | OK |
| Hayz and rejoicing explicit conditions | Advanced/traditional condition owners | `traditional_conditions` | `test_traditional_condition_normalizer.py`, `test_traditional_golden_cases.py`, `RG-131` | OK |
| Sect-aware triplicity | Dignities domain | Dignity score/breakdown | `test_triplicity_golden_cases.py`, `test_planet_dignity_scoring_service.py`, `RG-132` | OK |
| Benefic/malefic sect mitigation | Advanced conditions | Advanced condition facts | `test_sect_nature_mitigation_detector.py`, `test_advanced_condition_engine.py`, `RG-133` | OK |
| Score stability | Dignities/advanced/condition/dominance/adapter owners | Scores and downstream facts | Targeted backend suite: 100 passed | OK |
| Closure evidence | CS-207 evidence directory | Six required artifacts plus JSON status | Evidence checks, `python -m json.tool`, `RG-134` closure invariant | OK |
