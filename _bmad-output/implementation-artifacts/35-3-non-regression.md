# Story 35.3 : Non-régression et déterminisme moteur

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un pack de fixtures, snapshots et tests de non-régression qui verrouillent le déterminisme et les clamps du moteur sur 12 cas types + 2 journées complètes,
so that tout changement de référentiel ou de logique est détecté immédiatement et la reproductibilité est garantie à chaque CI.

## Acceptance Criteria

### AC1 — Déterminisme strict

Pour chaque fixture : double run avec même `EngineInput` → `input_hash`, notes, pivots et `raw_day` identiques.

### AC2 — Clamps toujours respectés

Pour tous les cas : `NS(c) ∈ [0.75, 1.25]`, `Contribution ∈ [-1, +1]`, `RawStep ∈ [-3, +3]`, `RawDay ∈ [-2, +2]`, `note_20 ∈ [1, 20]`.

### AC3 — Pivots stables à version donnée

Mêmes pivots (heure, raison, catégories) sur double run avec même version de référentiel.

### AC4 — Changement de version → hash et sortie changent

Changer `ruleset_version` dans l'`EngineInput` → `input_hash` différent.

### AC5 — 12 cas types couverts

| # | Fixture | Particularité |
|---|---------|---------------|
| F01 | Journée calme | Aucun aspect exact |
| F02 | Lune maison 7 | Forte occupation amoureuse |
| F03 | Mars carré MC natal | Pivot professionnel négatif |
| F04 | Jupiter trigone Soleil natal | Signal positif multi-catégorie |
| F05 | Saturne conjonction Asc natal | Contrainte, signal santé |
| F06 | Lune change de signe à 14h | `moon_sign_ingress` → pivot |
| F07 | Signal Mercure | `enter_orb` / `exact` côté communication |
| F08 | Latitude 60°N | Latitude élevée couverte |
| F09 | Timezone UTC-8 | Décalage UT fort |
| F10 | DST printemps (92 pas) | 2026-03-29 Europe/Paris |
| F11 | DST automne (100 pas) | 2026-10-25 Europe/Paris |
| F12 | Calibration provisoire | `is_provisional_calibration=True` |

### AC6 — 2 snapshots complets

2 snapshots JSON d'une journée entière : tous les champs de `EngineOutput` comparés champ par champ.

## Tasks / Subtasks

### T1 — Créer l'infrastructure de tests de non-régression

- [x] Créer `backend/app/tests/regression/__init__.py`
- [x] Créer `backend/app/tests/regression/fixtures/` (dossier)
- [x] Créer les 12 fichiers `F01_calm_day.json` à `F12_provisional_calibration.json`
  - [x] Chaque fixture : `{"input": {...}, "expected": {"input_hash": "...", "category_notes": {...}, "pivot_count": N, "clamps_ok": true}}`
- [x] Créer `snapshot_full_day_A.json` et `snapshot_full_day_B.json`

### T2 — Tests de non-régression (AC1–AC6)

- [x] Créer `backend/app/tests/regression/test_engine_non_regression.py`
 - [x] `@pytest.mark.parametrize("fixture_file", F01..F12)` → `test_case_type(fixture_file)`
    - [x] Charger fixture, construire `EngineInput`
    - [x] Run × 2 → comparer hash, scores, pivots et blocs
    - [x] Vérifier les attentes spécifiques de fixture (`sample_count`, événements requis, calibration provisoire)
  - [x] `@pytest.mark.parametrize("snapshot_file", [A, B])` → `test_full_snapshot(snapshot_file)`
    - [x] Charger snapshot, run moteur, comparer `serialize_output(result) == expected_output`
  - [x] `test_hash_changes_on_version_change` — `ruleset_version` différent → hash différent
  - [x] `test_ns_bounds_all_fixtures` — `NS(c) ∈ [0.75, 1.25]` sur tous les F01–F12
  - [x] `test_pivots_stable` — double run → même liste de pivots

### T3 — Helper de sérialisation déterministe (AC6)

- [x] Créer `backend/app/tests/regression/helpers.py`
  - [x] `serialize_output(engine_output) -> dict` — sérialisation JSON-safe déterministe de l'output complet
  - [x] `assert_clamps(orchestrator, engine_input, engine_output)` — vérifie les clamps réels (`NS`, `Contribution`, `RawStep`, `RawDay`, `note_20`)
  - [x] `create_session()` — base SQLite temporaire autonome + seed V1/V2 pour éliminer la dépendance à une DB locale pré-remplie

## Dev Notes

### Format fichier fixture

```json
{
  "input": {
    "natal_chart": {
      "planets": {"Sun": 15.5, "Moon": 220.3, ...},
      "houses": {"1": 102.0, "2": 132.0, ...}
    },
    "local_date": "2026-03-07",
    "timezone": "Europe/Paris",
    "latitude": 48.85,
    "longitude": 2.35,
    "reference_version": "V1",
    "ruleset_version": "V1",
    "debug_mode": false
  },
  "expected": {
    "input_hash": "sha256_hex_string",
    "category_notes": {
      "amour": 12,
      "travail": 8
    },
    "pivot_count": 2,
    "clamps_ok": true
  }
}
```

### Génération des snapshots

Pour générer les snapshots de référence lors de la première exécution :
```python
import json
from pathlib import Path

def generate_snapshot(engine_output, output_path: Path):
    """Appeler UNE SEULE FOIS pour créer le snapshot de référence."""
    data = {
        "input": {...},
        "expected_output": serialize_output(engine_output)
    }
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
```

### DST — Fixtures F10 et F11

```python
# F10 : passage printemps
"local_date": "2026-03-29",  # 2h → 3h localement (23h, 92 pas)
"timezone": "Europe/Paris"

# F11 : passage automne
"local_date": "2026-10-25",  # 3h → 2h localement (25h, 100 pas)
"timezone": "Europe/Paris"
```

### CI integration

Ajouter dans `pytest.ini` ou `pyproject.toml` :
```toml
[tool.pytest.ini_options]
testpaths = ["backend/app/tests"]
markers = ["regression: regression tests (deselect with -m 'not regression')"]
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/tests/regression/__init__.py` | Créer |
| `backend/app/tests/regression/fixtures/F01_*.json` à `F12_*.json` | Créer (12 fixtures) |
| `backend/app/tests/regression/fixtures/snapshot_full_day_A.json` | Créer |
| `backend/app/tests/regression/fixtures/snapshot_full_day_B.json` | Créer |
| `backend/app/tests/regression/test_engine_non_regression.py` | Créer |
| `backend/app/tests/regression/helpers.py` | Créer |

### Fichiers à NE PAS toucher

- Tous les fichiers `backend/app/prediction/*.py`
- `backend/app/infra/db/`

### Références

- [Source: docs/model_de_calcul_journalier.md — Périmètre V1, décisions figées]
- [Source: _bmad-output/implementation-artifacts/33-1-engine-contract-orchestrateur.md — EngineInput, EngineOutput]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Mise en place de l'infrastructure de tests de non-régression dans `backend/app/tests/regression/`.
- Génération de 12 fixtures couvrant les cas types (DST, latitudes élevées, aspects, etc.).
- Création de 2 snapshots complets pour comparaison de la sérialisation complète de `EngineOutput`.
- Implémentation d'un helper de sérialisation déterministe et des helpers d'inspection du moteur.
- Validation du déterminisme strict, des pivots stables et des clamps réels.
- Intégration du marker `regression` dans `pyproject.toml` et `pytest.ini`.
- Correctif post-review: l'infrastructure de régression est maintenant hermétique, avec base temporaire et seed automatique `1.0.0` puis `2.0.0`.
- Correctif post-review: les snapshots complets A/B ont été régénérés pour inclure le champ `editorial` issu de 35.4.
- Validation finale exécutée dans le venv: chapitre 35 vert, puis suite backend complète verte.

### File List

- `backend/app/tests/regression/__init__.py`
- `backend/app/tests/regression/helpers.py`
- `backend/app/tests/regression/test_engine_non_regression.py`
- `backend/app/tests/regression/generate_fixtures.py`
- `backend/app/tests/regression/fixtures/F01_calm_day.json`
- `backend/app/tests/regression/fixtures/F02_moon_house_7.json`
- `backend/app/tests/regression/fixtures/F03_mars_square_mc.json`
- `backend/app/tests/regression/fixtures/F04_jupiter_trine_sun.json`
- `backend/app/tests/regression/fixtures/F05_saturn_conj_asc.json`
- `backend/app/tests/regression/fixtures/F06_moon_sign_ingress.json`
- `backend/app/tests/regression/fixtures/F07_mercury_retrograde.json`
- `backend/app/tests/regression/fixtures/F08_latitude_60n.json`
- `backend/app/tests/regression/fixtures/F09_timezone_utc_8.json`
- `backend/app/tests/regression/fixtures/F10_dst_spring.json`
- `backend/app/tests/regression/fixtures/F11_dst_autumn.json`
- `backend/app/tests/regression/fixtures/F12_provisional_calibration.json`
- `backend/app/tests/regression/fixtures/snapshot_full_day_A.json`
- `backend/app/tests/regression/fixtures/snapshot_full_day_B.json`
- `backend/pyproject.toml`
- `pytest.ini`
