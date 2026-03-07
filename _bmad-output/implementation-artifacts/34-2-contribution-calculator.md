# Story 34.2 : Service de contribution `Contribution(e,c,t)`

Status: done


## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `ContributionCalculator` qui calcule la contribution pondérée et bornée de chaque événement pour chaque catégorie,
so that l'agrégateur temporel (story 34-3) dispose de signaux élémentaires précis et correctement normalisés.

## Acceptance Criteria

### AC1 — Formule complète V1

```
Contribution(e,c,t) = clamp(
    w_event × w_planet × w_aspect × f_orb × f_phase × f_target × NS(c) × D(e,c) × Pol(e,c),
    -1.0, +1.0
)
```

### AC2 — `w_aspect` depuis `AspectProfileData.intensity_weight`

Conjonction: 1.00, Opposition: 0.90, Carré: 0.85, Trigone: 0.80, Sextile: 0.65.

### AC3 — `f_orb` parabolique

```
f_orb = 1 − (orb_deg / orb_max)²
```
`f_orb = 0.0` si `orb_deg > orb_max`. `f_orb = 1.0` à orbe 0.

### AC4 — `f_phase`

`applying → 1.05`, `exact → 1.15`, `separating → 0.95`.

### AC5 — `f_target` par classe de cible

Angle (Asc, MC): 1.30, Luminaire (Sun, Moon): 1.20, Personnel (Mercury, Venus, Mars): 1.10, Social (Jupiter, Saturn): 1.00, Transpersonnel (Uranus, Neptune, Pluto): 0.90.

### AC6 — `Pol(e,c)` valence contextuelle

Lue depuis `AspectProfileData.default_valence` et le type de planète. La conjonction n'est jamais automatiquement positive/négative. Valeurs dans `{-1.0, -0.5, 0.0, +0.5, +1.0}`.

### AC7 — Hors orbe → contribution 0.0

Si `f_orb = 0`, retourner `0.0` pour toutes les catégories. Pas d'exception.

### AC8 — Borne `[-1, +1]`

Toutes les valeurs clampées après calcul.

## Tasks / Subtasks

### T1 — `ContributionCalculator` (AC1–AC8)

- [x] Créer `backend/app/prediction/contribution_calculator.py`
  - [x] Constante `TARGET_CLASS_WEIGHTS: dict[str, float]` = mapping classe → f_target
  - [x] Constante `TARGET_CLASS_MAP: dict[str, str]` = mapping planet_code → classe
  - [x] Classe `ContributionCalculator`
  - [x] `compute(event, ns_map, d_map, ctx) -> dict[str, float]`
    - [x] `_w_event(event, ctx) -> float` — depuis `EventTypeData.base_weight`
    - [x] `_w_planet(planet_code, ctx) -> float` — depuis `PlanetProfileData.weight_intraday`
    - [x] `_w_aspect(aspect_code, ctx) -> float` — depuis `AspectProfileData.intensity_weight`
    - [x] `_f_orb(event, ctx) -> float` — parabolique, 0 si hors orbe
    - [x] `_f_phase(event) -> float` — depuis `event.metadata["phase"]`
    - [x] `_f_target(target_code) -> float` — depuis `TARGET_CLASS_WEIGHTS`
    - [x] `_pol(event, cat_code, ctx) -> float` — valence contextuelle
    - [x] Clamp final `[-1, +1]`
    - [x] Si `f_orb == 0` → retourner dict avec 0.0 pour toutes les catégories

### T2 — Tests unitaires (AC1–AC8)

- [x] Créer `backend/app/tests/unit/test_contribution_calculator.py`
  - [x] `test_out_of_orb_all_zero` — `orb_deg > orb_max` → toutes contributions = 0.0
  - [x] `test_exact_orb_max_f_orb` — `orb_deg = 0` → `f_orb = 1.0`
  - [x] `test_f_phase_applying` — `phase="applying"` → `f_phase = 1.05` (fonction dédiée)
  - [x] `test_f_phase_exact` — `phase="exact"` → `f_phase = 1.15` (fonction dédiée)
  - [x] `test_f_phase_separating` — `phase="separating"` → `f_phase = 0.95` (fonction dédiée)
  - [x] `test_saturn_conjunction_mc_negative` — Saturne conjonction MC natal → contribution négative
  - [x] `test_moon_trine_sun_positive` — Lune trigone Soleil natal → contribution positive
  - [x] `test_mars_square_mercury_negative` — Mars carré Mercure natal → contribution négative
  - [x] `test_clamped_to_plus_minus_1` — cas extrême → résultat ∈ `[-1, +1]`
  - [x] `test_f_target_angle_1_30` — cible = Asc ou MC → `f_target = 1.30`

## Dev Notes

### Mapping classe de cible

```python
TARGET_CLASS_MAP: dict[str, str] = {
    "Asc": "angle", "MC": "angle",
    "Sun": "luminary", "Moon": "luminary",
    "Mercury": "personal", "Venus": "personal", "Mars": "personal",
    "Jupiter": "social", "Saturn": "social",
    "Uranus": "transpersonal", "Neptune": "transpersonal", "Pluto": "transpersonal",
}

TARGET_CLASS_WEIGHTS: dict[str, float] = {
    "angle": 1.30, "luminary": 1.20, "personal": 1.10,
    "social": 1.00, "transpersonal": 0.90,
}
```

### Valence contextuelle

```python
def _pol(self, event: AstroEvent, cat_code: str, ctx) -> float:
    aspect_profile = ctx.prediction_context.aspect_profiles.get(event.aspect or "")
    if aspect_profile is None:
        return 1.0
    valence = aspect_profile.default_valence  # "positive", "negative", "neutral", "contextual"
    if valence == "positive":
        return 1.0
    elif valence == "negative":
        return -1.0
    elif valence == "neutral":
        return 0.0
    else:  # "contextual" — utiliser le profil de la planète
        planet_profile = ctx.prediction_context.planet_profiles.get(event.body or "")
        if planet_profile and planet_profile.typical_polarity == "negative":
            return -0.5
        elif planet_profile and planet_profile.typical_polarity == "positive":
            return 0.5
        return 0.0
```

### `_f_orb` implementation

```python
def _f_orb(self, event: AstroEvent, ctx) -> float:
    if event.orb_deg is None:
        return 0.0
    orb_max = self._orb_max(event.body, event.aspect, ctx)
    if event.orb_deg > orb_max:
        return 0.0
    return 1.0 - (event.orb_deg / orb_max) ** 2
```

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/contribution_calculator.py` | Créer |
| `backend/app/tests/unit/test_contribution_calculator.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/prediction/domain_router.py`
- `backend/app/prediction/natal_sensitivity.py`

### Références

- [Source: docs/model_de_calcul_journalier.md — Architecture de scoring, Contribution(e,c,t)]
- [Source: backend/app/infra/db/repositories/prediction_schemas.py — AspectProfileData, PlanetProfileData, EventTypeData]

## Change Log

- Initial implementation of `ContributionCalculator` (AC1-AC8) (Date: 2026-03-07)
- Unit tests added covering all acceptance criteria (Date: 2026-03-07)
- Code review fixes applied (Date: 2026-03-07):
  - H1: Ajout commentaire V1 sur `cat_code` non utilisé dans `_pol()` (intentionnel per AC6)
  - H2: `_w_event()` utilise désormais `event.base_weight` directement (suppression re-lookup redondant)
  - M1: Ajout `logger.warning()` dans `_get_orb_max()` pour le fallback silencieux `orb_max=10.0`
  - M2: `_pol()` retourne `0.0` (au lieu de `1.0`) pour les aspects inconnus
  - M3: Tests de phase scindés en 3 fonctions dédiées (`test_f_phase_applying/exact/separating`)
  - M4: `_f_target()` retourne `1.0` (neutre) pour les cibles inconnues au lieu de "personal"
  - L1: Commentaire `test_clamped_to_plus_minus_1` mis à jour (base_weight=10.0 est désormais utilisé via H2)
  - L2: Nouveau test `test_orb_max_from_metadata` couvrant le chemin metadata
  - L3: Nouveau test `test_unknown_aspect_pol_returns_zero`
  - L4: Comparaison `f_orb == 0.0` remplacée par `f_orb < 1e-9`
- Post-review fixes applied (Date: 2026-03-08):
  - H5: normalisation robuste des lookups planète/aspect pour compatibilité avec les codes DB en minuscules et les `AstroEvent` en `TitleCase`
  - H6: intégration effective de `ContributionCalculator` dans `EngineOrchestrator`
  - M5: test d'intégration orchestrateur ajouté pour verrouiller le runtime réel avec profils référentiels lowercase

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

### Completion Notes List

- Implemented `ContributionCalculator` with all factors: w_event, w_planet, w_aspect, f_orb, f_phase, f_target, NS(c), D(e,c), Pol(e,c).
- Implemented contextual valence `_pol` logic based on aspect and planet profiles.
- Implemented parabolic orb factor `_f_orb` with automated `orb_max` discovery.
- Added comprehensive unit tests covering all ACs and edge cases.
- All tests passed and code follows project standards (Ruff/formatting).
- Runtime now handles lowercase reference codes and `TitleCase` event bodies consistently.
- `ContributionCalculator` is now exercised through the real prediction pipeline, not only in isolation.

### File List

- `backend/app/prediction/contribution_calculator.py`
- `backend/app/tests/unit/test_contribution_calculator.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

