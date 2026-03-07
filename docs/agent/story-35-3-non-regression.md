# Story 35-3 — Non-régression et déterminisme moteur

## Contexte & Périmètre

**Epic 35 / Story 35-3**
**Chapitre 35** — Persistance, explicabilité et audit

Le moteur de calcul doit être strictement déterministe et reproductible. Cette story verrouille ce déterminisme via un pack de fixtures, des snapshots de sortie, et des tests de non-régression couvrant les cas types du modèle. Tout changement de référentiel ou ruleset doit modifier explicitement le hash et la sortie.

---

## Hypothèses & Dépendances

- **Dépend de 35-2** : moteur complet (épics 33, 34, 35-1, 35-2) opérationnel
- Les fixtures sont des `EngineInput` synthétiques couvrant des cas astrologiques représentatifs
- Les snapshots sont des `EngineOutput` sérialisés (JSON) produits lors d'une première exécution de référence
- Les tests de non-régression comparent la sortie actuelle au snapshot de référence

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Créer un dossier `backend/app/tests/regression/` avec fixtures et snapshots
- Implémenter les tests de non-régression sur ≥ 12 cas types + 2 snapshots complets
- Valider les bornes/clamps dans tous les cas
- Valider la stabilité des notes et des pivots à version figée

**Non-Objectifs :**
- Pas de nouvelle fonctionnalité moteur
- Pas de tests de performance (seulement de correction)

---

## Acceptance Criteria

### AC1 — Déterminisme strict
Pour chaque fixture, appeler le moteur deux fois avec le même `EngineInput` produit exactement le même `EngineOutput` :
- Mêmes `input_hash`
- Mêmes notes 1–20 par catégorie
- Mêmes pivots (heure, raison, catégories impactées)
- Mêmes `raw_day` et `power`/`volatility`

### AC2 — Clamps toujours respectés
Pour tous les cas fixtures :
- `NS(c) ∈ [0.75, 1.25]`
- `Contribution(e,c,t) ∈ [-1, +1]`
- `RawStep(c,t) ∈ [-3, +3]`
- `RawDay(c) ∈ [-2, +2]`
- `note_20 ∈ [1, 20]`

### AC3 — Pivots stables à version donnée
Pour une fixture avec version de référence `V1`, les pivots sont identiques à chaque run tant que la version ne change pas.

### AC4 — Changement de référentiel → hash et sortie changent
Si `reference_version` ou `ruleset_version` dans l'`EngineInput` change, le `input_hash` change et la sortie peut différer (aucun test d'identité dans ce cas).

### AC5 — Couverture minimum : 12 cas types

| # | Fixture | Particularité |
|---|---------|---------------|
| F01 | Journée calme | Aucun aspect exact, peu d'événements |
| F02 | Lune en maison 7 | Forte occupation amoureuse |
| F03 | Mars carré MC natal | Pivot professionnel négatif |
| F04 | Jupiter trigone Soleil natal | Signal positif multi-catégorie |
| F05 | Saturne conjonction Asc natal | Contrainte, signal santé |
| F06 | Lune change de signe en milieu de journée | Ingress lunaire → pivot détecté |
| F07 | Mercure rétrograde (orbe entrant) | enter_orb communication |
| F08 | Latitude extrême (60°N) | Repli Porphyre tracé |
| F09 | Timezone UTC-8 (Pacific) | Décalage UT important |
| F10 | Jour DST printemps | 100 pas, changement d'heure |
| F11 | Jour DST automne | 92 pas |
| F12 | Calibration provisoire | `is_provisional_calibration=True` |

### AC6 — 2 snapshots complets de journée
En plus des 12 cas types, 2 snapshots JSON complets d'une journée entière sont stockés et utilisés comme référence de régression. Ces snapshots incluent tous les champs de `EngineOutput`.

### AC7 — Test de snapshot : aucune régression
La sortie actuelle du moteur doit correspondre au snapshot de référence champ par champ (notes, pivots, blocs, hash, power, volatility). Toute divergence est un échec de test.

---

## Spécification technique

### Structure des fichiers

```
backend/app/tests/regression/
├── __init__.py
├── fixtures/
│   ├── F01_calm_day.json
│   ├── F02_moon_house7.json
│   ├── ...
│   ├── F12_provisional_calibration.json
│   ├── snapshot_full_day_A.json
│   └── snapshot_full_day_B.json
└── test_engine_non_regression.py
```

### Format d'une fixture

```json
{
  "input": {
    "natal_chart": { ... },
    "local_date": "2026-03-07",
    "timezone": "Europe/Paris",
    "latitude": 48.85,
    "longitude": 2.35,
    "reference_version": "V1",
    "ruleset_version": "V1",
    "debug_mode": false
  },
  "expected": {
    "input_hash": "abc123...",
    "category_notes": {
      "amour": 12,
      "travail": 8,
      "sante": 15,
      ...
    },
    "pivot_count": 2,
    "ns_bounds_ok": true,
    "clamps_ok": true
  }
}
```

### `test_engine_non_regression.py` — structure

```python
import json
import pytest
from pathlib import Path
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.schemas import EngineInput

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.mark.parametrize("fixture_file", sorted(FIXTURES_DIR.glob("F*.json")))
def test_case_type(fixture_file, db_session, loaded_ctx):
    data = json.loads(fixture_file.read_text())
    engine_input = EngineInput(**data["input"])
    result1 = EngineOrchestrator().run(engine_input, ...)
    result2 = EngineOrchestrator().run(engine_input, ...)

    # Déterminisme
    assert result1.effective_context.input_hash == result2.effective_context.input_hash
    assert _extract_notes(result1) == _extract_notes(result2)

    # Clamps
    assert _all_clamps_respected(result1)

    # Notes attendues (si présentes dans expected)
    if "category_notes" in data.get("expected", {}):
        assert _extract_notes(result1) == data["expected"]["category_notes"]


@pytest.mark.parametrize("snapshot_file", sorted(FIXTURES_DIR.glob("snapshot_*.json")))
def test_full_snapshot(snapshot_file, db_session, loaded_ctx):
    data = json.loads(snapshot_file.read_text())
    engine_input = EngineInput(**data["input"])
    result = EngineOrchestrator().run(engine_input, ...)
    assert _serialize_output(result) == data["expected_output"]
```

---

## Tests (les tests SONT les livrables de cette story)

| Test | Description |
|------|-------------|
| `test_case_type[F01]` à `test_case_type[F12]` | 12 cas types : déterminisme + clamps |
| `test_full_snapshot[A]` | Snapshot complet journée A (champ par champ) |
| `test_full_snapshot[B]` | Snapshot complet journée B (champ par champ) |
| `test_hash_changes_on_version_change` | Changer `ruleset_version` → hash différent |
| `test_ns_bounds_in_all_fixtures` | `NS(c) ∈ [0.75, 1.25]` sur tous les 12 fixtures |
| `test_pivots_stable_same_version` | Pivots identiques sur double run (même version) |

---

## Nouveaux fichiers

- `backend/app/tests/regression/__init__.py` ← CRÉER
- `backend/app/tests/regression/fixtures/` ← CRÉER (12 fixtures + 2 snapshots JSON)
- `backend/app/tests/regression/test_engine_non_regression.py` ← CRÉER

---

## Checklist de validation

- [ ] 12 fichiers fixtures JSON créés et valides
- [ ] 2 snapshots complets créés
- [ ] Double run → sortie identique (déterminisme)
- [ ] Tous les clamps respectés sur les 12 fixtures
- [ ] NS(c) borné dans tous les cas
- [ ] Pivots stables à version figée
- [ ] Changement de version → hash différent
- [ ] Tous les tests de non-régression passent
