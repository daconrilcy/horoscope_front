# Story 60.15 : Enrichissement Calculs Astrologiques — Progressions, Retours, Nœuds, Étoiles Fixes, Aspects Ciel

Status: done

## Story

En tant qu'utilisateur de la page Horoscope du jour,
je veux voir dans le module "Astrologie du jour" des informations astrologiques plus riches (progressions secondaires, retours planétaires, nœuds lunaires, étoiles fixes activées, aspects inter-planétaires du ciel actuel),
afin d'avoir une lecture astrale complète et précise de ma journée, au-delà des seuls transits de la Lune sur mon thème natal.

## Acceptance Criteria

### AC1 — Aspects inter-planétaires ciel (sky-to-sky) ← priorité max
- Pour chaque pas de temps de la journée, calculer les positions de toutes les planètes visibles (`StepAstroState.planets`), déjà disponibles dans `astro_states`
- Détecter les aspects exacts entre paires de planètes dans le ciel (orbe ≤ 1.5°), sur les 5 aspects classiques (conjonction, sextile, carré, trigone, opposition)
- Exclure les paires non pertinentes : même planète, ou Lune impliquée dans les deux corps (Lune/Lune impossible)
- Prioriser les aspects impliquant au moins une planète lente (Jupiter, Saturne, Uranus) — les aspects Lune/planète-lente sont retenus ; les aspects Mercure/Vénus entre eux sont filtrés si trop nombreux
- Injecter avec `event_type="sky_aspect"`, `body=planète_a`, `target=planète_b`, `aspect=type_aspect`
- Format affiché : "Vénus Trigone Saturne", "Jupiter Carré Neptune"
- Exposer dans `AstroDailyEvents` sous un groupe "Aspects du ciel" qui **remplace** le groupe "Transits actifs" actuel
- Max 4 aspects sky retenus, triés par priorité (planètes lentes en premier)

### AC2 — Nœuds lunaires (Rahu/Ketu)
- Calculer la position du Nœud Nord (Rahu) via `swe.calc_ut(ut_jd, swe.MEAN_NODE)` pour le jour courant
- Ketu = Rahu + 180° (mod 360)
- Détecter les conjonctions et oppositions (orbe ≤ 2°) de planètes en transit avec Rahu ou Ketu sur le day_grid
- Injecter avec `event_type="node_conjunction"`, `body=planète`, `target="north_node"` ou `"south_node"`
- Détecter également les conjonctions/oppositions des nœuds aux planètes **natales** (orbe ≤ 1.5°) — ces aspects sont stables sur la journée
- Format affiché : "Vénus conjoint Nœud Nord", "Mars conjoint Nœud Sud"
- Ajouter `"north_node"` et `"south_node"` dans `PLANET_NAMES_FR` de `public_astro_vocabulary.py` : `"Nœud Nord (Rahu)"`, `"Nœud Sud (Ketu)"`
- Exposer dans `AstroDailyEvents` sous groupe "Nœuds" (conditionnel)
- Inclure les positions Rahu/Ketu dans `planet_positions` si calculées

### AC3 — Retours solaires et lunaires
- **Retour lunaire** : chercher sur le day_grid l'instant où `abs(moon_longitude - natal_moon_longitude) % 360 ≤ 1.0°` → émettre `event_type="lunar_return"`, `body="moon"`, heure locale estimée par interpolation linéaire entre les deux steps encadrants
- **Retour solaire** : chercher sur le day_grid l'instant où `abs(sun_longitude - natal_sun_longitude) % 360 ≤ 0.5°` → émettre `event_type="solar_return"`, `body="sun"`, heure locale estimée
- Format affiché : "Retour Lunaire" / "Retour Solaire" avec heure si disponible
- Exposer dans le groupe "Mouvements" existant (avec ingresses), avec un badge distinctif `type="lunar_return"` ou `type="solar_return"`
- Fréquence : retour lunaire ≈ 1x/mois, retour solaire = 1x/an → la plupart des jours ces groupes sont vides

### AC4 — Progressions secondaires
- Calculer la date progressée : `birth_jd + (age_en_jours_au_local_date / 365.25)` où `age_en_jours = (local_date - birth_date).days`
- Calculer via `swe.calc_ut(progressed_jd, swe_body_id)` les positions progressées de : Soleil, Lune, Mercure, Vénus, Mars
- Détecter les aspects exacts (orbe ≤ 1°) entre planètes progressées et planètes **natales** (dans `natal_chart.planet_positions`)
- Émettre `event_type="progression_aspect"`, `body=f"prog_{planet}"` (ex : `"prog_sun"`), `target=natal_planet`
- Format affiché : "Soleil Progressé Conjoint Vénus natale", "Lune Progressée Carré Saturne natal"
- Exposer dans `AstroDailyEvents` sous groupe "Progressions" (conditionnel, absent si aucun aspect exact)
- Les aspects progressés sont stables sur ~1 mois → émettre 1 seul événement par paire body/target

### AC5 — Étoiles fixes
- Implémenter un catalogue `FIXED_STARS` dans `public_astro_vocabulary.py` avec 10 étoiles majeures et leur longitude écliptique tropicale 2025 :
  ```python
  FIXED_STARS = {
      "regulus":     {"name_fr": "Régulus",    "lon": 150.0},  # Lion 0°
      "algol":       {"name_fr": "Algol",       "lon":  56.0},  # Taureau 26°
      "spica":       {"name_fr": "Spica",       "lon": 203.0},  # Balance 23°
      "antares":     {"name_fr": "Antarès",     "lon": 249.0},  # Scorpion 9°
      "aldebaran":   {"name_fr": "Aldébaran",   "lon":  69.0},  # Gémeaux 9°
      "sirius":      {"name_fr": "Sirius",      "lon": 103.0},  # Cancer 13°
      "fomalhaut":   {"name_fr": "Fomalhaut",   "lon": 333.0},  # Poissons 3°
      "betelgeuse":  {"name_fr": "Bételgeuse",  "lon":  88.0},  # Gémeaux 28°
      "achernar":    {"name_fr": "Achernar",    "lon":  45.0},  # Bélier 15°
      "vega":        {"name_fr": "Véga",        "lon": 285.0},  # Capricorne 15°
  }
  ```
- Détecter les conjonctions (orbe ≤ 1.0°) de planètes en transit avec ces étoiles fixes sur le day_grid
- Émettre `event_type="fixed_star_conjunction"`, `body=planète`, `target=star_key`, `metadata={"star_name_fr": "Régulus"}`
- Format affiché : "Vénus conjoint Régulus", "Lune conjoint Spica"
- Exposer dans `AstroDailyEvents` sous groupe "Étoiles fixes" (conditionnel)

### AC6 — Intégration moteur : nouveau builder `EnrichedAstroEventsBuilder`
- Créer `backend/app/prediction/enriched_astro_events_builder.py` regroupant les 5 calculateurs en un seul builder injectable dans l'orchestrateur
- Signature : `build(astro_states, natal_chart, local_date, birth_date, timezone) -> list[AstroEvent]`
- L'orchestrateur appelle ce builder après `EventDetector.detect()` et **concatène** les événements résultants à `detected_events`
- Ne pas modifier le moteur de scoring (ces nouveaux events n'alimentent pas B(c) ni T(c,t) dans cette story — affichage seulement)

### AC7 — Intégration `PublicAstroDailyEventsPolicy`
- Étendre `public_astro_daily_events.py` pour extraire les nouveaux `event_type` :
  - `"sky_aspect"` → liste `sky_aspects` (remplace `aspects` dans le résultat)
  - `"node_conjunction"` → liste `node_aspects`
  - `"lunar_return"` / `"solar_return"` → liste `returns` avec `{"text", "time", "type"}`
  - `"progression_aspect"` → liste `progressions`
  - `"fixed_star_conjunction"` → liste `fixed_star_conjunctions`
- Les anciens transits Lune-natal (`aspect_exact_to_*`) sont renommés sous clé `transit_aspects` (conservés pour ne pas casser l'affichage si sky_aspects est vide)
- Structure du dict résultat étendue :
  ```python
  {
      "ingresses": [...],
      "returns": [...],            # nouveau
      "sky_aspects": [...],        # nouveau (remplace "aspects")
      "transit_aspects": [...],    # anciens transits lunar (fallback)
      "node_aspects": [...],       # nouveau
      "progressions": [...],       # nouveau
      "fixed_star_conjunctions": [...],  # nouveau
      "planet_positions": [...]
  }
  ```

### AC8 — DTO Pydantic étendu
- Ajouter dans `backend/app/api/v1/routers/predictions.py` :
  ```python
  class DailyPredictionReturn(BaseModel):
      text: str
      time: str | None
      type: str  # "solar_return" | "lunar_return"

  class DailyPredictionAstroDailyEvents(BaseModel):
      ingresses: list[DailyPredictionIngress]
      returns: list[DailyPredictionReturn] = []
      sky_aspects: list[str] = []
      transit_aspects: list[str] = []   # anciens aspects (fallback)
      aspects: list[str] = []           # conservé pour rétrocompatibilité (= sky_aspects || transit_aspects)
      node_aspects: list[str] = []
      progressions: list[str] = []
      fixed_star_conjunctions: list[str] = []
      planet_positions: list[str] | None = None
  ```
- Tous les nouveaux champs ont des valeurs par défaut vides → aucune rupture de compatibilité

### AC9 — Frontend : types, mapper, composant
- Étendre `DailyPredictionAstroDailyEvents` dans `frontend/src/types/dailyPrediction.ts` avec les nouveaux champs optionnels
- Étendre `astroDailyEventsMapper.ts` pour mapper les nouveaux champs
- Étendre `AstroDailyEventsViewData` avec : `skyAspects`, `transitAspects`, `returns`, `nodeAspects`, `progressions`, `fixedStarConjunctions`
- Dans `AstroDailyEvents.tsx` : afficher les nouveaux groupes conditionnels dans cet ordre :
  1. Retours planétaires ("Retours") — si `returns.length > 0`
  2. Mouvements / Ingresses — existant
  3. Aspects du ciel ("Aspects du ciel") — si `skyAspects.length > 0`
  4. Transits actifs — si `skyAspects.length === 0 && transitAspects.length > 0` (fallback)
  5. Nœuds lunaires ("Nœuds") — si `nodeAspects.length > 0`
  6. Progressions ("Progressions") — si `progressions.length > 0`
  7. Étoiles fixes ("Étoiles fixes") — si `fixedStarConjunctions.length > 0`
  8. Positions — existant

### AC10 — Tests
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py` :
  - Test sky_aspects : deux planètes en trigone exact → événement sky_aspect émis
  - Test sky_aspects self : pas d'aspect planète avec elle-même
  - Test nœuds : planète en conjonction avec Rahu → node_conjunction émis
  - Test étoiles fixes : Vénus à 0.5° de Régulus → fixed_star_conjunction émis
  - Test progressions : aspect progressé exact → progression_aspect émis
  - Test retour lunaire : Lune au retour → lunar_return émis
  - Test fallback vide : aucun événement → liste vide (pas d'exception)
- Les tests existants `test_public_astro_daily_events.py` doivent continuer à passer

## Tasks / Subtasks

- [x] T1 — Backend : vocabulaire étendu (AC2, AC5)
  - [x] T1.1 — Ajouter `FIXED_STARS` dans `public_astro_vocabulary.py`
  - [x] T1.2 — Ajouter `"north_node"` / `"south_node"` dans `PLANET_NAMES_FR`
  - [x] T1.3 — Ajouter fonction `get_fixed_star_name_fr(key) -> str`

- [x] T2 — Backend : `EnrichedAstroEventsBuilder` (AC1, AC2, AC3, AC4, AC5, AC6)
  - [x] T2.1 — Créer `backend/app/prediction/enriched_astro_events_builder.py`
  - [x] T2.2 — Implémenter `_compute_sky_aspects(astro_states)` → liste AstroEvent sky_aspect (AC1)
  - [x] T2.3 — Implémenter `_compute_node_conjunctions(astro_states, natal_chart)` (AC2)
  - [x] T2.4 — Implémenter `_compute_returns(astro_states, natal_chart)` → lunar/solar return (AC3)
  - [x] T2.5 — Implémenter `_compute_progressions(natal_chart, local_date, birth_date)` (AC4)
  - [x] T2.6 — Implémenter `_compute_fixed_star_conjunctions(astro_states)` (AC5)
  - [x] T2.7 — Méthode publique `build(...)` qui agrège les 5 listes et retourne `list[AstroEvent]`

- [x] T3 — Backend : intégrer dans l'orchestrateur (AC6)
  - [x] T3.1 — Importer `EnrichedAstroEventsBuilder` dans `engine_orchestrator.py`
  - [x] T3.2 — Appeler `enriched_builder.build(...)` après `event_detector.detect()`
  - [x] T3.3 — Concaténer les événements enrichis à `detected_events`
  - [x] T3.4 — Vérifier que `birth_date` est accessible depuis `loaded_context` ou `EngineInput`

- [x] T4 — Backend : `PublicAstroDailyEventsPolicy` étendue (AC7)
  - [x] T4.1 — Extraire `sky_aspects` (event_type="sky_aspect")
  - [x] T4.2 — Extraire `node_aspects` (event_type="node_conjunction")
  - [x] T4.3 — Extraire `returns` (event_type="lunar_return" / "solar_return")
  - [x] T4.4 — Extraire `progressions` (event_type="progression_aspect")
  - [x] T4.5 — Extraire `fixed_star_conjunctions` (event_type="fixed_star_conjunction")
  - [x] T4.6 — Renommer l'ancienne liste `aspects` en `transit_aspects` dans le dict retourné
  - [x] T4.7 — Ajouter `aspects` comme alias = `sky_aspects or transit_aspects` (rétrocompat)

- [x] T5 — Backend : DTO étendu (AC8)
  - [x] T5.1 — Ajouter `DailyPredictionReturn` dans `predictions.py`
  - [x] T5.2 — Étendre `DailyPredictionAstroDailyEvents` avec tous les nouveaux champs

- [x] T6 — Tests backend (AC10)
  - [x] T6.1 — Créer `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
  - [x] T6.2 — Tests sky aspects (AC1), nœuds (AC2), retours (AC3), progressions (AC4), étoiles fixes (AC5)
  - [x] T6.3 — Vérifier que `test_public_astro_daily_events.py` passe sans modification
  - [x] T6.4 — Lancer `ruff check` + `pytest tests/` avant de valider

- [x] T7 — Frontend : types et mapper (AC9)
  - [x] T7.1 — Étendre `DailyPredictionAstroDailyEvents` dans `dailyPrediction.ts`
  - [x] T7.2 — Étendre `AstroDailyEventsViewData` dans `astroDailyEventsMapper.ts`
  - [x] T7.3 — Mapper les nouveaux champs (avec valeurs par défaut `[]` si absents)

- [x] T8 — Frontend : composant (AC9)
  - [x] T8.1 — Ajouter les labels i18n pour les nouveaux groupes dans `AstroDailyEvents.tsx`
  - [x] T8.2 — Afficher groupe "Retours planétaires" (conditionnel)
  - [x] T8.3 — Afficher groupe "Aspects du ciel" / fallback "Transits actifs" (AC1)
  - [x] T8.4 — Afficher groupe "Nœuds lunaires" (conditionnel)
  - [x] T8.5 — Afficher groupe "Progressions" (conditionnel)
  - [x] T8.6 — Afficher groupe "Étoiles fixes" (conditionnel)
  - [x] T8.7 — Vérifier que `tsc --noEmit` passe

- [x] T9 — Vérification finale
  - [x] T9.1 — `ruff check backend/` passe sans erreur
  - [x] T9.2 — `pytest tests/ app/tests/integration/test_daily_prediction_qa.py` passe
  - [x] T9.3 — `tsc --noEmit` passe côté frontend

## Dev Notes

### Architecture critique — ne pas réinventer

**Réutiliser `swe.calc_ut` exactement comme dans `astro_calculator.py`** :
```python
import swisseph as swe

_FLG = swe.FLG_SWIEPH | swe.FLG_SPEED

# Nœud Nord moyen
xx, _ = swe.calc_ut(ut_jd, swe.MEAN_NODE, _FLG)
north_node_lon = xx[0]
south_node_lon = (north_node_lon + 180.0) % 360.0

# Planète progressée
xx, _ = swe.calc_ut(progressed_jd, swe.SUN, _FLG)
prog_sun_lon = xx[0]
```

**SWE body IDs** (déjà dans `astro_calculator.py`) :
```python
SWE_BODY_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}
# Nœud Nord moyen
swe.MEAN_NODE  # = 10 dans swisseph
```

**`astro_states` est déjà disponible** — c'est `list[StepAstroState]`, chaque step a `.planets: dict[str, PlanetState]` où `PlanetState.longitude` est la longitude écliptique. Pour sky-to-sky : itérer sur pairs de planètes dans chaque step.

**Calcul d'angle entre deux longitudes** :
```python
def angular_distance(lon_a: float, lon_b: float) -> float:
    diff = abs(lon_a - lon_b) % 360.0
    return min(diff, 360.0 - diff)

def aspect_orb(lon_a: float, lon_b: float, aspect_deg: int) -> float:
    return abs(angular_distance(lon_a, lon_b) - aspect_deg)
```

**`birth_date` dans le contexte** — vérifier où `birth_date` est exposé. Regarder `loaded_context: LoadedPredictionContext` qui provient de `context_loader.py`. Le `EngineInput` a `natal_chart: dict[str, Any]` qui contient `birth_date`. Chercher `birth_date` dans `engine_orchestrator.py` pour trouver le bon accès.

**Pattern interne des `AstroEvent`** :
```python
AstroEvent(
    event_type="sky_aspect",
    ut_time=step.ut_jd,
    local_time=step.local_time,
    body="venus",          # lowercase, snake_case
    target="saturn",       # lowercase, snake_case
    aspect="trine",        # lowercase
    orb_deg=0.8,
    priority=70,           # planètes lentes = priorité haute
    base_weight=1.0,
    metadata={},
)
```

**Dédoublonnage sky aspects** — pour éviter de dupliquer le même aspect à chaque step de la journée, utiliser un `set` de tuples `(body, target, aspect)` et émettre uniquement lors de la première détection (ou au minimum d'orbe).

**Format des progressions** — `body` préfixé `"prog_"` pour distinguer des transits normaux :
```python
body = f"prog_{planet_code}"   # ex: "prog_sun", "prog_moon"
```
Dans `get_planet_name_fr()`, il faudra gérer ce préfixe :
```python
if code.startswith("prog_"):
    return f"{get_planet_name_fr(code[5:])} Progressé"
```

### Contraintes CSS / Frontend

- **Jamais Tailwind** — uniquement variables CSS : `var(--glass)`, `var(--glass-2)`, `var(--glass-border)`, `var(--text-1)`, `var(--text-2)`, `var(--primary)`, `var(--success)`
- Nouveau groupe = même structure HTML que les groupes existants dans `AstroDailyEvents.tsx`
- Icônes Lucide pour les nouveaux groupes : `RotateCcw` (retours), `Globe` (aspects ciel), `GitMerge` (nœuds), `Layers` (progressions), `Star` (étoiles fixes — déjà `Star` pour mouvements, utiliser `Sparkles` ou `Zap`)

### Compatibilité rétrograde

- Le champ `aspects` dans le DTO doit être conservé (existant en production). Il doit être égal à `sky_aspects` si non-vide, sinon `transit_aspects`. Cela évite toute rupture du mapper frontend actuel.
- Les nouveaux champs ont des listes vides par défaut → jamais `None` → le mapper frontend peut faire `data.skyAspects ?? []` sans risque.

### Fichiers clés à créer/modifier

**À créer :**
- `backend/app/prediction/enriched_astro_events_builder.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`

**À modifier :**
- `backend/app/prediction/public_astro_vocabulary.py` — `FIXED_STARS`, `PLANET_NAMES_FR` (north_node, south_node), `get_fixed_star_name_fr()`
- `backend/app/prediction/public_astro_daily_events.py` — extraction 5 nouveaux types + renommage `aspects` → `transit_aspects`
- `backend/app/prediction/engine_orchestrator.py` — appel `EnrichedAstroEventsBuilder`
- `backend/app/api/v1/routers/predictions.py` — DTO étendu
- `frontend/src/types/dailyPrediction.ts` — types étendus
- `frontend/src/utils/astroDailyEventsMapper.ts` — mapper étendu
- `frontend/src/components/AstroDailyEvents.tsx` — nouveaux groupes
- `frontend/src/components/AstroDailyEvents.css` — styles supplémentaires si nécessaire

### Références

- `backend/app/prediction/astro_calculator.py` — pattern `swe.calc_ut`, `SWE_BODY_IDS`, `_FLG_SWIEPH_SPEED`
- `backend/app/prediction/event_detector.py` lignes 40-65 — `ASPECTS_V1`, `V1_NATAL_TARGETS`, `_discriminate_exact_code()`
- `backend/app/prediction/schemas.py` lignes 81-95 — `AstroEvent` dataclass (frozen)
- `backend/app/prediction/schemas.py` lignes 55-75 — `PlanetState.longitude`, `StepAstroState.planets`
- `backend/app/prediction/public_astro_daily_events.py` — policy existante à étendre
- `backend/app/prediction/public_astro_vocabulary.py` — vocabulaire à enrichir
- `backend/tests/unit/prediction/test_public_astro_daily_events.py` — pattern de tests à suivre
- `frontend/src/components/AstroDailyEvents.tsx` — composant à étendre
- `frontend/src/utils/astroDailyEventsMapper.ts` — mapper à étendre

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Code review post-implémentation — session 2026-03-20.

### Completion Notes List

**Bug 1 — `base_weight=1.0` sur les événements enrichis (critique)**
- **Symptôme** : Tests QA `test_daily_prediction_qa.py` échouaient avec "Unexpected pivot count: 12 (expected between 2 and 6)". Les événements enrichis (sky aspects, nœuds, progressions, etc.) alimentaient le moteur de scoring via `_build_prediction_outputs`, augmentant artificiellement le nombre de pivots.
- **Fix** : Tous les `AstroEvent` créés dans `enriched_astro_events_builder.py` utilisent `base_weight=0.0` (display-only, sans contribution au signal).
- **Fichier** : `backend/app/prediction/enriched_astro_events_builder.py`

**Bug 2 — `AttributeError: 'datetime.date' object has no attribute 'hour'` dans `prediction_request_resolver.py`**
- **Symptôme** : Prédiction retournait HTTP 503. `profile.birth_date` issu de la DB est de type `datetime.date`, mais le code supposait `datetime.datetime` (appel à `.hour`, `.minute`, `.second`).
- **Fix** : Ajout d'une normalisation `isinstance(birth_date, _date)` → `_dt.combine(birth_date, _time(12, 0))`. Les MagicMock des tests unitaires (non-`date`) sont traités par `birth_date = None`.
- **Fichier** : `backend/app/services/prediction_request_resolver.py`

**Bug 3 — `TypeError: can't subtract offset-naive and offset-aware datetimes` dans `turning_point_detector.py`**
- **Symptôme** : `_compute_progressions` créait un `datetime` naïf via `datetime.combine(local_date, datetime.min.time())` ; `curr.start_local` étant timezone-aware, la soustraction échouait.
- **Fix** : La méthode `build()` passe `ref_dt = astro_states[0].local_time` (timezone-aware) à `_compute_progressions`. Signature mise à jour : `_compute_progressions(natal_chart, local_date, birth_date, ref_local_time: datetime)`.
- **Fichiers** : `backend/app/prediction/enriched_astro_events_builder.py`, `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`

**Bug 4 — `TypeError: Cannot read properties of undefined (reading 'length')` dans `AstroDailyEvents.tsx`**
- **Symptôme** : Crash frontend au rendu du composant. `renderGroup` était appelé avec `items = undefined` (cache React Query avec ancienne prédiction sans les nouveaux champs).
- **Fix** : Signature `renderGroup` étendue à `items: string[] | undefined` + guard `if (!items || items.length === 0) return null`. Idem pour `ingresses && ingresses.length > 0`.
- **Fichier** : `frontend/src/components/AstroDailyEvents.tsx`

### File List

- `backend/app/prediction/enriched_astro_events_builder.py`
- `backend/app/prediction/public_astro_vocabulary.py`
- `backend/app/prediction/public_astro_daily_events.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/schemas.py`
- `backend/app/services/prediction_request_resolver.py`
- `backend/app/api/v1/routers/predictions.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/utils/astroDailyEventsMapper.ts`
- `frontend/src/components/AstroDailyEvents.tsx`
