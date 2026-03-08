# Story 37.4 : Validation métier des notes

Status: ready-for-dev

## Story

As a développeur du moteur de prédiction,
I want un script de génération de grille de revue et un processus de validation métier documenté sur un échantillon de jours réels,
so that les notes 1-20 produites par la calibration sont validées en usage réel et qu'une décision explicite de go/no-go de la calibration est tracée.

## Acceptance Criteria

### AC1 — Script de génération de la grille de revue

Un script `backend/app/jobs/calibration/generate_review_grid.py` charge les runs depuis `DailyPredictionRunModel` + `DailyPredictionCategoryScoreModel` (source principale avec `raw_score`, `note_20`, `contributors_json`) et génère une grille de revue au format CSV ou Markdown. `CalibrationRawDayModel` est utilisé en source secondaire uniquement pour enrichir avec `power` et `volatility`.

### AC2 — Colonnes requises dans la grille

La grille contient pour chaque ligne : jour, catégorie, raw_day, note (1-20), bande UX, top contributeurs (depuis `DailyPredictionCategoryScoreModel.contributors_json`), et un champ commentaire vide à remplir manuellement.

### AC3 — Écarts identifiés et documentés

Au moins 3 catégories sont reviewées et les écarts éventuels entre note calculée et perception métier sont documentés dans le rapport rempli `docs/calibration/review-grid-YYYY-MM-DD.md`.

### AC4 — Décision explicite documentée

Un fichier `docs/calibration/review-decision.md` contient une décision explicite : calibration validée OU recalibrage requis, avec justification et date de décision.

### AC5 — Rapport versionné dans `docs/calibration/`

Le rapport de revue rempli est versionné sous `docs/calibration/` avec la date dans le nom de fichier.

## Tasks / Subtasks

### T1 — Créer `backend/app/jobs/calibration/generate_review_grid.py`

**Source de données** : `CalibrationRawDayModel` (story 37-2) contient `raw_score`, `power`, `volatility` mais **pas** `note_20` ni `contributors_json`. Ces champs n'existent pas dans ce modèle. Il faut donc **joindre avec `DailyPredictionCategoryScoreModel`** pour des runs réels déjà persistés et calibrés, ou accepter que `note_20` soit calculé à la volée depuis le percentile au moment de la revue.

**Approche recommandée** : la grille de revue s'appuie sur des runs déjà calculés et persistés dans `DailyPredictionRunModel` + `DailyPredictionCategoryScoreModel` (qui ont `raw_score`, `note_20`, `contributors_json`), et fait un JOIN avec `CalibrationRawDayModel` sur `(local_date, category_code)` pour enrichir avec `power` et `volatility`. Le champ `local_date` est le nom correct (pas `day`).

- [ ] Importer `DailyPredictionCategoryScoreModel` et `DailyPredictionRunModel` (source principale)
- [ ] Importer `CalibrationRawDayModel` (source secondaire pour power/volatility si non disponible dans les scores)
- [ ] Charger les runs depuis `DailyPredictionRunModel` pour une plage de dates et un `user_id` (ou `profile_label`) configurable en argument CLI
- [ ] Pour chaque score : extraire `raw_score`, `note_20`, bande UX (via `note_to_band()`), top contributeurs depuis `contributors_json` (parsé JSON)
- [ ] Générer l'export en Markdown (tableau) ou CSV selon un flag `--format csv|md`
- [ ] Écrire le résultat dans un fichier horodaté sous `docs/calibration/`

### T2 — Créer `docs/calibration/review-grid-template.md`

- [ ] Créer le template Markdown avec les colonnes standard : `date`, `category`, `raw_day`, `note_20`, `band`, `top_contributors`, `commentaire`
- [ ] Ajouter une ligne d'exemple commentée
- [ ] Documenter les bandes UX dans l'en-tête du template

### T3 — Créer `docs/calibration/review-decision.md`

- [ ] Créer le fichier avec les sections : Date de décision, Reviewer, Résumé de la revue, Décision (validée / recalibrage), Justification, Prochaine échéance
- [ ] Le fichier est à remplir manuellement après exécution du script et revue métier

### T4 — Tests `backend/app/tests/unit/test_generate_review_grid.py`

- [ ] `test_grid_has_required_columns` — la grille générée contient toutes les colonnes requises (date, category, raw_day, note_20, band, top_contributors, commentaire)
- [ ] `test_band_mapping_correct` — vérifie que `note_to_band()` retourne la bonne bande pour chaque seuil (5, 9, 12, 16, 20)

## Dev Notes

### Fonction de mapping bande UX

```python
def note_to_band(note: int) -> str:
    if note <= 5:
        return "fragile"
    if note <= 9:
        return "tendu"
    if note <= 12:
        return "neutre"
    if note <= 16:
        return "porteur"
    return "très favorable"
```

### Squelette du script CLI

**Source principale** : `DailyPredictionCategoryScoreModel` (possède `raw_score`, `note_20`, `contributors_json`).
**Source secondaire** : `CalibrationRawDayModel` (pour `power` et `volatility` si nécessaire, via JOIN sur `local_date` + `category_code`).

```python
# backend/app/jobs/calibration/generate_review_grid.py
import argparse
import json
from datetime import date
from pathlib import Path

from sqlalchemy import select
from app.infra.db.session import get_session
from app.infra.db.models.daily_prediction import (
    DailyPredictionRunModel,
    DailyPredictionCategoryScoreModel,
)

DOCS_DIR = Path("docs/calibration")

def note_to_band(note: int) -> str:
    if note <= 5:
        return "fragile"
    if note <= 9:
        return "tendu"
    if note <= 12:
        return "neutre"
    if note <= 16:
        return "porteur"
    return "très favorable"

def generate_grid(start: date, end: date, fmt: str = "md") -> str:
    rows = []
    with get_session() as session:
        # Source principale : runs réels persistés + scores calibrés
        scores = session.scalars(
            select(DailyPredictionCategoryScoreModel)
            .join(DailyPredictionRunModel)
            .where(
                DailyPredictionRunModel.local_date >= start,
                DailyPredictionRunModel.local_date <= end,
            )
            .order_by(DailyPredictionRunModel.local_date, DailyPredictionCategoryScoreModel.category_code)
        ).all()
    for s in scores:
        contributors = json.loads(s.contributors_json or "[]")
        top = ", ".join(c.get("rule_id", str(c)) for c in contributors[:3])
        rows.append({
            "date": str(s.run.local_date),
            "category": s.category_code,
            "raw_day": round(s.raw_score, 3),
            "note_20": s.note_20,
            "band": note_to_band(s.note_20),
            "top_contributors": top,
            "commentaire": "",
        })
    if fmt == "csv":
        return _to_csv(rows)
    return _to_markdown(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--format", default="md", choices=["md", "csv"])
    args = parser.parse_args()
    content = generate_grid(date.fromisoformat(args.start), date.fromisoformat(args.end), args.format)
    out = DOCS_DIR / f"review-grid-{args.end}.{'md' if args.format == 'md' else 'csv'}"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"Grille générée : {out}")
```

### Nature semi-manuelle de la revue

La revue est un artefact semi-manuel : le script génère la grille avec les données calculées, et le métier remplit la colonne `commentaire` manuellement avant de documenter la décision dans `review-decision.md`. Ne pas tenter d'automatiser la décision métier elle-même.

### Structure des fichiers à créer

```
docs/calibration/
  review-grid-template.md
  review-grid-YYYY-MM-DD.md  ← généré par le script, rempli manuellement
  review-decision.md
backend/app/jobs/calibration/
  generate_review_grid.py
backend/app/tests/unit/
  test_generate_review_grid.py
```

## References

- [Source: _bmad-output/implementation-artifacts/37-1-specification-dataset-calibration.md — CalibrationRawDayModel, dataset de calibration]
- [Source: backend/app/prediction/editorial_builder.py — EditorialOutput, top3_contributors_per_category]
- [Source: backend/app/prediction/calibrator.py — PercentileCalibrator, note_20]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

- `backend/app/jobs/calibration/generate_review_grid.py`
- `backend/app/tests/unit/test_generate_review_grid.py`
- `docs/calibration/review-grid-template.md`
- `docs/calibration/review-decision.md`

## Change Log

- 2026-03-08: Story créée pour Epic 37.
