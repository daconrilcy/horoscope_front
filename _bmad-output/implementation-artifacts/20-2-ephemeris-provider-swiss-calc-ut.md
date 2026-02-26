# Story 20.2: Provider `ephemeris_provider` SwissEph pour positions planétaires

Status: done

## Title

Implémenter un provider SwissEph pour calcul planétaire (`calc_ut`) avec speed, rétrograde et options zodiacales.

## Context

Le pipeline natal doit produire des longitudes réelles reproductibles pour Sun..Pluto, avec état rétrograde basé sur la vitesse.

## Scope

- Créer `ephemeris_provider` basé sur `swe.calc_ut`.
- Corps minimaux: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
- Retourner:
  - longitude écliptique `0 <= lon < 360`
  - latitude écliptique
  - vitesse longitudinale
  - booléen rétrograde (`speed_longitude < 0`)
- Support `zodiac=tropical` (défaut) et `zodiac=sidereal`.
- Si sidéral sans ayanamsa explicite: `ayanamsa=lahiri`.

## Out of scope

- Calcul des maisons.
- Mapping final API/UI.

## Acceptance Criteria

1. **Given** un `jdut` valide **When** le provider calcule Sun..Pluto **Then** chaque planète est retournée avec `longitude`, `latitude`, `speed_longitude`, `is_retrograde`.
2. **Given** `zodiac=tropical` **When** aucun paramètre zodiacal n'est passé **Then** le calcul est tropical par défaut.
3. **Given** `zodiac=sidereal` sans ayanamsa **When** le provider est appelé **Then** `ayanamsa=lahiri` est appliqué explicitement et présent en metadata interne.
4. **Given** une planète avec `speed_longitude < 0` **When** le résultat est construit **Then** `is_retrograde=true`.
5. **Given** une erreur SwissEph de calcul **When** le provider échoue **Then** l'erreur est traduite en erreur technique normalisée (5xx) sans stack brute côté client.

## Technical Notes

- Prévoir mapping stable des ids planète internes vers constantes SwissEph.
- Éviter les effets globaux permanents de `set_sid_mode`; encapsuler au niveau requête.
- Ajouter métrique de latence provider:
  - `swisseph_planet_calc_duration_ms`

## Tests

- Tests unitaires paramétrés par planète (10 corps).
- Tests unitaires tropical vs sidéral (Lahiri par défaut).
- Test unitaire rétrograde (`speed < 0`).
- Test de robustesse: erreur SwissEph convertie en erreur API normalisée.

## Rollout/Feature flag

- Exécuté derrière `natal_engine=swisseph` tant que 20.4 n'est pas active.
- Conserver provider simplified inchangé durant l'introduction.

---

## Tasks / Subtasks

- [x] Task 1: Créer `app/domain/astrology/ephemeris_provider.py`
  - [x] 1.1 Constantes: `_PLANET_IDS` (10 corps Sun..Pluto → swe integer ids) et `_AYANAMSA_IDS` (lahiri → 1)
  - [x] 1.2 `PlanetData` (dataclass frozen): `planet_id`, `longitude`, `latitude`, `speed_longitude`, `is_retrograde`
  - [x] 1.3 `EphemerisCalcError` avec `code="ephemeris_calc_failed"`
  - [x] 1.4 `calculate_planets(jdut, *, zodiac="tropical", ayanamsa=None)` : itère sur les 10 corps, encapsule `set_sid_mode` per-call, normalise longitude `[0, 360)`, déduit `is_retrograde`
  - [x] 1.5 Métrique `swisseph_planet_calc_duration_ms` (observe_duration) et log structuré sans PII

- [x] Task 2: Ajouter exception handler dans `app/main.py`
  - [x] 2.1 Importer `EphemerisCalcError` depuis `app.domain.astrology.ephemeris_provider`
  - [x] 2.2 Handler 503 pour `EphemerisCalcError`

- [x] Task 3: Tests unitaires `backend/app/tests/unit/test_ephemeris_provider.py`
  - [x] 3.1 Tests paramétrés: chaque planète (10 corps) retourne `planet_id`, `longitude ∈ [0, 360)`, `latitude`, `speed_longitude`, `is_retrograde`
  - [x] 3.2 Test tropical par défaut (sans `zodiac`, `set_sid_mode` NON appelé)
  - [x] 3.3 Test sidéral: `zodiac="sidereal"` → `set_sid_mode(1)` appelé (Lahiri par défaut), reset appelé en fin
  - [x] 3.4 Test rétrograde: speed < 0 → `is_retrograde=True`; speed ≥ 0 → `is_retrograde=False`
  - [x] 3.5 Test erreur `calc_ut` → `EphemerisCalcError`
  - [x] 3.6 Test métrique `swisseph_planet_calc_duration_ms` enregistrée après calcul

## Dev Notes

### Architecture
- `app/domain/astrology/ephemeris_provider.py` : module pur domaine, sans état global mutable par requête.
- `set_sid_mode` encapsulé au niveau requête (appelé avant iteration, reset après) pour éviter side-effects permanents.
- `EphemerisCalcError` propagée via exception handler dans `main.py` → 503 normalisé.
- Import de `swisseph` à l'intérieur de la fonction → compatible avec mock `patch.dict("sys.modules", ...)` dans les tests.

### Patterns utilisés
- Constantes entières pour les IDs SwissEph (pas de dépendance aux attributs `swe.SUN`, etc.) → stable même sans pyswisseph installé.
- `observe_duration("swisseph_planet_calc_duration_ms", duration_ms)` depuis `app.infra.observability.metrics`.
- `dataclass(frozen=True)` pour l'immutabilité des résultats.

### Note sur pyswisseph dans les tests
Même approche que 20-1 : `patch.dict("sys.modules", {"swisseph": mock_swe})` pour simuler le module sans installation réelle.

## Dev Agent Record

### Implementation Plan

1. Créer `app/domain/astrology/ephemeris_provider.py` (constantes + PlanetData + EphemerisCalcError + calculate_planets)
2. Ajouter exception handler `EphemerisCalcError` dans `app/main.py`
3. Tests unitaires `backend/app/tests/unit/test_ephemeris_provider.py`

### Completion Notes

Implémentation complète le 2026-02-26 :

- **`app/domain/astrology/ephemeris_provider.py`** (nouveau) : module pur domaine.
  - `_PLANET_IDS` : mapping stable 10 corps (Sun→0, Moon→1, … Pluto→9) vers entiers SwissEph.
  - `_AYANAMSA_IDS` : mapping ayanamsa → constante SIDM (lahiri=1, fagan_bradley=0).
  - `PlanetData` (dataclass frozen) : `planet_id`, `longitude` `[0, 360)`, `latitude`, `speed_longitude`, `is_retrograde`.
  - `EphemerisCalcError` avec `code="ephemeris_calc_failed"`.
  - `calculate_planets(jdut, *, zodiac, ayanamsa)` : import lazy `swisseph` (compatible mock), `set_sid_mode` encapsulé per-call + reset `finally`, itération 10 corps via `calc_ut`, normalisation longitude, métrique `swisseph_planet_calc_duration_ms`, log structuré sans PII.
- **`app/main.py`** (modifié) : import `EphemerisCalcError` + handler 503 normalisé.
- **`test_ephemeris_provider.py`** (nouveau) : 44 tests — paramétrés par planète, tropical/sidéral, rétrograde, gestion d'erreurs, métriques. Tous verts.

**Acceptance Criteria satisfaits :**
- AC1 ✅ : 10 corps retournés avec `longitude`, `latitude`, `speed_longitude`, `is_retrograde`.
- AC2 ✅ : `zodiac=tropical` par défaut — `set_sid_mode` non appelé.
- AC3 ✅ : `zodiac=sidereal` sans ayanamsa → Lahiri appliqué (`set_sid_mode(1)`) + reset final.
- AC4 ✅ : `speed_longitude < 0` → `is_retrograde=True`.
- AC5 ✅ : Erreurs SwissEph → `EphemerisCalcError` (503 via handler), stack brute non exposée.

## File List

- `backend/app/domain/astrology/ephemeris_provider.py` (nouveau)
- `backend/app/core/ephemeris.py` (nouveau, support bootstrap)
- `backend/app/api/v1/routers/ephemeris.py` (nouveau, endpoint status)
- `backend/app/main.py` (modifié)
- `backend/app/tests/unit/test_ephemeris_provider.py` (nouveau)
- `_bmad-output/implementation-artifacts/20-2-ephemeris-provider-swiss-calc-ut.md` (modifié)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié)

## Change Log

- 2026-02-26 : Story 20-2 implémentée — Provider ephemeris_provider SwissEph (calc_ut).
  - Nouveau module `app/domain/astrology/ephemeris_provider.py` : calcul Sun..Pluto via swe.calc_ut, tropical/sidéral Lahiri, rétrograde.
  - Refactoring : metrics déplacées hors du domaine vers la couche service (Story 20.4), normalisation longitude simplifiée, constantes résolues dynamiquement.
  - Exception handler `EphemerisCalcError` → 503 dans `app/main.py`.
  - 45 tests unitaires (dont 1 smoke test) — 45 passés, zéro régression introduite.
