# Story 20.5: Metadata API complète pour la traçabilité du calcul accurate

Status: done

## Title

Exposer une metadata de calcul complète et stable pour auditabilité et reproductibilité.

## Context

Les résultats doivent être traçables: même input et mêmes paramètres doivent redonner le même output.

## Scope

- Étendre `metadata` de la réponse natal chart avec:
  - `engine`
  - `ephemeris`
  - `zodiac`
  - `ayanamsa` (si sidéral)
  - `frame`
  - `house_system`
  - `reference_version`
  - `ruleset_version`
  - `timezone_used`
  - `ephemeris_path_version`
- Garantir la présence des valeurs par défaut explicites:
  - `zodiac=tropical`
  - `frame=geocentric`
  - `house_system=placidus`

## Out of scope

- Affichage UI de tous les champs metadata (story 20.8 couvre le minimum).

## Acceptance Criteria

1. **Given** un calcul accurate par défaut **When** l'API répond **Then** metadata contient `engine=swisseph`, `zodiac=tropical`, `frame=geocentric`, `house_system=placidus`.
2. **Given** un calcul sidéral **When** l'API répond **Then** metadata contient `zodiac=sidereal` et `ayanamsa` (Lahiri par défaut si non fourni).
3. **Given** un calcul topocentrique **When** l'API répond **Then** metadata contient `frame=topocentric` et l'altitude appliquée (0 si absente).
4. **Given** une requête calculée **When** metadata est sérialisée **Then** `reference_version`, `ruleset_version`, `timezone_used`, `ephemeris_path_version` sont toujours présents.

## Technical Notes

- Versionner le schéma metadata si nécessaire (`metadata.schema_version`) pour compat future.
- Éviter toute donnée PII dans metadata.
- Assurer rétrocompatibilité avec consommateurs front existants.

## Tests

- Tests unitaires serializer metadata.
- Tests d'intégration API tropical/sidéral/topocentrique.
- Test de non-régression sur champs historiques déjà présents.

## Rollout/Feature flag

- Aucune bascule UI obligatoire pour publier ces champs.
- Peut être activé dès que 20.4 est merge.

---

## Tasks / Subtasks

- [x] Task 1: `natal_calculation.py` — Étendre `NatalResult` + params de calcul dans `build_natal_result()`
  - [x] 1.1 Ajouter champs à `NatalResult`: `engine`, `zodiac`, `frame`, `ayanamsa`, `ephemeris_path_version` (avec defaults backward-compat)
  - [x] 1.2 Mettre à jour `_build_swisseph_positions()`: ajouter params `zodiac`, `ayanamsa`, passer à `calculate_planets()`
  - [x] 1.3 Mettre à jour `_build_swisseph_houses()`: ajouter params `frame`, `altitude_m`, passer à `calculate_houses()`
  - [x] 1.4 Mettre à jour `build_natal_result()`: ajouter params `zodiac`, `ayanamsa`, `frame`, `altitude_m`, `ephemeris_path_version`; populer les nouveaux champs de `NatalResult`

- [x] Task 2: `natal_calculation_service.py` — Propager les params + extraire `ephemeris_path_version`
  - [x] 2.1 Ajouter params `zodiac`, `ayanamsa`, `frame`, `altitude_m` à `calculate()`
  - [x] 2.2 Extraire `ephemeris_path_version` depuis le bootstrap result (lorsque swisseph actif)
  - [x] 2.3 Passer tous les params à `build_natal_result()`

- [x] Task 3: `user_natal_chart_service.py` — Étendre `UserNatalChartMetadata` + propager
  - [x] 3.1 Ajouter champs à `UserNatalChartMetadata`: `engine`, `zodiac`, `frame`, `ayanamsa`, `timezone_used`, `ephemeris_path_version`
  - [x] 3.2 Mettre à jour `generate_for_user()`: populer tous les nouveaux champs depuis `result`
  - [x] 3.3 Mettre à jour `get_latest_for_user()`: reconstruire tous les nouveaux champs depuis `result`

- [x] Task 4: Tests unitaires `backend/app/tests/unit/test_natal_metadata.py`
  - [x] 4.1 Test `NatalResult` par défaut: `engine=simplified`, `zodiac=tropical`, `frame=geocentric`, `ayanamsa=None`
  - [x] 4.2 Test `build_natal_result()` avec engine swisseph: `engine=swisseph` dans result (mock providers)
  - [x] 4.3 Test metadata sidereal: `zodiac=sidereal`, `ayanamsa=lahiri` dans `NatalResult`
  - [x] 4.4 Test metadata topocentric: `frame=topocentric` dans `NatalResult`
  - [x] 4.5 Test `timezone_used` dans `UserNatalChartMetadata` depuis `prepared_input.birth_timezone`
  - [x] 4.6 Test `ephemeris_path_version` présent (None pour simplified, string pour swisseph)
  - [x] 4.7 Test rétrocompatibilité: champs historiques (`reference_version`, `ruleset_version`, `house_system`) préservés
  - [x] 4.8 Test non-régression: `NatalResult.model_validate()` accepte payloads anciens sans les nouveaux champs

- [x] Task 5: Tests d'intégration `backend/app/tests/integration/test_natal_chart_accurate_api.py`
  - [x] 5.1 Test AC4: tous les champs obligatoires toujours présents dans `metadata` (`reference_version`, `ruleset_version`, `timezone_used`, `ephemeris_path_version`)
  - [x] 5.2 Test defaults simplified: `engine=simplified`, `zodiac=tropical`, `frame=geocentric`
  - [x] 5.3 Test `get_latest_for_user()` reconstruit correctement la metadata depuis DB
  - [x] 5.4 [AI-Review] Test AC2 sidereal mode (zodiac/ayanamsa)
  - [x] 5.5 [AI-Review] Test AC3 topocentric mode (frame/altitude_m)

- [x] Task 6: Run tests + validation DoD
  - [x] 6.1 Run suite complète — zéro régression (436 unit tests passed, 75 story-specific tests passed)
  - [x] 6.2 Valider tous les ACs satisfaits

- [x] Task 7: [AI-Review] API Exposure
  - [x] 7.1 Exposer les paramètres de calcul dans `NatalChartGenerateRequest` (users router)
  - [x] 7.2 Exposer les paramètres de calcul dans `NatalCalculateRequest` (astrology-engine router)
  - [x] 7.3 Propager les paramètres depuis les routers vers `UserNatalChartService` et `NatalCalculationService`

## Dev Notes

### Architecture

- `NatalResult` dans `natal_calculation.py` est le modèle central — il doit contenir tous les params de calcul pour la traçabilité et reproductibilité.
- `engine`, `zodiac`, `frame`, `ayanamsa`, `ephemeris_path_version` sont ajoutés à `NatalResult` avec des defaults backward-compat pour les enregistrements DB existants.
- `timezone_used` n'est PAS stocké redondamment dans `NatalResult` car `prepared_input.birth_timezone` est déjà disponible — on le dérive au niveau service lors de la construction de `UserNatalChartMetadata`.
- `ephemeris_path_version` est extrait depuis `get_bootstrap_result().path_version` dans `NatalCalculationService.calculate()` et stocké dans `NatalResult`.

### Backward compat DB

Les enregistrements DB existants sont stockés sans les nouveaux champs. `NatalResult.model_validate()` assignera les defaults:
- `engine="simplified"` ✓
- `zodiac="tropical"` ✓
- `frame="geocentric"` ✓
- `ayanamsa=None` ✓
- `ephemeris_path_version=None` ✓

### Propagation des params

```
NatalCalculationService.calculate(zodiac, ayanamsa, frame, altitude_m)
  → bootstrap result → ephemeris_path_version
  → build_natal_result(zodiac, ayanamsa, frame, altitude_m, ephemeris_path_version)
    → _build_swisseph_positions(jdut, planet_codes, zodiac, ayanamsa)
    → _build_swisseph_houses(jdut, lat, lon, house_numbers, frame, altitude_m)
  → NatalResult(engine, zodiac, frame, ayanamsa, ephemeris_path_version, ...)

UserNatalChartService.generate_for_user()
  → UserNatalChartMetadata(
      engine=result.engine,
      zodiac=result.zodiac,
      frame=result.frame,
      ayanamsa=result.ayanamsa,
      timezone_used=result.prepared_input.birth_timezone,
      ephemeris_path_version=result.ephemeris_path_version,
      reference_version=result.reference_version,
      ruleset_version=result.ruleset_version,
      house_system=result.house_system,
    )
```

## Dev Agent Record

### Implementation Plan

1. Étendre `NatalResult` + helpers dans `natal_calculation.py`
2. Propager params dans `natal_calculation_service.py`
3. Étendre `UserNatalChartMetadata` dans `user_natal_chart_service.py`
4. Tests unitaires `test_natal_metadata.py`
5. Tests d'intégration (extension du fichier existant)
6. Run suite complète

### Code Review Fixes (2026-02-26)
- Étendu `UserNatalChartService.generate_for_user` pour accepter params de calcul.
- Mis à jour `NatalChartGenerateRequest` et `NatalCalculateRequest` models pour API exposure.
- Ajouté tests d'intégration pour sidereal et topocentric modes dans `test_natal_chart_accurate_api.py`.

## File List

### Modified
- `backend/app/domain/astrology/natal_calculation.py` — Étendu `NatalResult` (engine/zodiac/frame/ayanamsa/ephemeris_path_version); mis à jour `_build_swisseph_positions()`, `_build_swisseph_houses()`, `build_natal_result()`
- `backend/app/services/natal_calculation_service.py` — Ajout params zodiac/ayanamsa/frame/altitude_m à `calculate()`; extraction `ephemeris_path_version` depuis bootstrap
- `backend/app/services/user_natal_chart_service.py` — Étendu `UserNatalChartMetadata`; mis à jour `generate_for_user()` et `get_latest_for_user()`
- `backend/app/api/v1/routers/users.py` — Exposure des params dans `NatalChartGenerateRequest` et `generate_me_natal_chart`
- `backend/app/api/v1/routers/astrology_engine.py` — Exposure des params dans `NatalCalculateRequest` et `calculate_natal`
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py` — Mocks mis à jour avec `**kwargs` pour compatibilité nouveaux params
- `backend/app/tests/integration/test_natal_chart_accurate_api.py` — 5 nouveaux tests story 20-5 (AC4, defaults, DB round-trip, sidereal, topocentric)
- `backend/app/tests/unit/test_natal_interpretation_service.py` — Fix régression story-20-4: `house_system=` ajouté à `_make_natal_result()`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py` — Fix régression story-20-4: `house_system=` ajouté à `_make_natal_result()`

### Created
- `backend/app/tests/unit/test_natal_metadata.py` — 14 tests unitaires metadata (NatalResult defaults, backward compat, swisseph/sidereal/topocentric, timezone_used, ephemeris_path_version)

## Change Log

| Date       | Auteur    | Description                                      |
|------------|-----------|--------------------------------------------------|
| 2026-02-26 | Dev Agent | Démarrage story 20-5 : metadata API complète     |
| 2026-02-26 | Dev Agent | Implémentation complète tasks 1-6; 436 unit tests pass; fix régressions story-20-4 |
| 2026-02-26 | Reviewer  | Fix API exposure & missing integration tests (AC2/AC3) |
