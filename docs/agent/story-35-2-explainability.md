# Story 35-2 — Explicabilité : top contributeurs et mode debug

## Contexte & Périmètre

**Epic 35 / Story 35-2**
**Chapitre 35** — Persistance, explicabilité et audit

Chaque note 1–20 doit être auditable : on doit pouvoir remonter aux principaux événements qui l'ont produite. Cette story ajoute au moteur la capacité de conserver les top contributeurs par catégorie et les drivers de pivots, ainsi qu'un mode debug structuré qui peut être activé sans changer les scores.

---

## Hypothèses & Dépendances

- **Dépend de 35-1** : run persisté disponible, `DailyPredictionCategoryScoreModel` et `DailyPredictionTurningPointModel` accessibles en DB
- Les contributions par (événement, catégorie) sont disponibles en mémoire pendant le run (depuis 34-2)
- Le mode debug est activé via `EngineInput.debug_mode`
- Les top contributeurs ne nécessitent pas de colonne DB supplémentaire : ils sont sérialisés en JSON dans un champ `contributors_json` à ajouter sur `DailyPredictionCategoryScoreModel`

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Construire un `ExplainabilityReport` par run contenant top 3 contributeurs par catégorie
- Stocker les contributeurs dans la DB (champ JSON) ou dans un objet séparé selon la politique
- Implémenter le mode debug structuré (données supplémentaires sans impact sur les scores)
- Conserver les drivers de pivots (déjà partiellement fait en 35-1 via `driver_json`)

**Non-Objectifs :**
- Pas de génération de texte explicatif (texte libre LLM)
- Pas d'interface utilisateur
- Le mode debug n'est pas requis pour le rendu public

---

## Acceptance Criteria

### AC1 — Top 3 contributeurs par catégorie
`ExplainabilityBuilder.build_category_contributors(contributions_log, category_code)` retourne une liste de au maximum 3 `ContributorEntry` triés par `abs(contribution)` décroissant :

```python
@dataclass
class ContributorEntry:
    event_type: str
    body: str | None
    target: str | None
    aspect: str | None
    contribution: float        # valeur signée
    local_time: datetime
    orb_deg: float | None
    phase: str | None          # "applying" | "exact" | "separating"
```

### AC2 — Ordre décroissant cohérent
Les contributeurs sont triés par `abs(contribution)` décroissant. Le premier est toujours le plus impactant.

### AC3 — Drivers de pivots disponibles
Pour chaque `TurningPoint`, les drivers principaux sont accessibles via `TurningPoint.driver_events` (déjà défini en 34-5). Cette story vérifie que ces drivers sont correctement sérialisés dans `driver_json` de `DailyPredictionTurningPointModel`.

Format attendu de `driver_json` :
```json
[
  {"event_type": "exact", "body": "Mars", "target": "MC", "aspect": "square",
   "contribution": -0.72, "local_time": "2026-03-07T14:15:00+01:00"},
  ...
]
```

### AC4 — Mode debug on/off sans divergence de scores
Quand `debug_mode=True` :
- L'`EngineOutput` contient un champ `debug_data` (dict) avec les contributions brutes par pas et par événement
- Les scores, notes, pivots et blocs sont **strictement identiques** au mode non-debug

Quand `debug_mode=False` :
- `debug_data` est absent ou vide
- Aucun overhead de calcul pour les données debug

### AC5 — Stockage des contributeurs
Les top 3 contributeurs sont stockés dans `DailyPredictionCategoryScoreModel` via un champ `contributors_json` (Text, nullable).
Ce champ nécessite une migration Alembic si absent du modèle actuel.

### AC6 — Cohérence des données
Les contributeurs renvoyés correspondent aux événements réels du run. Aucun événement fictif ou interpolé.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── explainability.py    ← ExplainabilityBuilder, ContributorEntry, ExplainabilityReport
```

### Migration DB (si nécessaire)

Si `DailyPredictionCategoryScoreModel` n'a pas de champ `contributors_json` :
```
backend/migrations/versions/YYYYMMDD_0035_add_contributors_json_to_category_scores.py ← CRÉER
```

### `explainability.py` — extraits clés

```python
from dataclasses import dataclass, field
from datetime import datetime
from app.prediction.schemas import AstroEvent

@dataclass
class ContributorEntry:
    event_type: str
    body: str | None
    target: str | None
    aspect: str | None
    contribution: float
    local_time: datetime
    orb_deg: float | None
    phase: str | None

@dataclass
class CategoryExplainability:
    category_code: str
    top_contributors: list[ContributorEntry]  # max 3, triés par abs(contribution) desc

@dataclass
class ExplainabilityReport:
    run_input_hash: str
    categories: dict[str, CategoryExplainability]
    debug_data: dict | None  # None si debug_mode=False

class ExplainabilityBuilder:
    MAX_CONTRIBUTORS = 3

    def build(
        self,
        contributions_log: list[tuple[AstroEvent, str, float]],  # (event, cat_code, contribution)
        run_input_hash: str,
        debug_mode: bool,
        raw_contributions_by_step: list | None = None,
    ) -> ExplainabilityReport:
        by_category: dict[str, list] = {}
        for event, cat_code, contribution in contributions_log:
            by_category.setdefault(cat_code, []).append((abs(contribution), event, contribution))

        categories = {}
        for cat_code, items in by_category.items():
            items.sort(reverse=True)
            top = items[:self.MAX_CONTRIBUTORS]
            categories[cat_code] = CategoryExplainability(
                category_code=cat_code,
                top_contributors=[
                    ContributorEntry(
                        event_type=ev.event_type, body=ev.body, target=ev.target,
                        aspect=ev.aspect, contribution=contrib,
                        local_time=ev.local_time, orb_deg=ev.orb_deg,
                        phase=(ev.metadata or {}).get("phase"),
                    )
                    for _, ev, contrib in top
                ],
            )

        return ExplainabilityReport(
            run_input_hash=run_input_hash,
            categories=categories,
            debug_data=raw_contributions_by_step if debug_mode else None,
        )
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_explainability.py`

| Test | Description |
|------|-------------|
| `test_top3_contributors_present` | 5 événements pour une catégorie → 3 conservés |
| `test_contributors_sorted_desc` | Ordre décroissant par `abs(contribution)` vérifié |
| `test_max_3_per_category` | Jamais plus de 3 contributeurs par catégorie |
| `test_debug_mode_on_has_debug_data` | `debug_mode=True` → `debug_data` présent et non vide |
| `test_debug_mode_off_no_debug_data` | `debug_mode=False` → `debug_data` absent (None) |
| `test_debug_no_score_change` | Mêmes scores avec debug=True et debug=False |
| `test_driver_json_format` | `driver_json` sérialisable en JSON valide |
| `test_contributor_fields_complete` | Chaque `ContributorEntry` a tous les champs requis |

---

## Nouveaux fichiers

- `backend/app/prediction/explainability.py` ← CRÉER
- `backend/app/tests/unit/test_explainability.py` ← CRÉER
- `backend/migrations/versions/YYYYMMDD_0035_add_contributors_json.py` ← CRÉER si nécessaire

## Fichiers existants à modifier (si migration nécessaire)

- `backend/app/infra/db/models/daily_prediction.py` ← MODIFIER : ajouter `contributors_json: Mapped[str | None]` sur `DailyPredictionCategoryScoreModel`

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/contribution_calculator.py` — contributions par (événement, catégorie) (34-2)
- `backend/app/prediction/turning_point_detector.py` — `TurningPoint.driver_events` (34-5)
- `backend/app/infra/db/models/daily_prediction.py` — modèles DB existants

---

## Checklist de validation

- [ ] Top 3 contributeurs par catégorie, triés par `abs(contribution)` décroissant
- [ ] Jamais plus de 3 contributeurs par catégorie
- [ ] Drivers de pivots sérialisés en JSON valide dans `driver_json`
- [ ] `debug_mode=True` → `debug_data` présent, scores identiques
- [ ] `debug_mode=False` → `debug_data` absent, aucun overhead
- [ ] `contributors_json` persisté sur `DailyPredictionCategoryScoreModel`
- [ ] Tous les tests unitaires passent
