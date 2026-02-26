# Story 20.1: Installation & configuration Swiss Ephemeris

Status: done

## Title

Installation et bootstrap Swiss Ephemeris (`pyswisseph`) avec configuration d'environnement contrôlée.

## Context

Le moteur accurate devient la base du calcul natal. Le runtime doit charger les données Swiss Ephemeris de manière déterministe et observable.

## Scope

- Ajouter `pyswisseph` au backend Python.
- Ajouter settings/env pour:
  - `SWISSEPH_ENABLED`
  - `SWISSEPH_DATA_PATH`
  - `SWISSEPH_PATH_VERSION` (identifiant lisible de dataset)
- Implémenter une validation de bootstrap au démarrage du backend.
- Exposer une erreur normalisée si données SwissEph indisponibles.

## Out of scope

- Calcul des positions planétaires.
- Calcul des maisons.
- Intégration UI.

## Acceptance Criteria

1. **Given** un environnement backend avec `pyswisseph` installé **When** l'application démarre **Then** la configuration SwissEph est chargée sans fallback implicite.
2. **Given** `SWISSEPH_DATA_PATH` invalide ou vide **When** SwissEph est initialisé **Then** l'app renvoie une erreur structurée `code=ephemeris_data_missing` (5xx) avec log structuré sans PII.
3. **Given** un échec d'initialisation runtime SwissEph **When** le backend démarre ou traite une requête accurate **Then** l'erreur `code=swisseph_init_failed` est produite (5xx) et incrémente un compteur métrique dédié.
4. **Given** SwissEph activé **When** une requête accurate est exécutée **Then** `metadata.ephemeris_path_version` contient la version/empreinte du dataset configuré.

## Technical Notes

- Prévoir un module d'initialisation central (`app/core/ephemeris.py`) sans état global mutable par requête.
- Ne pas exposer le chemin filesystem brut si cela fuit une info sensible; publier plutôt un identifiant de version.
- Prévoir métriques:
  - `swisseph_init_errors_total`
  - `swisseph_data_missing_total`

## Tests

- Test unitaire settings: valeurs par défaut et validation.
- Test unitaire bootstrap: path valide vs invalide.
- Test d'intégration API: erreur 5xx normalisée quand path absent.
- Test observabilité: métrique erreur incrémentée et log structuré émis.

## Rollout/Feature flag

- Flag principal: `SWISSEPH_ENABLED=false` par défaut en dev tant que stories 20.2 à 20.6 non livrées.
- Activation progressive: env de test puis staging avant production.

---

## Tasks / Subtasks

- [x] Task 1: Ajouter pyswisseph comme dépendance production
  - [x] 1.1 Ajouter `pyswisseph>=2.10.0` dans `[project].dependencies` du `backend/pyproject.toml`

- [x] Task 2: Ajouter les settings SwissEph dans `app/core/config.py`
  - [x] 2.1 `swisseph_enabled` (SWISSEPH_ENABLED, bool, défaut false)
  - [x] 2.2 `swisseph_data_path` (SWISSEPH_DATA_PATH, str, défaut "")
  - [x] 2.3 `swisseph_path_version` (SWISSEPH_PATH_VERSION, str, défaut "")

- [x] Task 3: Créer `app/core/ephemeris.py` — module de bootstrap central
  - [x] 3.1 `EphemerisDataMissingError` avec `code="ephemeris_data_missing"`
  - [x] 3.2 `SwissEphInitError` avec `code="swisseph_init_failed"`
  - [x] 3.3 `bootstrap_swisseph(data_path, path_version)` — valide le path + appelle `swe.set_ephe_path`
  - [x] 3.4 Métriques `swisseph_init_errors_total` et `swisseph_data_missing_total`
  - [x] 3.5 Logs structurés sans PII (ne pas logguer le path brut dans les messages d'erreur)
  - [x] 3.6 État de bootstrap accessible via `get_bootstrap_result()`

- [x] Task 4: Intégrer le bootstrap dans le lifespan `app/main.py`
  - [x] 4.1 Appel conditionnel de `bootstrap_swisseph` si `SWISSEPH_ENABLED=true`
  - [x] 4.2 Exception handlers HTTP pour `EphemerisDataMissingError` (503) et `SwissEphInitError` (503)

- [x] Task 5: Endpoint de statut `/v1/ephemeris/status`
  - [x] 5.1 Créer `app/api/v1/routers/ephemeris.py` avec `GET /v1/ephemeris/status`
  - [x] 5.2 Enregistrer le router dans `app/main.py`

- [x] Task 6: Tests unitaires et d'intégration
  - [x] 6.1 Tests settings: valeurs par défaut et overrides env
  - [x] 6.2 Tests bootstrap: path valide, path vide, path inexistant, swe init failure
  - [x] 6.3 Tests observabilité: métriques `swisseph_data_missing_total` et `swisseph_init_errors_total`
  - [x] 6.4 Tests intégration API: endpoint status (200 disabled, 200 ok, 503 data_missing, 503 init_failed)

## Dev Notes

### Architecture
- `app/core/ephemeris.py` : bootstrap central, état singleton (set once at startup), read-only par requête.
- Erreurs propagées via exception handlers dans `main.py` → réponses 5xx normalisées avec `code`.
- `app/api/v1/routers/ephemeris.py` : expose statut bootstrap pour diagnostic et tests d'intégration.
- `SWISSEPH_ENABLED=false` par défaut — aucun bootstrap tenté, endpoint retourne `{"status": "disabled"}`.

### Patterns utilisés
- Bootstrap pattern : `bootstrap_swisseph()` appelé dans lifespan FastAPI; échec stocké dans état module, app continue.
- Error handling : `EphemerisDataMissingError` et `SwissEphInitError` enregistrés comme exception handlers.
- Metrics : `increment_counter()` de `app/infra/observability/metrics`.
- Logs structurés : format `key=value`, paths filesystem jamais exposés dans les messages d'erreur.

### Note sur pyswisseph dans les tests
`pyswisseph` n'est pas installé dans l'environnement de test actuel. Les tests utilisent
`patch.dict("sys.modules", {"swisseph": mock})` pour simuler le module. Une fois `pyswisseph`
installé (`pip install -e ".[dev]"` avec la nouvelle dépendance), les tests continueront de
fonctionner grâce à cette approche de mock.

## Dev Agent Record

### Implementation Plan

1. Dépendance pyswisseph (`pyproject.toml`)
2. Settings (`app/core/config.py`)
3. Module bootstrap (`app/core/ephemeris.py`)
4. Lifespan + exception handlers (`app/main.py`)
5. Status endpoint (`app/api/v1/routers/ephemeris.py`)
6. Tests unitaires + intégration

### Completion Notes

Implémentation complète en 2026-02-26 :
- **pyproject.toml** : `pyswisseph>=2.10.0` ajouté aux dépendances production.
- **pyswisseph** : Installé dans l'environnement local pour validation réelle (plus seulement mock).
- **app/core/config.py** : 3 nouveaux settings (`swisseph_enabled`, `swisseph_data_path`, `swisseph_path_version`), tous strip-triés, `swisseph_enabled` défaut `false`.
- **app/core/ephemeris.py** : module bootstrap central. `bootstrap_swisseph()` valide `path_version` (empty → `SwissEphInitError`) et `data_path` (vide → `EphemerisDataMissingError`, inexistant → `EphemerisDataMissingError`, import failure → `SwissEphInitError`, set_ephe_path failure → `SwissEphInitError`). Métriques incrémentées, logs sans PII. État singleton accessible via `get_bootstrap_result()`.
- **app/main.py** : bootstrap conditionnel dans lifespan, exception handlers pour `EphemerisDataMissingError` (503) et `SwissEphInitError` (503).
- **app/api/v1/routers/ephemeris.py** : `GET /v1/ephemeris/status` — 200 disabled / 200 ok+path_version / 503 normalisé.
- **app/api/v1/routers/astrology_engine.py** : Inclusion de `metadata.ephemeris_path_version` dans les réponses `calculate` et `prepare`.
- **Tests** : 37 tests écrits et verts (25 unitaires + 12 intégration), couvrant les métriques et les métadonnées engine, zéro régression.

**Acceptance Criteria satisfaits :**
- AC1 ✅ : settings chargés sans fallback implicite (`SWISSEPH_ENABLED=false` par défaut).
- AC2 ✅ : `EphemerisDataMissingError` + 503 + log `reason=data_path_empty/not_found` sans PII + métrique `swisseph_data_missing_total`.
- AC3 ✅ : `SwissEphInitError` + 503 + métrique `swisseph_init_errors_total`.
- AC4 ✅ : `metadata.ephemeris_path_version` présent dans les réponses de l'engine accurate et dans l'endpoint status.

## File List

- `backend/pyproject.toml` (modifié)
- `backend/app/core/config.py` (modifié)
- `backend/app/core/ephemeris.py` (nouveau)
- `backend/app/api/v1/routers/ephemeris.py` (nouveau)
- `backend/app/api/v1/routers/astrology_engine.py` (modifié)
- `backend/app/main.py` (modifié)
- `backend/app/tests/unit/test_ephemeris_bootstrap.py` (nouveau)
- `backend/app/tests/integration/test_ephemeris_api.py` (nouveau)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié)

## Change Log

- 2026-02-26 : Story 20-1 implémentée — Installation & configuration Swiss Ephemeris.
  - Ajout de `pyswisseph>=2.10.0` aux dépendances production.
  - Nouveaux settings : `SWISSEPH_ENABLED`, `SWISSEPH_DATA_PATH`, `SWISSEPH_PATH_VERSION`.
  - Module bootstrap central `app/core/ephemeris.py` avec gestion d'erreurs normalisées, métriques et validation `path_version`.
  - Bootstrap conditionnel dans lifespan FastAPI + exception handlers 503.
  - Endpoint diagnostic `GET /v1/ephemeris/status`.
  - Mise à jour de `astrology_engine.py` pour AC4 (metadata).
  - 37 tests (unitaires + intégration), zéro régression.
