# CS-198 Acceptance Traceability

| AC | Statut | Evidence code | Evidence validation |
|---|---|---|---|
| AC1 | PASS | `contracts.py` ajoute `PlanetSectCondition` immuable et valide. | `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py` |
| AC2 | PASS | `PlanetDignityScoringService` calcule un seul `ChartSectResult` et attache une condition par planete. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` |
| AC3 | PASS | Regles runtime `in_sect` day -> `diurnal`; Soleil/Jupiter/Saturne en theme day. | Test scoring + evidence runtime dans `planet-sect-validation.md`. |
| AC4 | PASS | Regles runtime `in_sect` night -> `nocturnal`; Lune/Mars en theme night. | Test scoring. |
| AC5 | PASS | Comparaison chart night vs `diurnal` donne `out_of_sect`. | Test scoring Jupiter en theme night. |
| AC6 | PASS | Comparaison chart day vs `nocturnal` donne `out_of_sect`. | Test scoring Lune en theme day. |
| AC7 | PASS | Mercure consomme la regle runtime `chart_sect_code=all` et retourne `common` / `variable_by_condition`; les planetes sans regle restent `unknown`. | Test scoring Mercury common + Uranus unknown; repository test sur seed runtime. |
| AC8 | PASS | `json_builder.py` projette `sect_condition` depuis le resultat precompute. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` |
| AC9 | PASS | Downstream sans import du calculateur. | Scan `PlanetSectConditionCalculator|planet_sect_condition_calculator` zero-hit hors domaine. |
| AC10 | PASS | Snapshots avant/apres et validation persistante. | `planet-sect-before.json`, `planet-sect-after.json`, `planet-sect-validation.md`. |
