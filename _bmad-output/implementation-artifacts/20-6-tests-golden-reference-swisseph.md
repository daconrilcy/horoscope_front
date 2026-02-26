# Story 20.6: Golden tests de référence SwissEph

Status: review

## Title

Mettre en place une suite de tests golden pour verrouiller la précision et la stabilité temporelle du moteur SwissEph.

## Context

L'introduction d'un moteur accurate nécessite des références numériques fixes pour détecter les dérives de calcul.

## Scope

- Ajouter 3 cas golden fixes (date/heure/lieu) avec assertions:
  - `Sun.longitude`
  - `Moon.longitude`
  - `Mercury.longitude`
  - tolérance absolue `0.01°`
- Ajouter un cas timezone historique `Europe/Paris` en 1973.
- Ajouter un cas rétrograde connu (`speed_longitude < 0`).
- Séparer les fixtures golden du code métier.

## Out of scope

- Benchmark performance large échelle.
- Golden tests UI.

## Acceptance Criteria

1. **Given** les 3 cas golden définis **When** les tests sont exécutés **Then** les longitudes Sun/Moon/Mercury respectent une tolérance de `0.01°`.
2. **Given** un cas historique `Europe/Paris` en 1973 **When** la conversion timezone est appliquée **Then** le `JDUT` et les positions résultantes sont conformes aux valeurs de référence.
3. **Given** un cas rétrograde connu **When** le calcul est exécuté **Then** `speed_longitude < 0` et `is_retrograde=true`.
4. **Given** une régression de précision au-delà de `0.01°` **When** la CI lance les tests **Then** la suite échoue explicitement.

## Technical Notes

- Documenter l'origine des valeurs golden (dataset SwissEph + date de génération).
- Geler précisément les paramètres de calcul dans les fixtures (zodiac/frame/house_system/timezone).
- Éviter les tests fragiles dépendants de l'heure système locale.

## Tests

- `pytest` marqueur dédié `@pytest.mark.golden`.
- Tests unitaires conversion date locale -> JDUT sur les 3 cas.
- Tests d'intégration moteur accurate avec fixtures golden.

## Rollout/Feature flag

- Obligatoire avant activation SwissEph par défaut en production.
- Exécution en CI sur chaque PR touchant pipeline natal.

---

## Tasks / Subtasks

- [x] Task 1: Créer le module de fixtures golden séparé du code métier
  - [x] 1.1 Créer `backend/app/tests/golden/__init__.py`
  - [x] 1.2 Créer `backend/app/tests/golden/fixtures.py` avec `PlanetGolden` et `GoldenCase` dataclasses
  - [x] 1.3 Définir 5 cas golden (3 cas principaux + TZ historique 1973 + Mercure rétrograde)
  - [x] 1.4 Documenter l'origine des valeurs (pyswisseph Moshier, 2026-02-26)

- [x] Task 2: Créer le fichier de tests golden avec marqueur dédié
  - [x] 2.1 Créer `backend/app/tests/unit/test_golden_reference_swisseph.py`
  - [x] 2.2 Tests unitaires conversion date locale → JDUT pour les 3 cas (sans pyswisseph)
  - [x] 2.3 Tests golden intégration moteur via `calculate_planets()` (avec pyswisseph réel)
  - [x] 2.4 Assertions explicites tolérance 0.01° (AC4)

- [x] Task 3: Enregistrer le marqueur pytest `golden`
  - [x] 3.1 Ajouter `markers = [...]` dans `[tool.pytest.ini_options]` de `backend/pyproject.toml`

- [x] Task 4: Valider que tous les ACs sont satisfaits
  - [x] 4.1 AC1 : 3 cas Sun/Moon/Mercury dans ± 0.01° ✅
  - [x] 4.2 AC2 : Cas 1973 Europe/Paris UTC+1 historique → offset +01:00, JDUT correct ✅
  - [x] 4.3 AC3 : Mercury rétrograde (speed=-0.005020°/j, is_retrograde=True) ✅ + Saturn J2000 + Mars 1980
  - [x] 4.4 AC4 : Régression > 0.01° → assertion failure explicite ✅

- [x] Task 5: Review Follow-ups (AI)
  - [x] 5.1 Tighten JD_TOLERANCE to 1e-6 (approx 0.08s) for higher precision verification.
  - [x] 5.2 Add precision assertions for `speed_longitude` (tolerance 0.0001°/j).
  - [x] 5.3 Translate pytest marker description to English in `pyproject.toml`.

## Dev Notes

### Architecture

- **`app/tests/golden/`** : Module dédié pour les fixtures golden, séparé du code métier.
  - `fixtures.py` : `PlanetGolden` (dataclass frozen), `GoldenCase` (dataclass frozen), 5 cas nommés.
  - `__init__.py` : module marker vide.
- **`app/tests/unit/test_golden_reference_swisseph.py`** : Fichier de tests en deux catégories :
  - `TestDateConversionGolden` : Unit tests sans pyswisseph (testent `prepare_birth_data()`).
  - `TestGoldenPlanetPositions` : Integration tests avec pyswisseph réel (testent `calculate_planets()`).

### Éphéméride utilisée

Éphéméride **Moshier intégrée** de pyswisseph (aucun fichier .se1 requis). Précision : ±1-2 arcseconds
pour les planètes majeures dans l'intervalle -3000/+3000. La tolérance de 0.01° (36 arcseconds) est
largement supérieure à l'erreur Moshier, rendant les tests stables dans le temps.

### Cas 1973 Europe/Paris (AC2)

La France n'a adopté l'heure d'été qu'en 1976 (choc pétrolier 1973). En juillet 1973,
`Europe/Paris = CET = UTC+1` (pas UTC+2). La base IANA (tzdata) contient ces règles historiques.
Le test vérifie `"+01:00" in birth_datetime_local` et `"T08:00:00" in birth_datetime_utc`.

### Marqueur `@pytest.mark.golden`

Enregistré dans `pyproject.toml` pour éviter `PytestUnknownMarkWarning`. Les tests moteur sont
automatiquement ignorés si pyswisseph n'est pas importable (skip, pas d'erreur).

### 2 régressions pré-existantes (hors scope 20-6)

Les tests `test_natal_service_propagates_birth_lat_lon_to_birth_input` et
`test_natal_service_propagates_none_lat_lon_when_absent` dans `test_geo_place_resolved.py`
échouaient déjà avant story 20-6 (cassés par story 20-5 qui a ajouté `zodiac` comme kwarg).
Ces échecs sont hors scope et documentés.

## Dev Agent Record

### Implementation Plan

1. `app/tests/golden/__init__.py` + `fixtures.py` — fixtures frozen séparées
2. `app/tests/unit/test_golden_reference_swisseph.py` — tests unit (JD) + integration (planets)
3. `backend/pyproject.toml` — enregistrement du marqueur `golden`
4. Validation des 4 ACs + linting ruff + suite de régression

### Completion Notes

Implémentation complète le 2026-02-26 :

- **`app/tests/golden/`** : Nouveau module créé avec `PlanetGolden` et `GoldenCase` (frozen dataclasses).
  5 cas golden documentés, valeurs gelées générées par pyswisseph Moshier le 2026-02-26.
- **`app/tests/unit/test_golden_reference_swisseph.py`** : 18 tests (17 pass, 1 skip attendu).
  - 6 tests unitaires conversion date → JDUT (sans pyswisseph).
  - 12 tests d'intégration moteur avec pyswisseph réel (marqueur `@pytest.mark.golden`).
- **`backend/pyproject.toml`** : Marqueur `golden` enregistré.

**Acceptance Criteria satisfaits :**
- AC1 ✅ : 3 cas J2000/1990/1980 — Sun/Moon/Mercury dans ± 0.01° (paramétrisé).
- AC2 ✅ : 1973-07-04 Europe/Paris → offset +01:00 vérifié, JDUT = 2441867.833333 confirmé.
- AC3 ✅ : Mercury rétrograde 2000-07-17 (speed=-0.005020, is_retrograde=True) + Saturn J2000 + Mars 1980.
- AC4 ✅ : Message d'erreur explicite "RÉGRESSION DE PRÉCISION" avec valeurs attendue/obtenue/delta.

**Résultats tests :** 17 passed, 1 skipped (cas Mercury sans valeur sun — comportement attendu).
**Linting ruff :** 0 erreur.
**Régressions :** 2 pré-existantes hors scope (test_geo_place_resolved.py, cassées par story 20-5).

## File List

- `backend/app/tests/golden/__init__.py` (nouveau)
- `backend/app/tests/golden/fixtures.py` (nouveau)
- `backend/app/tests/unit/test_golden_reference_swisseph.py` (nouveau)
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py` (nouveau)
- `backend/app/tests/integration/test_natal_chart_accurate_api.py` (nouveau)
- `backend/pyproject.toml` (modifié — ajout marqueur `golden`)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié — review)

## Change Log

- 2026-02-26 : Story 20-6 implémentée — Golden tests de référence SwissEph.
  - Nouveau module `app/tests/golden/` avec 5 fixtures golden (3 cas principaux + TZ 1973 + rétrograde).
  - Nouveau fichier `test_golden_reference_swisseph.py` : 18 tests golden marqués `@pytest.mark.golden`.
  - Tests unitaires conversion JD + tests intégration `calculate_planets()` avec pyswisseph réel.
  - Marqueur pytest `golden` enregistré dans `pyproject.toml`.
  - 17 tests passent, 0 régression introduite, linting propre.
