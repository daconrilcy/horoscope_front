# Story 35-4 — Préparation de la couche éditoriale dérivée

## Contexte & Périmètre

**Epic 35 / Story 35-4**
**Chapitre 35** — Persistance, explicabilité et audit

Le moteur numérique ne rédige jamais de texte libre. Cette story produit un objet de sortie structuré, intégralement dérivé des scores et métriques du moteur, qui sera exploité par la future couche éditoriale (LLM) pour générer des textes d'horoscope. Elle prépare ainsi le contrat d'interface entre le moteur et la synthèse éditoriale sans les mélanger.

---

## Hypothèses & Dépendances

- **Dépend de 35-2** : `ExplainabilityReport` et scores complets disponibles
- L'objet éditorial est construit en mémoire après le run, avant ou après la persistance
- Aucun LLM n'est appelé dans cette story
- Les catégories santé et argent sont identifiées par leurs codes (ex. `"sante"`, `"argent"`) et flaguées pour rédaction prudente
- Le "meilleur bloc" est celui dont la note moyenne des catégories top 3 est la plus haute

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Créer `EditorialOutputBuilder.build(engine_output, explainability_report)` → `EditorialOutput`
- Calculer : top 3 catégories, bottom 2, pivot principal, meilleure fenêtre, flags prudence
- Dériver le ton global depuis les scores (pas de LLM)
- Préparer les champs nécessaires aux templates de rédaction

**Non-Objectifs :**
- Pas de génération de texte libre LLM dans cette story
- Pas de prompt, pas d'appel API
- Pas de frontend
- La couche éditoriale LLM (future) est hors périmètre

---

## Acceptance Criteria

### AC1 — Aucun texte libre LLM produit
`EditorialOutputBuilder` ne fait aucun appel à un LLM, ne génère aucun texte libre, et ne contient aucune chaîne de caractères rédigée en dur pour l'utilisateur final.

### AC2 — Top 3 catégories
`EditorialOutput.top3_categories` = liste des 3 catégories avec les meilleures notes, triées par note décroissante. En cas d'égalité, tri par `category.sort_order`.

### AC3 — Bottom 2 catégories
`EditorialOutput.bottom2_categories` = liste des 2 catégories avec les notes les plus basses.

### AC4 — Pivot principal
`EditorialOutput.main_pivot` = le `TurningPoint` avec la `severity` la plus haute sur la journée. Si aucun pivot, `main_pivot = None`.

### AC5 — Meilleure fenêtre (Peak90)
`EditorialOutput.best_window` = l'intervalle horaire correspondant à la fenêtre de 90 minutes avec le `peak90` le plus élevé sur les catégories top 3. Contient :
- `start_local` : `datetime`
- `end_local` : `datetime`
- `dominant_category` : code de la catégorie dominante dans cette fenêtre

### AC6 — Flags prudence santé / argent
`EditorialOutput.caution_flags` = dict `{category_code: bool}` indiquant les catégories qui nécessitent une rédaction prudente.
- `"sante"` est flagué si sa note ≤ 7 ou sa volatilité ≥ 1.5
- `"argent"` est flagué si sa note ≤ 7 ou sa volatilité ≥ 1.5
- Les codes de catégories "à risque" sont configurables via les paramètres du ruleset

### AC7 — Ton global dérivé
`EditorialOutput.overall_tone` est dérivé mécaniquement :
- `"positive"` si la moyenne des notes top 3 ≥ 13
- `"negative"` si la moyenne ≤ 7
- `"mixed"` si l'écart entre meilleure et pire note top 3 ≥ 5
- `"neutral"` sinon

### AC8 — Champs suffisants pour les templates
`EditorialOutput` contient tous les champs nécessaires pour qu'un template de rédaction (future couche LLM) puisse générer un texte sans accéder directement au moteur :
- `top3_categories` avec notes et `power`/`volatility`
- `bottom2_categories` avec notes
- `main_pivot` avec heure et raison
- `best_window` avec intervalle
- `caution_flags`
- `overall_tone`
- `top3_contributors_per_category` : `dict[str, list[ContributorEntry]]` (depuis explainability)

### AC9 — Cohérence top 3 / bottom 2
Les catégories dans `top3_categories` et `bottom2_categories` sont disjointes (pas de doublon).

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── editorial_builder.py    ← EditorialOutputBuilder, EditorialOutput, BestWindow
```

### `editorial_builder.py` — extraits clés

```python
from dataclasses import dataclass
from datetime import datetime
from app.prediction.schemas import EngineOutput
from app.prediction.explainability import ExplainabilityReport, ContributorEntry
from app.prediction.turning_point_detector import TurningPoint

CAUTION_CATEGORY_CODES = {"sante", "argent"}
CAUTION_NOTE_THRESHOLD = 7
CAUTION_VOL_THRESHOLD = 1.5

@dataclass
class BestWindow:
    start_local: datetime
    end_local: datetime
    dominant_category: str

@dataclass
class CategorySummary:
    code: str
    note_20: int
    power: float
    volatility: float

@dataclass
class EditorialOutput:
    top3_categories: list[CategorySummary]
    bottom2_categories: list[CategorySummary]
    main_pivot: TurningPoint | None
    best_window: BestWindow | None
    caution_flags: dict[str, bool]
    overall_tone: str
    top3_contributors_per_category: dict[str, list[ContributorEntry]]

class EditorialOutputBuilder:
    def build(
        self,
        engine_output: EngineOutput,
        explainability: ExplainabilityReport,
    ) -> EditorialOutput:
        scores = engine_output.category_scores  # dict[str, CategoryScore]
        sorted_by_note = sorted(
            scores.items(), key=lambda x: (-x[1].note_20, x[1].sort_order)
        )
        top3 = [CategorySummary(code=c, note_20=s.note_20, power=s.power, volatility=s.volatility)
                for c, s in sorted_by_note[:3]]
        bottom2 = [CategorySummary(code=c, note_20=s.note_20, power=s.power, volatility=s.volatility)
                   for c, s in sorted_by_note[-2:]]

        main_pivot = self._find_main_pivot(engine_output.turning_points)
        best_window = self._find_best_window(engine_output.time_blocks, top3)
        caution_flags = self._compute_caution_flags(scores)
        overall_tone = self._derive_tone(top3)

        return EditorialOutput(
            top3_categories=top3,
            bottom2_categories=bottom2,
            main_pivot=main_pivot,
            best_window=best_window,
            caution_flags=caution_flags,
            overall_tone=overall_tone,
            top3_contributors_per_category={
                cat_code: exp.top_contributors
                for cat_code, exp in explainability.categories.items()
            },
        )
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_editorial_builder.py`

| Test | Description |
|------|-------------|
| `test_top3_sorted_by_note_desc` | Top 3 triés par note décroissante |
| `test_bottom2_lowest_notes` | Bottom 2 = les deux notes les plus basses |
| `test_top3_bottom2_disjoint` | Pas de code commun entre top3 et bottom2 |
| `test_main_pivot_highest_severity` | Pivot principal = celui avec severity max |
| `test_no_pivot_main_pivot_none` | Aucun pivot → `main_pivot=None` |
| `test_best_window_is_peak90` | Meilleure fenêtre = bloc avec peak90 max sur top3 |
| `test_caution_flag_sante_low_note` | Santé note ≤ 7 → `caution_flags["sante"]=True` |
| `test_caution_flag_argent_high_vol` | Argent volatilité ≥ 1.5 → flagué |
| `test_no_caution_high_note_low_vol` | Note > 7 et vol < 1.5 → pas de flag |
| `test_tone_positive` | Top 3 moyenne ≥ 13 → `overall_tone="positive"` |
| `test_tone_negative` | Top 3 moyenne ≤ 7 → `overall_tone="negative"` |
| `test_tone_mixed` | Écart top3 ≥ 5 → `overall_tone="mixed"` |
| `test_no_llm_call` | Aucun mock LLM requis (tout est dérivé) |
| `test_contributors_from_explainability` | `top3_contributors_per_category` = données explainability |

---

## Nouveaux fichiers

- `backend/app/prediction/editorial_builder.py` ← CRÉER
- `backend/app/tests/unit/test_editorial_builder.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `EngineOutput`
- `backend/app/prediction/explainability.py` — `ExplainabilityReport`, `ContributorEntry` (35-2)
- `backend/app/prediction/turning_point_detector.py` — `TurningPoint` (34-5)
- `backend/app/prediction/block_generator.py` — `TimeBlock` (34-5)

---

## Checklist de validation

- [ ] Aucun appel LLM dans `EditorialOutputBuilder`
- [ ] `EditorialOutput` intégralement dérivé des scores et métriques
- [ ] Top 3 triés par note décroissante, disjoints du bottom 2
- [ ] Pivot principal = severity max, `None` si absent
- [ ] Meilleure fenêtre correspond au peak90 des top 3
- [ ] Flags prudence santé/argent corrects (note ≤ 7 ou vol ≥ 1.5)
- [ ] Ton global dérivé mécaniquement
- [ ] Top 3 contributeurs par catégorie présents dans la sortie
- [ ] Tous les tests unitaires passent
