# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le fichier `solar_phase_relation_calculator.py` existe. | Nouveau module pur. | `Test-Path`, test cible. | PASS |
| AC2 | `calculate_solar_phase_relation` est importable. | Export package et module. | Test cible. | PASS |
| AC3 | `SolarPhaseRelationThresholds` expose la tolerance par defaut. | Contrat dataclass dans `contracts.py`. | Test contrats + test cible. | PASS |
| AC4 | `SolarPhaseRelationThresholds` rejette les tolerances invalides. | Validation `__post_init__`. | Test contrats. | PASS |
| AC5 | Les longitudes sont normalisees dans le cercle zodiacal. | Helper local pur. | Test cible. | PASS |
| AC6 | L'angle relatif applique `(planet - sun) % 360.0`. | Calculateur. | Test cible. | PASS |
| AC7 | `CONJUNCT_SOLAR` est retourne pour angle `0`. | Calculateur. | Test cible. | PASS |
| AC8 | `CONJUNCT_SOLAR` respecte la tolerance autour de `0/360`. | Calculateur. | Test cible. | PASS |
| AC9 | `OCCIDENTAL` est retourne pour l'hemicycle occidental. | Calculateur. | Test cible. | PASS |
| AC10 | L'opposition exacte est `OCCIDENTAL`. | Convention documentee dans la docstring. | Test cible. | PASS |
| AC11 | `ORIENTAL` est retourne pour l'hemicycle oriental. | Calculateur. | Test cible. | PASS |
| AC12 | `planet_key == "sun"` retourne `CONJUNCT_SOLAR`. | Branche explicite Soleil. | Test cible. | PASS |
| AC13 | Le resultat utilise `PlanetarySolarPhaseRelation`. | Retour contractuel canonique. | Test cible. | PASS |
| AC14 | Le calculateur ne produit pas `UNKNOWN` pour des longitudes valides. | Branches limitees aux trois relations autorisees. | Test cible. | PASS |
| AC15 | La fonction batch retourne une relation par entree. | `calculate_solar_phase_relations`. | Test cible. | PASS |
| AC16 | Le calculateur exclut les dependances interdites. | Imports limites a stdlib + contrats package. | Scans imports. | PASS |
| AC17 | Le calculateur exclut le scoring. | Aucun symbole de scoring. | Scan scoring. | PASS |
| AC18 | Le calculateur exclut l'interpretation. | Aucun symbole narratif. | Scan interpretation. | PASS |
| AC19 | Le calculateur exclut la visibilite avancee. | Aucun symbole heliacal/visibility. | Scan visibilite avancee. | PASS |
| AC20 | Aucune integration adjacente n'est ajoutee hors package. | Aucun fichier adjacent modifie. | Scan public symbols + diff adjacent. | PASS |
| AC21 | La qualite backend passe dans le venv. | Format, lint, suite complete. | `ruff format .`, `ruff check .`, `pytest -q`. | PASS |
