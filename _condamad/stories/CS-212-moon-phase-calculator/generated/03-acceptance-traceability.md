# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `moon_phase_calculator.py` existe. | Nouveau calculateur. | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` PASS. | PASS |
| AC2 | Fonction importable depuis le package public. | Export `calculate_moon_phase_condition`. | Test d'import cible PASS. | PASS |
| AC3 | Retourne `MoonPhaseCondition` pour longitudes finies. | Fonction publique pure. | Test cible PASS. | PASS |
| AC4 | Normalisation longitude canonique. | Helper de normalisation. | Cas `361`, `-1`, `720` PASS. | PASS |
| AC5 | Angle `(moon - sun) % 360.0`. | Calcul angle relatif avec snap des angles majeurs. | Cas passage zero et decimaux enroules PASS. | PASS |
| AC6 | Angles exacts majeurs en `EXACT`. | Classification waxing/waning. | Tests `0`, `180`, `360.1/0.1`, `540.1/0.1` PASS. | PASS |
| AC7 | Hemisphere croissant en `WAXING`. | Classification waxing/waning. | Test cible PASS. | PASS |
| AC8 | Hemisphere decroissant en `WANING`. | Classification waxing/waning. | Test cible PASS. | PASS |
| AC9 | `NEW_MOON` respecte les bornes. | Resolution phase. | Tests de bornes PASS. | PASS |
| AC10 | `FULL_MOON` respecte les bornes. | Resolution phase. | Tests de bornes PASS. | PASS |
| AC11 | Phases intermediaires respectent les bornes. | Resolution phase. | Tests parametres PASS. | PASS |
| AC12 | `BALSAMIC` respecte la plage prioritaire. | Resolution phase priorisee. | Tests `315`, `337.5` PASS. | PASS |
| AC13 | Ordre de priorite applique. | Resolution phase priorisee. | Tests `350`, `180`, `330` PASS. | PASS |
| AC14 | Illumination applique `(1 - cos(angle_rad)) / 2`. | Calcul illumination. | `pytest.approx` PASS. | PASS |
| AC15 | `phase_index` stable `0..8`. | Mapping phase index. | Test parametre PASS. | PASS |
| AC16 | Longitudes non finies levent `ValueError`. | Validation `isfinite`. | Tests `nan`, `inf` PASS. | PASS |
| AC17 | Dependances interdites exclues. | Imports limites. | Scan imports interdits zero hit. | PASS |
| AC18 | Scoring exclu. | Aucun symbole scoring. | Scan scoring zero hit. | PASS |
| AC19 | Interpretation exclue. | Aucun symbole narratif. | Scan interpretation zero hit. | PASS |
| AC20 | Domaines hors scope exclus. | Aucun symbole hors scope. | Scan hors scope zero hit. | PASS |
| AC21 | Aucune integration adjacente ajoutee. | Aucun changement adjacent. | Scan symboles adjacent zero hit + diff adjacent vide. | PASS |
| AC22 | Qualite backend passe dans le venv. | Aucun impact hors scope. | `ruff format .`, `ruff check .`, `pytest -q` PASS. | PASS |
