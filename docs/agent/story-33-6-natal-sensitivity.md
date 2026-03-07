# Story 33-6 — Calculateur de sensibilité natale `NS(c)`

## Contexte & Périmètre

**Epic 33 / Story 33-6**
**Chapitre 33** — Fondations du moteur de calcul quotidien

La sensibilité natale `NS(c)` est un coefficient multiplicateur calculé une seule fois par run, par catégorie. Il module l'intensité des contributions en fonction de la configuration natale de l'utilisateur : occupation des maisons (planètes natales dans les maisons liées à la catégorie), rulership (maître du signe de la maison natale), angularité (présence sur les angles MC/Asc), et dominance (aspect natal fort sur un angle). Ce coefficient amplifie ou atténue le signal brut selon le thème de l'utilisateur.

---

## Hypothèses & Dépendances

- **Dépend de 33-2** : `LoadedPredictionContext` avec `PredictionContext` (catégories, profils planètes, house_category_weights, rulerships, aspect_profiles) disponible
- Le thème natal est fourni comme dict structuré contenant positions natales, maisons natales, maître de chaque signe de maison
- La formule V1 est figée : `NS(c) = clip(Occ + Rul + Ang + Dom + 1.0, 0.75, 1.25)` (1.0 = neutre)
- `Dom` reste optionnel en V1 : si non calculé, il vaut 0 (neutre) — code doit supporter sa neutralisation explicite
- La calibration des poids `Occ`, `Rul`, `Ang`, `Dom` est issue du contexte ruleset

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Implémenter `NatalSensitivityCalculator.compute(natal_chart, ctx)` → `dict[str, float]` (catégorie → NS)
- Calculer les 4 composantes `Occ`, `Rul`, `Ang`, `Dom` selon les barèmes V1
- Borner chaque `NS(c)` dans `[0.75, 1.25]`
- Calculer `NS(c)` pour toutes les catégories actives du contexte

**Non-Objectifs :**
- Pas de calcul de contributions (c'est 34-2)
- Pas de calcul d'aspects transit (c'est 33-5)
- `Dom` peut être neutralisé (valeur 0) sans erreur ni exception

---

## Acceptance Criteria

### AC1 — Calcul pour toutes les catégories actives
`compute(natal_chart, ctx)` retourne un dict avec une entrée pour chaque `CategoryData.code` dont `is_enabled=True`.

### AC2 — Formule V1 respectée
```
NS(c) = clip(1.0 + w_occ * Occ(c) + w_rul * Rul(c) + w_ang * Ang(c) + w_dom * Dom(c), 0.75, 1.25)
```
Où `w_occ`, `w_rul`, `w_ang`, `w_dom` proviennent des paramètres du ruleset.

### AC3 — Composante `Occ` (Occupation)
`Occ(c)` = somme des poids natals des planètes natales occupant les maisons associées à la catégorie `c`.
- Les poids nataux par classe de planète proviennent de `PlanetProfileData.weight_day_climate` (ou équivalent paramétré)
- Une maison "associée" à la catégorie est celle dont `HouseCategoryWeightData.category_code == c` avec `weight > 0`

### AC4 — Composante `Rul` (Rulership)
`Rul(c)` = somme sur les maisons associées à `c` : si le maître du signe de la cuspide de cette maison natale est en maison angulaire ou dans une maison liée à `c`, le rulership contribue selon les barèmes.
- Les rulerships de signes viennent de `PredictionContext.sign_rulerships`

### AC5 — Composante `Ang` (Angularité)
`Ang(c)` = contribution des planètes natales situées dans les maisons angulaires (1, 4, 7, 10), pondérées par leur lien à la catégorie `c`.
- Une planète natale angulaire au MC ou Asc contribue davantage.

### AC6 — Composante `Dom` optionnelle
`Dom(c)` peut être fournie (aspects nataux forts sur MC/Asc) ou neutralisée (`= 0`). Le code ne lève pas d'exception si `Dom` est désactivé.

### AC7 — Borne `[0.75, 1.25]`
Chaque `NS(c)` est strictement bornée après calcul. Aucune valeur hors de cette plage ne peut être retournée.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── natal_sensitivity.py    ← NatalSensitivityCalculator
```

### `natal_sensitivity.py` — extraits clés

```python
from dataclasses import dataclass
from app.prediction.context_loader import LoadedPredictionContext

NS_MIN = 0.75
NS_MAX = 1.25

@dataclass
class NatalChart:
    """Représentation minimaliste du thème natal pour NS(c)."""
    planet_positions: dict[str, float]   # code → longitude natale
    planet_houses: dict[str, int]        # code → maison natale (1–12)
    house_sign_rulers: dict[int, str]    # maison → code planète régente du signe de la cuspide

class NatalSensitivityCalculator:
    def compute(
        self,
        natal: NatalChart,
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        """Retourne NS(c) pour chaque catégorie active."""
        result = {}
        pc = ctx.prediction_context
        params = ctx.ruleset_context.parameters

        w_occ = float(params.get("ns_weight_occ", 0.15))
        w_rul = float(params.get("ns_weight_rul", 0.10))
        w_ang = float(params.get("ns_weight_ang", 0.10))
        w_dom = float(params.get("ns_weight_dom", 0.0))  # 0 = désactivé V1

        for cat in pc.categories:
            if not cat.is_enabled:
                continue
            occ = self._compute_occ(natal, cat.code, pc)
            rul = self._compute_rul(natal, cat.code, pc)
            ang = self._compute_ang(natal, cat.code, pc)
            dom = self._compute_dom(natal, cat.code, pc) if w_dom > 0 else 0.0
            raw = 1.0 + w_occ * occ + w_rul * rul + w_ang * ang + w_dom * dom
            result[cat.code] = max(NS_MIN, min(NS_MAX, raw))

        return result
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_natal_sensitivity.py`

| Test | Description |
|------|-------------|
| `test_ns_present_for_all_active_categories` | Toutes les catégories actives ont une entrée dans le résultat |
| `test_ns_bounds_always_respected` | Pour tout contexte synthétique, NS ∈ [0.75, 1.25] |
| `test_no_occupation_neutral` | Aucune planète dans les maisons liées → NS ≈ 1.0 |
| `test_strong_occupation_raises_ns` | Plusieurs planètes lourdes dans maisons liées → NS > 1.0 |
| `test_angular_ruler_raises_ns` | Maître de maison angulaire → NS augmenté |
| `test_dom_disabled_no_exception` | `w_dom=0` dans params → aucune exception, Dom=0 |
| `test_ns_capped_at_1_25` | Contexte synthétique extrême → NS exactement 1.25 (jamais > 1.25) |
| `test_ns_floored_at_0_75` | Contexte synthétique inverse → NS exactement 0.75 (jamais < 0.75) |

---

## Nouveaux fichiers

- `backend/app/prediction/natal_sensitivity.py` ← CRÉER
- `backend/app/tests/unit/test_natal_sensitivity.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/context_loader.py` — `LoadedPredictionContext` (33-2)
- `backend/app/infra/db/repositories/prediction_schemas.py` — `PredictionContext`, `HouseCategoryWeightData`, `PlanetProfileData`
- `docs/model_de_calcul_journalier.md` — formule NS(c), barèmes V1

---

## Checklist de validation

- [ ] `NS(c)` calculé pour toutes les catégories actives
- [ ] Bornes `[0.75, 1.25]` respectées dans tous les cas
- [ ] `Occ` utilise les poids nataux par classe de planète
- [ ] `Rul` repose sur les rulerships de signes du contexte
- [ ] `Ang` applique la logique maison angulaire
- [ ] `Dom = 0` quand désactivé, sans exception
- [ ] Tous les tests unitaires passent (mocks, sans DB)
