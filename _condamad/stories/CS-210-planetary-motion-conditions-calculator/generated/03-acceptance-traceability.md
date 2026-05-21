# Acceptance Traceability - CS-210

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Fonction principale importable depuis le module calculateur. | `planetary_motion_calculator.py` et exports ajoutes. | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py` PASS. | PASS |
| AC2 | `PlanetaryMotionProfile` expose le contrat du brief. | Dataclass ajoutee dans `contracts.py` avec validation des seuils finis. | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py` PASS. | PASS |
| AC3 | Direction selon les seuils. | Direct/retrograde/stationary implementes. | Tests direction PASS. | PASS |
| AC4 | Stationnarite prioritaire. | Seuil absolu applique avant le signe. | Tests direction PASS. | PASS |
| AC5 | Vitesse zero stationnaire. | Zero classe `STATIONARY`. | Test vitesse zero PASS. | PASS |
| AC6 | Ratio `abs(speed) / mean_speed`. | Ratio calcule si mean speed valide. | Tests ratio PASS. | PASS |
| AC7 | Etats de vitesse configurables. | Classifier par seuils du profil. | Tests parametrises PASS. | PASS |
| AC8 | Mean speed invalide -> `UNKNOWN`. | Ratio `None`, speed state `UNKNOWN`. | Tests mean speed invalide PASS. | PASS |
| AC9 | Catalogue par defaut conforme. | `planetary_motion_profiles.py` ajoute. | Tests catalogue PASS. | PASS |
| AC10 | Lot leve `ValueError` si profil manquant. | Fonction batch explicite; mismatch profil/planete refuse. | Tests profil manquant et mismatch PASS. | PASS |
| AC11 | Interdits exclus du calculateur. | Aucun import/symbole interdit. | Scans `rg` zero-hit PASS. | PASS |
| AC12 | Aucune integration adjacente. | Pas de changement hors package/test/story. | `git diff --` surfaces adjacentes vide PASS. | PASS |
| AC13 | Qualite backend dans le venv. | Formatting/lint/tests. | `ruff format .`, `ruff check .`, `pytest -q` PASS avec 2853 tests. | PASS |
