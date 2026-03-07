# Story 34-1 — Service de routage domaine `D(e,c)`

## Contexte & Périmètre

**Epic 34 / Story 34-1**
**Chapitre 34** — Scoring, notes et timeline UX

Chaque événement astrologique détecté doit être projeté vers les catégories de l'horoscope (amour, travail, santé, etc.) avec un poids de routage `D(e,c)`. Ce poids combine le vecteur maison (maison natale cible et maison transitante) et la couleur planétaire de l'événement. C'est la première étape du pipeline de scoring.

---

## Hypothèses & Dépendances

- **Dépend de 33-2** : `LoadedPredictionContext` avec `house_category_weights` et `planet_category_weights` disponibles
- **Dépend de 33-5** : `AstroEvent` avec `target` (cible natale), `body` (planète transitante), `natal_house_transited`
- Les matrices `HouseCategoryWeightData` et `PlanetCategoryWeightData` sont déjà chargées dans le contexte
- Le vecteur maison V1 : `70%` sur la maison natale cible, `30%` sur la maison transitante (si différente)
- Le blend planétaire est `D_planet(c) = 0.50 + 0.50 × W_planet_to_cat(c)`

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Implémenter `DomainRouter.route(event, ctx)` → `dict[str, float]` (catégorie → D(e,c))
- Calculer le vecteur maison normalisé (70%/30%)
- Appliquer le blend planétaire pour chaque catégorie
- Calculer `D(e,c)` final pour toutes les catégories actives

**Non-Objectifs :**
- Pas de scoring ni de contribution (c'est 34-2)
- Pas de persistance

---

## Acceptance Criteria

### AC1 — Vecteur maison normalisé
Le vecteur maison `H_e` est construit comme suit :
- Si la planète transitante touche une cible natale dans la maison `h_natal` : poids `0.70` sur `h_natal`
- Si la maison transitante `h_transit ≠ h_natal` : poids `0.30` sur `h_transit`
- Si `h_transit == h_natal` : poids `1.00` sur `h_natal`
- La somme du vecteur maison = 1.0 (normalisé)

### AC2 — Mapping maison → catégories
Pour chaque maison dans le vecteur, le poids maison est distribué sur les catégories via `HouseCategoryWeightData`.
Exemple : maison 7 avec poids 0.70 → catégorie "amour" avec `house_weight = 0.80` → contribution 0.70 × 0.80 = 0.56 sur "amour".

### AC3 — Blend planétaire
`D_planet(c) = 0.50 + 0.50 × W_planet_to_cat(c)` où `W_planet_to_cat(c)` vient de `PlanetCategoryWeightData`.
- `D_planet(c)` est toujours dans `[0.50, 1.00]` (la couleur planétaire n'annule jamais le routage maison)

### AC4 — D(e,c) final
`D(e,c) = sum_maisons(H_e[h] × house_to_cat[h][c]) × D_planet(c)`

Ce produit est calculé pour toutes les catégories actives.

### AC5 — Couverture totale des catégories
`D(e,c)` est calculé pour chaque catégorie active, même si la valeur est nulle.

### AC6 — Événements non-aspect (heures planétaires, ingresses)
Pour les événements sans cible natale (`target=None`), le routage se fait uniquement via `D_planet(c)` avec un vecteur maison neutre uniforme (ou via `event_type` si routage spécifique défini dans le contexte).

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── domain_router.py    ← DomainRouter
```

### `domain_router.py` — extraits clés

```python
from app.prediction.schemas import AstroEvent
from app.prediction.context_loader import LoadedPredictionContext

class DomainRouter:
    def route(
        self,
        event: AstroEvent,
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        """Retourne D(e,c) pour chaque catégorie active."""
        house_vector = self._build_house_vector(event)
        category_weights_from_houses = self._project_houses_to_categories(
            house_vector, ctx
        )
        planet_blend = self._compute_planet_blend(event.body, ctx)
        result = {}
        for cat in ctx.prediction_context.categories:
            if not cat.is_enabled:
                continue
            d_house = category_weights_from_houses.get(cat.code, 0.0)
            d_planet = planet_blend.get(cat.code, 0.5)
            result[cat.code] = d_house * d_planet
        return result

    def _build_house_vector(self, event: AstroEvent) -> dict[int, float]:
        """Construit le vecteur maison 70/30 depuis l'événement."""
        ...

    def _project_houses_to_categories(
        self,
        house_vector: dict[int, float],
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        ...

    def _compute_planet_blend(
        self,
        planet_code: str | None,
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        """D_planet(c) = 0.50 + 0.50 * W_planet_to_cat(c)"""
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_domain_router.py`

| Test | Description |
|------|-------------|
| `test_house_vector_sum_is_one` | Vecteur maison 70/30 → somme = 1.0 |
| `test_house_vector_single_when_same_house` | Maison cible = maison transitante → poids 1.0 unique |
| `test_planet_blend_in_range` | `D_planet(c) ∈ [0.5, 1.0]` pour toutes les catégories |
| `test_d_e_c_all_categories_covered` | Dict résultat contient toutes les catégories actives |
| `test_d_e_c_house7_heavy_amour` | Maison 7 avec fort poids amour → D("amour") élevé |
| `test_no_target_uses_uniform_vector` | Événement sans cible → routage via blend planétaire seul |
| `test_planet_blend_never_cancels_routing` | `D_planet(c) ≥ 0.5` toujours → jamais annulation totale |

---

## Nouveaux fichiers

- `backend/app/prediction/domain_router.py` ← CRÉER
- `backend/app/tests/unit/test_domain_router.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `AstroEvent` (33-1)
- `backend/app/prediction/context_loader.py` — `LoadedPredictionContext` (33-2)
- `backend/app/infra/db/repositories/prediction_schemas.py` — `HouseCategoryWeightData`, `PlanetCategoryWeightData`

---

## Checklist de validation

- [ ] Somme vecteur maison = 1.0
- [ ] `D_planet(c) ∈ [0.5, 1.0]` pour toutes catégories
- [ ] `D(e,c)` calculé pour toutes les catégories actives
- [ ] Maison cible seule (maison cible = maison transit) → poids 1.0
- [ ] Événement sans cible → routage planétaire seul, pas d'exception
- [ ] Tous les tests unitaires passent
