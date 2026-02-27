# Story 20.4: Intégration SwissEph dans le pipeline natal existant

Status: done

## Title

Brancher le moteur SwissEph dans `natal_preparation_service`, `natal_calculation_service` et `build_natal_result`.

## Context

Le pipeline actuel fonctionne en simplified. Il faut intégrer accurate sans régression de contrat API ni perte de garde-fous de cohérence.

## Scope

- `natal_preparation_service`:
  - conversion `date + heure locale + timezone IANA -> UTC`
  - conversion `UTC -> JDUT`
- `natal_calculation_service`:
  - sélection engine selon ruleset/feature flag
- `natal_calculation`:
  - consommation positions + maisons SwissEph
  - conservation validations hard-fail existantes (signe/longitude, intervalle maison)
- Gestion erreurs métier vs techniques:
  - `422`: `missing_birth_time`, `missing_birth_place_resolved`, `missing_timezone`
  - `5xx`: `ephemeris_data_missing`, `swisseph_init_failed`

## Out of scope

- Refonte algorithme aspects si déjà générique.
- Évolution UI.

## Acceptance Criteria

1. **Given** un profil complet (date, heure, timezone, birth_place_resolved) **When** le calcul natal accurate est demandé **Then** le pipeline convertit en UTC puis JDUT et appelle SwissEph.
2. **Given** `birth_time` absent **When** le calcul accurate est demandé **Then** la réponse est `422` avec `code=missing_birth_time`.
3. **Given** `birth_place_resolved_id` absent **When** le calcul accurate est demandé **Then** la réponse est `422` avec `code=missing_birth_place_resolved`.
4. **Given** timezone IANA absente **When** le calcul accurate est demandé **Then** la réponse est `422` avec `code=missing_timezone` (pas d'approximation silencieuse).
5. **Given** SwissEph indisponible **When** le calcul accurate démarre **Then** la réponse est `5xx` avec `code=ephemeris_data_missing` ou `code=swisseph_init_failed`.
6. **Given** un résultat SwissEph valide **When** `build_natal_result` assemble la réponse **Then** les invariants de cohérence sont vérifiés et hard-fail en cas d'incohérence.

## Technical Notes

- Utiliser `zoneinfo` IANA et tracer la timezone effectivement utilisée.
- Lire lat/lon depuis `geo_place_resolved` comme source de vérité.
- Préserver compatibilité contrats existants (`longitude brute`, signe, maison).

## Tests

- Tests unitaires conversion temporelle locale -> UTC -> JDUT.
- Tests d'intégration erreurs `422` (`missing_*`).
- Tests d'intégration erreurs `5xx` SwissEph init/data.
- Tests de non-régression invariants pipeline.

## Rollout/Feature flag

- Flag `NATAL_ENGINE_DEFAULT=swisseph` activé après validation stories 20.1-20.3.
- Maintien de `simplified` en fallback contrôlé (story 20.7).

---

## Tasks / Subtasks

- [x] Task 1: `natal_calculation.py` — Chemin SwissEph dans `build_natal_result()`
  - [x] 1.1 Ajouter paramètres `engine: str = "simplified"`, `birth_lat: float | None = None`, `birth_lon: float | None = None`
  - [x] 1.2 Quand `engine="swisseph"`: appeler `ephemeris_provider.calculate_planets(jdut)`, filtrer selon `planet_codes`, construire `positions_raw` avec `{planet_code, longitude, sign_code}`
  - [x] 1.3 Quand `engine="swisseph"`: appeler `houses_provider.calculate_houses(jdut, lat, lon)`, construire `houses_raw` depuis `HouseData.cusps` en `{number, cusp_longitude}`
  - [x] 1.4 Conserver toutes les validations hard-fail existantes (signe/longitude, intervalle maison) pour les deux engines
  - [x] 1.5 Utiliser `effective_house_system` dans les détails d'erreur de cohérence (`"placidus"` pour swisseph, `HOUSE_SYSTEM_CODE` pour simplified)

- [x] Task 2: `natal_calculation_service.py` — Sélection de l'engine
  - [x] 2.1 Ajouter paramètre `accurate: bool = False` à `calculate()`
  - [x] 2.2 Sélectionner engine: `"swisseph"` si `accurate=True` ET `settings.swisseph_enabled=True`, sinon `"simplified"`
  - [x] 2.3 Si engine=swisseph: vérifier `get_bootstrap_result()` — lever l'erreur de bootstrap stockée si échec (`EphemerisDataMissingError` ou `SwissEphInitError`)
  - [x] 2.4 Passer `engine=engine`, `birth_lat=birth_input.birth_lat`, `birth_lon=birth_input.birth_lon` à `build_natal_result()`

- [x] Task 3: `user_natal_chart_service.py` — Propagation accurate + missing_timezone
  - [x] 3.1 Ajouter vérification `missing_timezone` en mode accurate si `profile.birth_timezone` est absent/None (avant création de `BirthInput`)
  - [x] 3.2 Passer `accurate=accurate` à `NatalCalculationService.calculate()`

- [x] Task 4: Tests unitaires `backend/app/tests/unit/test_natal_pipeline_swisseph.py`
  - [x] 4.1 Test sélection engine swisseph quand `accurate=True` et `swisseph_enabled=True`
  - [x] 4.2 Test sélection engine simplified quand `accurate=False`
  - [x] 4.3 Test sélection engine simplified quand `accurate=True` mais `swisseph_enabled=False`
  - [x] 4.4 Test erreur bootstrap swisseph → `EphemerisDataMissingError` propagée
  - [x] 4.5 Test `build_natal_result(engine="swisseph")` — appelle `calculate_planets` et `calculate_houses` (mock)
  - [x] 4.6 Test `build_natal_result(engine="swisseph")` — invariants de cohérence préservés (mock données valides)
  - [x] 4.7 Test `missing_timezone` dans `user_natal_chart_service` en mode accurate
  - [x] 4.8 Test conversion temporelle locale → UTC → JDUT (natif `zoneinfo`)

- [x] Task 5: Tests d'intégration `backend/app/tests/integration/test_natal_chart_accurate_api.py`
  - [x] 5.1 Test `generate_for_user(accurate=True)` sans `birth_place_resolved_id` → `missing_birth_place_resolved`
  - [x] 5.2 Test `generate_for_user(accurate=True)` sans `birth_time` → `missing_birth_time`
  - [x] 5.3 Test `generate_for_user(accurate=True)` avec swisseph disabled → fallback simplified OK
  - [x] 5.4 Test non-régression: `generate_for_user(accurate=False)` toujours fonctionnel

## Dev Notes

### Architecture
- `natal_calculation.py` → `build_natal_result()`: nouveau paramètre `engine` contrôle quelle branche de calcul est utilisée.
- Pour `engine="swisseph"`:
  - Positions planétaires : `ephemeris_provider.calculate_planets(jdut)` → `list[PlanetData]` → filtrer selon `planet_codes` référence → dict `{planet_code, longitude, sign_code}`
  - Maisons: `houses_provider.calculate_houses(jdut, lat, lon)` → `HouseData` → dict `{number, cusp_longitude}` depuis `HouseData.cusps[house_number - 1]`
  - Toutes les validations hard-fail existantes restent identiques (sign/longitude, house interval)
- `natal_calculation_service.py`: sélection engine conditionnelle, vérification bootstrap avant appel SwissEph.
- `user_natal_chart_service.py`: déjà gère `missing_birth_time` (ligne 212) et `missing_birth_place_resolved` (lignes 196-201). Ajouter `missing_timezone`.

### Patterns utilisés
- Import des providers SwissEph depuis le module (pas lazy intra-fonction) pour lisibilité, compatible mock via `monkeypatch`.
- `settings.swisseph_enabled` + `accurate` → engine selection.
- `get_bootstrap_result()` → vérification état bootstrap avant tout appel.
- Erreurs SwissEph (`EphemerisDataMissingError`, `SwissEphInitError`) déjà enregistrées comme handlers 503 dans `main.py` (stories 20-1/20-2).

### Mapping PlanetData → positions_raw
```python
# calculate_planets retourne list[PlanetData] avec planet_id in {sun, moon, mercury, ...}
# planet_codes de la référence data : ["sun", "moon", "mercury"] (par défaut)
planet_data_by_id = {pd.planet_id: pd for pd in calculate_planets(jdut)}
positions_raw = [
    {
        "planet_code": code,
        "longitude": planet_data_by_id[code].longitude,  # déjà [0, 360)
        "sign_code": _sign_from_longitude(planet_data_by_id[code].longitude),
    }
    for code in planet_codes
    if code in planet_data_by_id
]
```

### Mapping HouseData → houses_raw
```python
# houses_provider.calculate_houses retourne HouseData avec cusps = tuple 12 floats
# cusps[0] = maison 1, ..., cusps[11] = maison 12
houses_raw = [
    {"number": number, "cusp_longitude": house_data.cusps[number - 1]}
    for number in house_numbers
    if 1 <= number <= 12
]
```

### `missing_timezone` (AC4)
- Dans `user_natal_chart_service.generate_for_user()`, avant création de `BirthInput`:
  ```python
  if accurate and not profile.birth_timezone:
      raise UserNatalChartServiceError(code="missing_timezone", ...)
  ```
- `birth_timezone` est `Mapped[str]` (non-nullable DB), donc normalement toujours présent. Vérification défensive.

## Dev Agent Record

### Implementation Plan

1. `natal_calculation.py` — SwissEph path dans `build_natal_result()`
2. `natal_calculation_service.py` — sélection engine + bootstrap check
3. `user_natal_chart_service.py` — propagation accurate + missing_timezone
4. Tests unitaires `test_natal_pipeline_swisseph.py`
5. Tests d'intégration `test_natal_chart_accurate_api.py`
6. Run complet test suite, fix regressions

### Completion Notes

- Implémentation complète en 3 fichiers de production + 2 fichiers de tests.
- **Ordre des vérifications 422** : `missing_birth_place_resolved` est contrôlé *avant* `missing_birth_time` dans `generate_for_user()` car la résolution de lieu est une pré-condition pour accurate. Les tests d'intégration ont été adaptés en conséquence.
- **Mocks existants mis à jour** : 4 tests unitaires pré-existants mis à jour pour accepter `accurate: bool = False`.
- **`missing_timezone` défensif** : vérification ajoutée en mode accurate.
- **Validation de plage de date** : ajout d'une validation dans `natal_preparation.py` pour garantir que le Julian Day est dans la plage supportée (-3000 à 3000 AD).
- **Métadonnées dynamiques du système de maisons** : ajout du champ `house_system` dans `NatalResult` pour refléter dynamiquement le système utilisé (ex: "placidus" pour swisseph) au lieu de hardcoder une constante dans l'API.
- Le flag `SWISSEPH_ENABLED=False` produit un fallback transparent vers le moteur simplified.
- 20 tests écrits, tous verts.

## File List

- `backend/app/domain/astrology/natal_calculation.py` — ajout helpers, paramètres `engine/birth_lat/birth_lon`, et champ `house_system` dans `NatalResult`.
- `backend/app/services/natal_calculation_service.py` — paramètre `accurate`, sélection engine, vérification bootstrap.
- `backend/app/services/user_natal_chart_service.py` — vérification `missing_timezone`, propagation `accurate`, utilisation du `house_system` dynamique.
- `backend/app/domain/astrology/natal_preparation.py` — ajout de la validation de plage de date (JD).
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py` — 16 tests unitaires (nouveau fichier).
- `backend/app/tests/integration/test_natal_chart_accurate_api.py` — 4 tests d'intégration (nouveau fichier).
- `backend/app/tests/unit/test_user_natal_chart_service.py` — mocks mis à jour.
- `backend/app/tests/unit/test_geo_place_resolved.py` — mocks mis à jour.

## Change Log

| Date       | Auteur       | Description                                                        |
|------------|--------------|--------------------------------------------------------------------|
| 2026-02-26 | Dev Agent    | Implémentation story 20-4 : intégration SwissEph pipeline natal   |
| 2026-02-27 | Dev Agent    | Fix review: propagation `frame/lat/lon/altitude_m` vers `_build_swisseph_positions` pour activer le vrai mode topocentrique planétaire |
