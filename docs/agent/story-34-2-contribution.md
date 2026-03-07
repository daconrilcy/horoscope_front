# Story 34-2 — Service de contribution `Contribution(e,c,t)`

## Contexte & Périmètre

**Epic 34 / Story 34-2**
**Chapitre 34** — Scoring, notes et timeline UX

La contribution est le signal élémentaire produit par chaque événement astrologique pour chaque catégorie à un instant `t`. C'est la multiplication de tous les facteurs de pondération : poids de l'événement, de la planète, de l'aspect, décroissance d'orbe, phase, type de cible, sensibilité natale, routage domaine et polarité. Le résultat est borné dans `[-1, +1]`.

---

## Hypothèses & Dépendances

- **Dépend de 33-5** : `AstroEvent` avec tous les champs requis (orbe, phase applying/separating, type d'événement)
- **Dépend de 33-6** : `NS(c)` dict catégorie → float disponible pour le run
- **Dépend de 34-1** : `D(e,c)` dict catégorie → float disponible pour chaque événement
- Les poids `w_event`, `w_planet`, `w_aspect` viennent de `EventTypeData.base_weight`, `PlanetProfileData`, `AspectProfileData`
- La valence de polarité `Pol(e,c)` est contextuelle : la conjonction n'est jamais automatiquement positive ou négative

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Implémenter `ContributionCalculator.compute(event, ns_map, d_map, ctx)` → `dict[str, float]`
- Calculer la formule complète pour chaque catégorie active
- Borner chaque valeur dans `[-1, +1]`

**Non-Objectifs :**
- Pas d'agrégation temporelle (c'est 34-3)
- Pas de persistance
- Pas de calcul de polarité LLM (la valence est dérivée des données de référence)

---

## Acceptance Criteria

### AC1 — Formule complète V1
```
Contribution(e,c,t) = clamp(
    w_event(e) × w_planet(e) × w_aspect(e) × f_orb(e) × f_phase(e) × f_target(e) × NS(c) × D(e,c) × Pol(e,c),
    -1.0, +1.0
)
```

### AC2 — `w_aspect` selon les poids V1
Poids d'aspect issus de `AspectProfileData.intensity_weight` :
- Conjonction : 1.00
- Opposition : 0.90
- Carré : 0.85
- Trigone : 0.80
- Sextile : 0.65

### AC3 — `f_orb` décroissance parabolique
```
f_orb = 1 − (orb_deg / orb_max) ^ 2
```
- `f_orb = 1.0` à orbe 0 (exact)
- `f_orb = 0.0` à orbe = `orb_max`
- `f_orb = 0.0` si `orb_deg > orb_max` (hors orbe → contribution nulle)

### AC4 — `f_phase` selon le statut
- `applying` → `f_phase = 1.05`
- `exact` → `f_phase = 1.15`
- `separating` → `f_phase = 0.95`

### AC5 — `f_target` selon la classe de la cible natale
- Angle (Asc, MC) → `f_target = 1.30`
- Luminaire (Sun, Moon) → `f_target = 1.20`
- Planète personnelle (Mercury, Venus, Mars) → `f_target = 1.10`
- Planète sociale (Jupiter, Saturn) → `f_target = 1.00`
- Planète transpersonnelle (Uranus, Neptune, Pluto) → `f_target = 0.90`

### AC6 — `Pol(e,c)` valence contextuelle
- La valence est lue depuis `AspectProfileData.default_valence` et le contexte de l'événement
- La conjonction n'est jamais codée automatiquement positive ou négative : sa valence dépend des planètes impliquées (lue depuis le contexte)
- La valeur de `Pol(e,c)` est dans `{-1.0, -0.5, 0.0, +0.5, +1.0}` selon la configuration

### AC7 — Hors orbe → contribution nulle
Si `f_orb = 0` (orbe hors seuil), `Contribution(e,c,t) = 0.0` pour toutes les catégories. Pas d'exception.

### AC8 — Borne `[-1, +1]`
Chaque valeur est clampée après calcul. Aucune valeur hors de `[-1, +1]` n'est retournée.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── contribution_calculator.py    ← ContributionCalculator
```

### `contribution_calculator.py` — extraits clés

```python
from app.prediction.schemas import AstroEvent
from app.prediction.context_loader import LoadedPredictionContext

TARGET_CLASS_WEIGHTS = {
    "angle": 1.30,
    "luminary": 1.20,
    "personal": 1.10,
    "social": 1.00,
    "transpersonal": 0.90,
}

class ContributionCalculator:
    def compute(
        self,
        event: AstroEvent,
        ns_map: dict[str, float],      # catégorie → NS(c)
        d_map: dict[str, float],       # catégorie → D(e,c)
        ctx: LoadedPredictionContext,
    ) -> dict[str, float]:
        """Retourne Contribution(e,c,t) pour chaque catégorie active."""
        w_event = self._w_event(event, ctx)
        w_planet = self._w_planet(event.body, ctx)
        w_aspect = self._w_aspect(event.aspect, ctx)
        f_orb = self._f_orb(event, ctx)
        f_phase = self._f_phase(event)
        f_target = self._f_target(event.target, ctx)

        if f_orb == 0.0:
            return {cat.code: 0.0 for cat in ctx.prediction_context.categories if cat.is_enabled}

        result = {}
        for cat in ctx.prediction_context.categories:
            if not cat.is_enabled:
                continue
            pol = self._pol(event, cat.code, ctx)
            ns = ns_map.get(cat.code, 1.0)
            d = d_map.get(cat.code, 0.0)
            raw = w_event * w_planet * w_aspect * f_orb * f_phase * f_target * ns * d * pol
            result[cat.code] = max(-1.0, min(1.0, raw))
        return result

    def _f_orb(self, event: AstroEvent, ctx: LoadedPredictionContext) -> float:
        orb_max = self._orb_max(event.body, event.aspect, ctx)
        if event.orb_deg is None or event.orb_deg > orb_max:
            return 0.0
        return 1.0 - (event.orb_deg / orb_max) ** 2

    def _f_phase(self, event: AstroEvent) -> float:
        phase = (event.metadata or {}).get("phase", "separating")
        return {"applying": 1.05, "exact": 1.15, "separating": 0.95}.get(phase, 0.95)
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_contribution_calculator.py`

| Test | Description |
|------|-------------|
| `test_out_of_orb_returns_zero` | `orb_deg > orb_max` → toutes contributions = 0 |
| `test_exact_orb_gives_max_local` | `orb_deg = 0` → `f_orb = 1.0`, contribution maximale locale |
| `test_f_phase_applying` | `phase="applying"` → `f_phase = 1.05` |
| `test_f_phase_exact` | `phase="exact"` → `f_phase = 1.15` |
| `test_f_phase_separating` | `phase="separating"` → `f_phase = 0.95` |
| `test_saturn_conjunction_mc_negative` | Saturne conjonction MC natal → contribution négative sur catégorie concernée |
| `test_moon_trine_sun_positive` | Lune trigone Soleil natal → contribution positive |
| `test_mars_square_mercury_negative` | Mars carré Mercure natal → contribution négative localisée |
| `test_conjunction_polarity_contextual` | Conjonction Jupiter/MC → positif, Saturne/Mars → négatif (selon contexte) |
| `test_contribution_clamped` | Cas extrême → résultat dans `[-1, +1]` |
| `test_f_target_angle_highest` | Cible = Asc ou MC → `f_target = 1.30` |

---

## Nouveaux fichiers

- `backend/app/prediction/contribution_calculator.py` ← CRÉER
- `backend/app/tests/unit/test_contribution_calculator.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `AstroEvent`
- `backend/app/prediction/domain_router.py` — `D(e,c)` (34-1)
- `backend/app/prediction/natal_sensitivity.py` — `NS(c)` (33-6)
- `backend/app/infra/db/repositories/prediction_schemas.py` — `AspectProfileData`, `PlanetProfileData`, `EventTypeData`
- `docs/model_de_calcul_journalier.md` — formule Contribution, barèmes f_target

---

## Checklist de validation

- [ ] Formule complète appliquée avec tous les facteurs
- [ ] Hors orbe → contribution = 0 (pas d'exception)
- [ ] `f_orb` parabolique correct à orbe 0, orbe max et hors orbe
- [ ] `f_phase` correct pour les 3 phases
- [ ] `f_target` correct par classe de cible
- [ ] Conjonction : valence contextuelle (pas hard-codée positive/négative)
- [ ] Contribution bornée dans `[-1, +1]`
- [ ] Tous les tests unitaires passent
