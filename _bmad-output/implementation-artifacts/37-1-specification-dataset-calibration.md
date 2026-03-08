# Story 37.1 : Spécification du dataset de calibration

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want un dataset de calibration documenté, versionné et reproductible avec un panel de thèmes natals représentatifs,
so that toute campagne de calcul percentile s'appuie sur un corpus cohérent, traçable et validable par script.

## Acceptance Criteria

### AC1 — Dataset documenté et reproductible

Un fichier `docs/calibration/dataset-spec.md` décrit exhaustivement le dataset : panel de profils natals, plage temporelle, versions moteur fixées, catégories actives, politique des jours invalides.

### AC2 — Couverture temporelle ≥ 365 jours par profil

La spécification mentionne explicitement une plage d'au moins 365 jours consécutifs par profil (plage recommandée : 2024-01-01 → 2024-12-31).

### AC3 — Conventions moteur uniformes sur tout le corpus

La même combinaison `reference_version` + `ruleset_version` est fixée pour l'ensemble du dataset et documentée dans la spec.

### AC4 — Dataset versionné

La spec comporte un champ `dataset_version` (ex. `"1.0.0"`) incrémenté à chaque modification substantielle du panel ou de la plage.

### AC5 — Profils natals importables et validables par script

Le fichier `backend/app/jobs/calibration/natal_profiles.py` est importable en Python pur et un script `validate_dataset.py` vérifie la cohérence (nombre de profils ≥ 5, champs requis présents, diversité fuseau).

## Tasks / Subtasks

### T1 — Créer la documentation de spécification du dataset

- [ ] Créer le dossier `docs/calibration/`
- [ ] Créer `docs/calibration/dataset-spec.md` avec les sections :
  - En-tête : `dataset_version`, date de création, auteur
  - Panel de profils natals (≥ 5 lignes avec label, signe solaire, ascendant, timezone, lat/lon)
  - Plage temporelle (dates de début et fin, politique sur les jours invalides)
  - Versions moteur fixées (`reference_version`, `ruleset_version`)
  - Liste des catégories actives couvertes
  - Politique des jours invalides (éphémérides manquantes, interruption job)
  - Changelog du dataset

### T2 — Créer le package `backend/app/jobs/calibration/`

- [ ] Créer `backend/app/jobs/__init__.py` (si absent)
- [ ] Créer `backend/app/jobs/calibration/__init__.py`

### T3 — Créer le fichier de profils natals de calibration

- [ ] Créer `backend/app/jobs/calibration/natal_profiles.py`
  - [ ] Définir `CALIBRATION_PROFILES: list[dict]` avec ≥ 5 profils
  - [ ] Couvrir au minimum : 2 fuseaux européens, 1 fuseau américain, 1 fuseau asiatique, 1 latitude > 55°N
  - [ ] Chaque profil contient : `label`, `natal_chart`, `timezone`, `latitude`, `longitude`
  - [ ] Définir `CALIBRATION_DATE_RANGE = {"start": "2024-01-01", "end": "2024-12-31"}`
  - [ ] Définir `CALIBRATION_VERSIONS` en lisant **les versions actives réelles** via `settings` :
    ```python
    from app.core.config import settings
    # NE PAS coder "1.0.0" en dur — lire depuis la config active au moment du run
    CALIBRATION_VERSIONS = {
        "reference_version": settings.active_reference_version,
        "ruleset_version": settings.active_ruleset_version,  # à ajouter dans config si absent
    }
    ```
  - [ ] Documenter dans `dataset-spec.md` les versions **effectivement utilisées** lors de la campagne (à remplir après exécution, pas à coder en dur)

### T4 — Créer le script de validation du dataset

- [ ] Créer `backend/app/jobs/calibration/validate_dataset.py`
  - [ ] Vérifier `len(CALIBRATION_PROFILES) >= 5`
  - [ ] Vérifier que chaque profil possède les clés : `label`, `natal_chart`, `timezone`, `latitude`, `longitude`
  - [ ] Vérifier que les labels sont uniques
  - [ ] Vérifier la diversité des fuseaux (au moins 2 valeurs distinctes)
  - [ ] Vérifier la plage temporelle ≥ 365 jours
  - [ ] Afficher un rapport de validation en stdout
  - [ ] Retourner code de sortie 0 si OK, 1 si erreur

## Dev Notes

### Format d'un profil natal de calibration

```python
# backend/app/jobs/calibration/natal_profiles.py

CALIBRATION_PROFILES = [
    {
        "label": "profile_paris_aries",
        "natal_chart": {
            "planets": {"Sun": 15.5, "Moon": 220.3, "Mercury": 5.2, "Venus": 40.1,
                        "Mars": 280.0, "Jupiter": 100.0, "Saturn": 310.5,
                        "Uranus": 50.0, "Neptune": 350.0, "Pluto": 270.0},
            "houses": {"1": 102.0, "2": 132.0, "3": 162.0, "4": 192.0,
                       "5": 222.0, "6": 252.0, "7": 282.0, "8": 312.0,
                       "9": 342.0, "10": 12.0, "11": 42.0, "12": 72.0}
        },
        "timezone": "Europe/Paris",
        "latitude": 48.85,
        "longitude": 2.35,
    },
    {
        "label": "profile_london_scorpio",
        "natal_chart": {...},
        "timezone": "Europe/London",
        "latitude": 51.51,
        "longitude": -0.13,
    },
    {
        "label": "profile_new_york_cancer",
        "natal_chart": {...},
        "timezone": "America/New_York",
        "latitude": 40.71,
        "longitude": -74.01,
    },
    {
        "label": "profile_tokyo_capricorn",
        "natal_chart": {...},
        "timezone": "Asia/Tokyo",
        "latitude": 35.68,
        "longitude": 139.69,
    },
    {
        "label": "profile_stockholm_aquarius",
        "natal_chart": {...},
        "timezone": "Europe/Stockholm",
        "latitude": 59.33,   # latitude > 55°N
        "longitude": 18.07,
    },
]

CALIBRATION_DATE_RANGE = {"start": "2024-01-01", "end": "2024-12-31"}

# NE PAS coder les versions en dur — lire depuis la config active au moment du run
from app.core.config import settings
CALIBRATION_VERSIONS = {
    "reference_version": settings.active_reference_version,
    "ruleset_version": settings.active_ruleset_version,  # à ajouter dans config si absent
}
```

### Script de validation

```python
# backend/app/jobs/calibration/validate_dataset.py
import sys
from datetime import date
from app.jobs.calibration.natal_profiles import (
    CALIBRATION_PROFILES,
    CALIBRATION_DATE_RANGE,
    CALIBRATION_VERSIONS,
)

REQUIRED_KEYS = {"label", "natal_chart", "timezone", "latitude", "longitude"}

def validate() -> bool:
    errors = []

    if len(CALIBRATION_PROFILES) < 5:
        errors.append(f"Moins de 5 profils ({len(CALIBRATION_PROFILES)} trouvés)")

    labels = [p["label"] for p in CALIBRATION_PROFILES]
    if len(labels) != len(set(labels)):
        errors.append("Labels de profils non uniques")

    for p in CALIBRATION_PROFILES:
        missing = REQUIRED_KEYS - p.keys()
        if missing:
            errors.append(f"Profil {p.get('label','?')}: clés manquantes {missing}")

    timezones = {p["timezone"] for p in CALIBRATION_PROFILES}
    if len(timezones) < 2:
        errors.append("Diversité de fuseaux insuffisante (< 2 valeurs distinctes)")

    start = date.fromisoformat(CALIBRATION_DATE_RANGE["start"])
    end = date.fromisoformat(CALIBRATION_DATE_RANGE["end"])
    if (end - start).days < 365:
        errors.append("Plage temporelle < 365 jours")

    if errors:
        for e in errors:
            print(f"[ERREUR] {e}")
        return False

    print(f"[OK] Dataset valide — {len(CALIBRATION_PROFILES)} profils, "
          f"{(end - start).days + 1} jours, "
          f"versions {CALIBRATION_VERSIONS}")
    return True

if __name__ == "__main__":
    sys.exit(0 if validate() else 1)
```

### Structure des dossiers à créer

```
docs/
  calibration/
    dataset-spec.md
backend/app/jobs/
  __init__.py
  calibration/
    __init__.py
    natal_profiles.py
    validate_dataset.py
```

### Plage temporelle recommandée

- Début : `2024-01-01`
- Fin : `2024-12-31`
- Durée : 366 jours (2024 est bissextile)

### Versions actives à documenter dans la spec

Les versions ne sont **pas codées en dur** — elles sont lues depuis `settings.active_reference_version` et `settings.active_ruleset_version` au moment du run. La documentation `docs/calibration/dataset-spec.md` doit être complétée **après exécution** avec les valeurs effectives de la campagne (ex. : versions lues en prod lors du lancement du job).

## References

- [Source: backend/app/prediction/ — EngineOrchestrator, EngineInput, EngineOutput]
- [Source: backend/app/core/config.py — settings.active_reference_version]
- [Source: _bmad-output/implementation-artifacts/35-1-persistance-run.md — DailyPredictionRunModel, CategoryScoreModel]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

- `docs/calibration/dataset-spec.md`
- `backend/app/jobs/__init__.py`
- `backend/app/jobs/calibration/__init__.py`
- `backend/app/jobs/calibration/natal_profiles.py`
- `backend/app/jobs/calibration/validate_dataset.py`

## Change Log

- 2026-03-08: Story créée pour Epic 37.
