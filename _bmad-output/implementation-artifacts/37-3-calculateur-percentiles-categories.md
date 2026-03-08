# Story 37.3 : Calculateur de percentiles par catégorie

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want un service qui agrège le dataset `CalibrationRawDay` et calcule les percentiles P5/P25/P50/P75/P95 par catégorie, puis les injecte dans `CategoryCalibrationModel`,
so that le moteur bascule sur une calibration réelle sans aucun changement de code et que la calibration provisoire devient obsolète.

## Acceptance Criteria

### AC1 — Une calibration par catégorie active après le calcul

Après exécution du service, `CategoryCalibrationModel` contient exactement une entrée valide pour chaque catégorie active couverte par le dataset (même `ruleset_id`, même `(valid_from, valid_to)`).

### AC2 — `sample_size` renseigné

Chaque entrée injectée dans `CategoryCalibrationModel` comporte un `sample_size` égal au nombre de `raw_score` ayant servi au calcul (tous profils × toutes dates pour cette catégorie).

### AC3 — Monotonie des percentiles garantie

Pour chaque catégorie : `P5 ≤ P25 ≤ P50 ≤ P75 ≤ P95`. Le service rejette tout résultat qui violerait cette contrainte et le signale dans le rapport.

### AC4 — Basculement sans changement de code

La calibration provisoire est remplacée par la calibration réelle via l'injection dans `CategoryCalibrationModel`. Le moteur utilise la même API `PredictionRulesetRepository.get_calibrations()` — aucune modification du code moteur n'est nécessaire.

### AC5 — Rapport de contrôle produit

Le service génère un rapport JSON ou CSV par catégorie incluant : `sample_size`, `min`, `max`, `mean`, `P5`, `P25`, `P50`, `P75`, `P95`, liste des outliers (valeurs au-delà de 3 écarts-types).

## Tasks / Subtasks

### T1 — Créer le service `PercentileCalculatorService`

- [ ] Créer `backend/app/jobs/calibration/percentile_calculator.py`
  - [ ] Définir `PercentileResult` (dataclass ou TypedDict) : `category_code`, `p5`, `p25`, `p50`, `p75`, `p95`, `sample_size`, `mean`, `min`, `max`, `outliers: list[float]`
  - [ ] Implémenter `compute_percentile(data: list[float], p: float) -> float` (interpolation linéaire)
  - [ ] Implémenter `compute_percentiles(raw_scores: list[float]) -> PercentileResult`
    - [ ] Vérifier `len(raw_scores) >= 1`
    - [ ] Calculer P5, P25, P50, P75, P95
    - [ ] Vérifier la monotonie — lever `ValueError` si violée
    - [ ] Calculer `mean`, `min`, `max`
    - [ ] Identifier les outliers (|x - mean| > 3 × stddev)
  - [ ] Implémenter `class PercentileCalculatorService`
    - [ ] `__init__(self, db, calibration_repo: CalibrationRepository)`
    - [ ] `run(reference_version, ruleset_version, ruleset_id, valid_from, valid_to) -> list[PercentileResult]`
      - [ ] Charger tous les `raw_score` par catégorie depuis `CalibrationRawDayModel`
      - [ ] Appeler `compute_percentiles()` par catégorie
      - [ ] Upsert dans `CategoryCalibrationModel` (delete + insert par `(ruleset_id, category_id, valid_from)`)
      - [ ] Retourner la liste des `PercentileResult`
    - [ ] `generate_report(results: list[PercentileResult], output_path: Path) -> None` — écrit un fichier JSON

### T2 — Créer l'entrypoint CLI

- [ ] Créer `backend/app/jobs/compute_calibration_percentiles.py`
  - [ ] Bloc `if __name__ == "__main__":` invocable via `python -m app.jobs.compute_calibration_percentiles`
  - [ ] Charger `CALIBRATION_VERSIONS` depuis `natal_profiles.py`
  - [ ] Instancier `PercentileCalculatorService` avec la session DB
  - [ ] Appeler `service.run(...)` avec `valid_from="2024-01-01"`, `valid_to="2024-12-31"`
  - [ ] Appeler `service.generate_report(results, Path("docs/calibration/percentile_report.json"))`
  - [ ] Afficher un résumé en stdout (nb catégories traitées, sample_size moyen)

### T3 — Tests unitaires

- [ ] Créer `backend/app/tests/unit/test_percentile_calculator.py`
  - [ ] `test_percentiles_monotone` — vérifier que P5 ≤ P25 ≤ P50 ≤ P75 ≤ P95 sur un dataset synthétique de 1 000 valeurs aléatoires
  - [ ] `test_sample_size_correct` — `sample_size` correspond exactement au nombre de valeurs passées
  - [ ] `test_compute_percentile_known_values` — vérifier P50 = médiane sur un dataset de taille paire et impaire
  - [ ] `test_calibration_injected_in_db` — après `service.run()`, `CategoryCalibrationModel` contient les entrées attendues avec les bons champs
  - [ ] `test_motor_uses_real_calibration` — après injection, `PredictionRulesetRepository.get_calibrations()` retourne la calibration réelle (non provisoire)

## Dev Notes

### Calcul des percentiles (interpolation linéaire)

```python
def compute_percentile(data: list[float], p: float) -> float:
    """Calcule le p-ième percentile par interpolation linéaire (méthode type 7)."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 1:
        return sorted_data[0]
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])

def compute_percentiles(raw_scores: list[float]) -> PercentileResult:
    if not raw_scores:
        raise ValueError("Dataset vide — impossible de calculer les percentiles")
    p5  = compute_percentile(raw_scores, 5)
    p25 = compute_percentile(raw_scores, 25)
    p50 = compute_percentile(raw_scores, 50)
    p75 = compute_percentile(raw_scores, 75)
    p95 = compute_percentile(raw_scores, 95)
    # Vérification monotonie
    if not (p5 <= p25 <= p50 <= p75 <= p95):
        raise ValueError(f"Percentiles non monotones: {p5} {p25} {p50} {p75} {p95}")
    mean = sum(raw_scores) / len(raw_scores)
    variance = sum((x - mean) ** 2 for x in raw_scores) / len(raw_scores)
    stddev = variance ** 0.5
    outliers = [x for x in raw_scores if abs(x - mean) > 3 * stddev]
    return PercentileResult(
        p5=p5, p25=p25, p50=p50, p75=p75, p95=p95,
        sample_size=len(raw_scores),
        mean=mean, min=min(raw_scores), max=max(raw_scores),
        outliers=outliers,
    )
```

### Vérification du modèle `CategoryCalibrationModel` avant implémentation

Vérification faite sur le code actuel : `CategoryCalibrationModel` expose déjà `p05`, `p25`, `p50`, `p75`, `p95`, `sample_size`, `valid_from`, `valid_to`. Aucune migration supplémentaire n'est nécessaire pour `sample_size`.

### Pattern upsert dans `CategoryCalibrationModel`

```python
from app.infra.db.models.prediction_ruleset import CategoryCalibrationModel

def _upsert_calibration(
    db, ruleset_id: int, category_id: int,
    result: PercentileResult, valid_from: str, valid_to: str
) -> None:
    # Delete existant
    db.query(CategoryCalibrationModel).filter_by(
        ruleset_id=ruleset_id,
        category_id=category_id,
        valid_from=valid_from,
        valid_to=valid_to,
    ).delete()
    # Insert nouveau
    calibration = CategoryCalibrationModel(
        ruleset_id=ruleset_id,
        category_id=category_id,
        p05=result.p5,
        p25=result.p25,
        p50=result.p50,
        p75=result.p75,
        p95=result.p95,
        valid_from=valid_from,
        valid_to=valid_to,
        sample_size=result.sample_size,
    )
    db.add(calibration)
    db.commit()
```

### Dataset 37.2 validé et prêt à consommer

Validation locale réelle effectuée le `2026-03-08` sur SQLite locale :

- `reference_version=2.0.0`
- `ruleset_version=1.0.0`
- `5` profils
- `366` jours (`2024-01-01` → `2024-12-31`)
- `12` catégories actives :
  - `career`
  - `communication`
  - `energy`
  - `family_home`
  - `health`
  - `love`
  - `money`
  - `mood`
  - `pleasure_creativity`
  - `sex_intimacy`
  - `social_network`
  - `work`
- `1830` raw scores par catégorie
- `21960` lignes totales
- `0` doublon

Implications directes pour l'implémentation :

- le `ruleset_id` à résoudre pour la campagne locale validée est celui du ruleset `1.0.0`
- la story doit cibler les codes de catégories réellement présents en base, pas les anciens exemples `amour/travail/vitalité/finances`
- le rapport de contrôle peut s'appuyer sur un `sample_size` attendu de `1830` pour chaque catégorie tant que le dataset reste inchangé

### Format du rapport de contrôle

```json
{
  "generated_at": "2026-03-08T12:00:00Z",
  "reference_version": "2.0.0",
  "ruleset_version": "1.0.0",
  "valid_from": "2024-01-01",
  "valid_to": "2024-12-31",
  "categories": {
    "love": {
      "sample_size": 1830,
      "min": -0.01295,
      "max": 0.05327,
      "mean": 0.03,
      "p5": -0.01,
      "p25": -0.00,
      "p50": 0.00,
      "p75": 0.01,
      "p95": 0.03,
      "outlier_count": 0
    }
  }
}
```

### Fichiers à créer

| Fichier | Action |
|---------|--------|
| `backend/app/jobs/calibration/percentile_calculator.py` | Créer |
| `backend/app/jobs/compute_calibration_percentiles.py` | Créer |
| `backend/app/tests/unit/test_percentile_calculator.py` | Créer |
| `docs/calibration/percentile_report.json` | Généré à l'exécution (ne pas committer) |

### Fichiers à NE PAS toucher

- Tous les fichiers `backend/app/prediction/*.py`
- `backend/app/infra/db/repositories/prediction_ruleset_repository.py` (utiliser l'API existante)

### Dépendance sur story 37.2

Ce service lit la table `calibration_raw_days` produite par la story 37.2. Il faut que le job 37.2 ait été exécuté et ait produit des données avant de lancer ce service.

### Notes d'implémentation révisées après validation dataset

- Utiliser `reference_version=CALIBRATION_VERSIONS["reference_version"]` et `ruleset_version=CALIBRATION_VERSIONS["ruleset_version"]` lors du run, puis résoudre le `ruleset_id` via `PredictionRulesetRepository.get_ruleset()`.
- Les champs du modèle sont `p05/p25/p50/p75/p95` et non `p5/p25/p50/p75/p95`.
- La story peut rester sans modification moteur: `PredictionRulesetRepository.get_calibrations()` lit déjà `sample_size`.
- Générer le rapport dans `docs/calibration/percentile_report.json`, fichier non commité.

## References

- [Source: backend/app/infra/db/models/prediction_ruleset.py — CategoryCalibrationModel (champs P5…P95, valid_from, valid_to)]
- [Source: backend/app/infra/db/repositories/ — PredictionRulesetRepository.get_calibrations()]
- [Source: _bmad-output/implementation-artifacts/37-2-job-generation-rawday-calibration.md — CalibrationRawDayModel, CalibrationRepository]
- [Source: _bmad-output/implementation-artifacts/37-1-specification-dataset-calibration.md — CALIBRATION_VERSIONS, plage temporelle]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List
- Dataset 37.2 validé localement avant démarrage: `21960` raw days, `1830` scores par catégorie, `0` doublon.
- Contrat modèle confirmé: `CategoryCalibrationModel.sample_size` existe déjà et le champ percentile bas est `p05`.

### File List

- `backend/app/jobs/calibration/percentile_calculator.py`
- `backend/app/jobs/compute_calibration_percentiles.py`
- `backend/app/tests/unit/test_percentile_calculator.py`

## Change Log

- 2026-03-08: Story créée pour Epic 37.
