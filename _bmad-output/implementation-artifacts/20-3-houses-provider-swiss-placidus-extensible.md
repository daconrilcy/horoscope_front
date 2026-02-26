# Story 20.3: Provider maisons SwissEph (Placidus par défaut, extensible)

Status: done

## Title

Créer un provider de maisons natales via SwissEph (`houses_ex`) avec Placidus par défaut et architecture extensible.

## Context

Le moteur accurate doit calculer cuspides 1..12 et angles (ASC/MC) en cohérence avec les conventions actuelles d'intervalle `[start, end)`.

## Scope

- Implémenter provider maisons via `swe.houses_ex` (ou équivalent SwissEph stable).
- `house_system=placidus` par défaut.
- Sortie attendue:
  - cuspides 1..12 (longitudes 0..360)
  - `ascendant_longitude`
  - `mc_longitude`
- Préparer extension future pour `equal` et `whole_sign` sans casser l'API interne.
- Support frame:
  - `geocentric` par défaut
  - `topocentric` optionnel (altitude `0` si absente)

## Out of scope

- UI des maisons.
- Bascule produit publique vers Equal/Whole Sign.

## Acceptance Criteria

1. **Given** une date/heure/coordonnées valides **When** le provider maisons est exécuté **Then** les 12 cuspides + ASC/MC sont retournés et normalisés dans `[0, 360)`.
2. **Given** aucun `house_system` fourni **When** le provider est appelé **Then** `house_system=placidus` est appliqué par défaut.
3. **Given** `frame=topocentric` avec altitude absente **When** le calcul est lancé **Then** altitude `0` est utilisée explicitement.
4. **Given** une tentative de house system non supporté **When** l'appel est exécuté **Then** l'erreur est fonctionnelle `422` avec code explicite (ex: `unsupported_house_system`).
5. **Given** une sortie de maisons **When** l'assignation planète->maison est appliquée dans la story 20.4 **Then** la convention `[start, end)` reste compatible avec le moteur existant.

## Technical Notes

- Introduire une interface `HousesProvider` (strategy) pour éviter un couplage direct à SwissEph.
- Centraliser mapping house-system (`placidus -> P`) dans un module dédié.
- Ajouter métrique de latence:
  - `swisseph_houses_calc_duration_ms`

## Tests

- Tests unitaires: validité structure cuspides/angles.
- Tests unitaires: défaut `placidus`.
- Test unitaire topocentrique altitude implicite `0`.
- Test erreur `422 unsupported_house_system`.

## Rollout/Feature flag

- Activé uniquement via engine SwissEph.
- Equal/Whole Sign restent cachés derrière un flag interne non exposé en public API.

---

## Tasks / Subtasks

- [x] Task 1: Créer `app/domain/astrology/houses_provider.py`
  - [x] 1.1 Constantes : `_HOUSE_SYSTEM_CODES` (placidus → b"P", equal → b"E", whole_sign → b"W") et `_SUPPORTED_HOUSE_SYSTEMS` frozenset (placidus uniquement)
  - [x] 1.2 `HouseData` (dataclass frozen) : `cusps` tuple 12 floats, `ascendant_longitude`, `mc_longitude`, `house_system`
  - [x] 1.3 `HousesCalcError` avec `code="houses_calc_failed"` et `UnsupportedHouseSystemError` avec `code="unsupported_house_system"`
  - [x] 1.4 `calculate_houses(jdut, lat, lon, *, house_system="placidus", frame="geocentric", altitude_m=None)` : validation house_system, lazy import swe, gestion topocentric via `swe.set_topo` (reset en finally), appel `swe.houses_ex`, normalisation cuspides + ASC/MC dans `[0, 360)`
  - [x] 1.5 Métrique `swisseph_houses_calc_duration_ms` (observe_duration) et log structuré sans PII

- [x] Task 2: Ajouter handlers d'exception dans `app/main.py`
  - [x] 2.1 Import `HousesCalcError` et `UnsupportedHouseSystemError` depuis `app.domain.astrology.houses_provider`
  - [x] 2.2 Handler 503 pour `HousesCalcError`
  - [x] 2.3 Handler 422 pour `UnsupportedHouseSystemError`

- [x] Task 3: Tests unitaires `backend/app/tests/unit/test_houses_provider.py`
  - [x] 3.1 Tests structure HouseData : 12 cuspides, ASC/MC normalisés `[0, 360)`, champ `house_system` présent
  - [x] 3.2 Test Placidus par défaut — `houses_ex` appelé avec `b"P"`, pas de paramètre explicite requis
  - [x] 3.3 Test topocentrique : `set_topo(lon, lat, 0)` quand `altitude_m=None`, reset `set_topo(0,0,0)` en sortie
  - [x] 3.4 Test géocentrique : `set_topo` non appelé
  - [x] 3.5 Test erreur `422 unsupported_house_system` pour système inconnu et pour "equal"/"whole_sign" (réservés)
  - [x] 3.6 Test `HousesCalcError` quand `houses_ex` lève une exception
  - [x] 3.7 Test métrique `swisseph_houses_calc_duration_ms` enregistrée après calcul

## Dev Notes

### Architecture
- `app/domain/astrology/houses_provider.py` : module pur domaine, sans état global mutable par requête.
- Pattern strategy : `_HOUSE_SYSTEM_CODES` centralise le mapping public→code SwissEph. `_SUPPORTED_HOUSE_SYSTEMS` contrôle l'exposition publique (seul `"placidus"` en v1).
- `UnsupportedHouseSystemError` → 422 (erreur fonctionnelle). `HousesCalcError` → 503 (erreur technique).
- `swe.set_topo` encapsulé per-call avec reset `finally` pour éviter side-effects permanents (même approche que `set_sid_mode` dans story 20.2).
- Import `swisseph` en lazy (inside function) → compatible avec `patch.dict("sys.modules", ...)` dans les tests.

### Patterns utilisés
- Même approche que `ephemeris_provider.py` : constantes stables, lazy import, mock-friendly.
- `observe_duration("swisseph_houses_calc_duration_ms", elapsed_ms)` depuis `app.infra.observability.metrics`.
- `dataclass(frozen=True)` pour l'immutabilité de `HouseData`.
- Convention `[0, 360)` : normalisation via `lon % 360.0` sur chaque cuspide et angle.

### Signature `swe.houses_ex`
```
cusps_raw, ascmc_raw = swe.houses_ex(jdut, lat, lon, hsys_code)
# cusps_raw : 13 éléments — index 0 non utilisé, index 1..12 = maisons 1..12
# ascmc_raw : 10 éléments — index 0 = ASC, index 1 = MC
```

## Dev Agent Record

### Implementation Plan

1. Créer `app/domain/astrology/houses_provider.py` (constantes + HouseData + erreurs + calculate_houses)
2. Ajouter handlers `HousesCalcError` (503) et `UnsupportedHouseSystemError` (422) dans `app/main.py`
3. Tests unitaires `backend/app/tests/unit/test_houses_provider.py`

### Completion Notes

Implémentation complète le 2026-02-26 :

- **`app/domain/astrology/houses_provider.py`** (nouveau) : module pur domaine.
  - `_HOUSE_SYSTEM_CODES` : mapping stable `placidus→b"P"`, `equal→b"E"`, `whole_sign→b"W"`.
  - `_SUPPORTED_HOUSE_SYSTEMS` : frozenset `{"placidus"}` — contrôle exposition publique en v1.
  - `HouseData` (dataclass frozen) : `cusps` tuple 12 floats normalisés `[0, 360)`, `ascendant_longitude`, `mc_longitude`, `house_system`.
  - `HousesCalcError` (`code="houses_calc_failed"`) et `UnsupportedHouseSystemError` (`code="unsupported_house_system"`).
  - `calculate_houses(jdut, lat, lon, *, house_system, frame, altitude_m)` : validation pré-calcul, lazy import swe, gestion `set_topo` per-call + reset `finally` pour topocentric, appel `swe.houses_ex`, normalisation `lon % 360.0`, métrique `swisseph_houses_calc_duration_ms`, log structuré sans PII.
- **`app/main.py`** (modifié) : import + handlers `HousesCalcError → 503` et `UnsupportedHouseSystemError → 422`.
- **`test_houses_provider.py`** (nouveau) : 38 tests — structure HouseData, Placidus par défaut, topocentrique altitude implicite, reset set_topo, unsupported system 422, erreurs normalisées, métriques, compatibilité `[0, 360)`. Tous verts.

**Acceptance Criteria satisfaits :**
- AC1 ✅ : 12 cuspides + ASC/MC retournés, normalisés `[0, 360)`.
- AC2 ✅ : `house_system=placidus` par défaut — `houses_ex` appelé avec `b"P"`.
- AC3 ✅ : `frame=topocentric` sans altitude → `altitude_m=0` appliqué explicitement via `swe.set_topo`.
- AC4 ✅ : Système non supporté → `UnsupportedHouseSystemError` (code `unsupported_house_system`) → 422.
- AC5 ✅ : Convention `[0, 360)` compatible avec l'assignation planète→maison de la story 20.4.

## File List

- `backend/app/domain/astrology/houses_provider.py` (nouveau)
- `backend/app/main.py` (modifié)
- `backend/app/tests/unit/test_houses_provider.py` (nouveau)
- `_bmad-output/implementation-artifacts/20-3-houses-provider-swiss-placidus-extensible.md` (modifié)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié)

## Change Log

- 2026-02-26 : Story 20-3 implémentée — Provider maisons SwissEph (Placidus par défaut, extensible).
  - Nouveau module `app/domain/astrology/houses_provider.py` : calcul 12 cuspides + ASC/MC via `swe.houses_ex`, Placidus par défaut, architecture strategy extensible, support topocentrique.
  - Handlers d'exception `HousesCalcError → 503` et `UnsupportedHouseSystemError → 422` dans `app/main.py`.
  - 38 tests unitaires — 38 passés, zéro régression introduite (406 tests unitaires au total).
