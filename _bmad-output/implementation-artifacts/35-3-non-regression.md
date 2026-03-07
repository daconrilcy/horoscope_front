# Story 35.3 : Non-régression et déterminisme moteur

Status: ready-for-dev

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
| F07 | Mercure rétrograde entrant | `enter_orb` communication |
| F08 | Latitude 60°N | Repli Porphyre tracé |
| F09 | Timezone UTC-8 | Décalage UT fort |
| F10 | DST printemps (100 pas) | 2026-03-29 Europe/Paris |
| F11 | DST automne (92 pas) | 2026-10-25 Europe/Paris |
| F12 | Calibration provisoire | `is_provisional_calibration=True` |

### AC6 — 2 snapshots complets

2 snapshots JSON d'une journée entière : tous les champs de `EngineOutput` comparés champ par champ.

## Tasks / Subtasks

### T1 — Créer l'infrastructure de tests de non-régression

- [ ] Créer `backend/app/tests/regression/__init__.py`
- [ ] Créer `backend/app/tests/regression/fixtures/` (dossier)
- [ ] Créer les 12 fichiers `F01_calm_day.json` à `F12_provisional_calibration.json`
  - [ ] Chaque fixture : `{"input": {...}, "expected": {"input_hash": "...", "category_notes": {...}, "pivot_count": N, "clamps_ok": true}}`
- [ ] Créer `snapshot_full_day_A.json` et `snapshot_full_day_B.json`

### T2 — Tests de non-régression (AC1–AC6)

- [ ] Créer `backend/app/tests/regression/test_engine_non_regression.py`
  - [ ] `@pytest.mark.parametrize("fixture_file", F01..F12)` → `test_case_type(fixture_file)`
    - [ ] Charger fixture, construire `EngineInput`
    - [ ] Run × 2 → comparer hashes, notes, clamps
    - [ ] Si `expected.category_notes` présent → vérifier les notes attendues
  - [ ] `@pytest.mark.parametrize("snapshot_file", [A, B])` → `test_full_snapshot(snapshot_file)`
    - [ ] Charger snapshot, run moteur, comparer `_serialize_output(result) == expected_output`
  - [ ] `test_hash_changes_on_version_change` — `ruleset_version` différent → hash différent
  - [ ] `test_ns_bounds_all_fixtures` — `NS(c) ∈ [0.75, 1.25]` sur tous les F01–F12
  - [ ] `test_pivots_stable` — double run → même liste de pivots

### T3 — Helper de sérialisation déterministe (AC6)

- [ ] Créer `backend/app/tests/regression/helpers.py`
  - [ ] `serialize_output(engine_output) -> dict` — sérialisation JSON-safe déterministe
  - [ ] `assert_clamps(engine_output)` — vérifie tous les clamps du rapport

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
"local_date": "2026-03-29",  # 2h → 3h localement (25h, 100 pas)
"timezone": "Europe/Paris"

# F11 : passage automne
"local_date": "2026-10-25",  # 3h → 2h localement (23h, 92 pas)
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

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
