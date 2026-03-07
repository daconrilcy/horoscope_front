# Story 33-5 — Détecteur d'événements astrologiques V1

## Contexte & Périmètre

**Epic 33 / Story 33-5**
**Chapitre 33** — Fondations du moteur de calcul quotidien

Le détecteur transforme la séquence de `StepAstroState` produite par `AstroCalculator` en événements atomiques horodatés. Chaque événement représente un fait astrologique discret (entrée/sortie d'orbe, exactitude d'un aspect, changement de signe lunaire, changement de signe ascendant, début d'heure planétaire) avec son heure locale et UT, ses paramètres et son poids de base.

---

## Hypothèses & Dépendances

- **Dépend de 33-4** : `AstroCalculator`, `StepAstroState`, `PlanetState` disponibles
- `AstroEvent` est défini dans `backend/app/prediction/schemas.py` (story 33-1)
- Les profils d'aspects (`AspectProfileData`) et profils planètes (`PlanetProfileData`) sont disponibles via `LoadedPredictionContext` (story 33-2)
- Les orbes par planète et par aspect sont chargés depuis le contexte (table `prediction_schemas.PlanetProfileData.orb_active_deg`, modulation par aspect)
- Le thème natal est disponible comme dict de positions natales `{code: longitude}`

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Détecter les aspects transit → natal : `enter_orb`, `exact`, `exit_orb` avec statut `applying/separating`
- Détecter les changements de signe de la Lune (`moon_sign_ingress`)
- Détecter les changements de signe de l'Ascendant (`asc_sign_change`)
- Détecter les débuts d'heures planétaires (`planetary_hour_change`)
- Enrichir chaque `AstroEvent` avec type, horodatages, corps, cible, aspect, orbe, priorité, poids de base

**Non-Objectifs :**
- Pas de scoring ni de contribution dans ce service
- Pas d'aspects transit → transit (V1 = transit → natal uniquement)
- Pas d'aspects mineurs (quinconx, semi-carré, etc.)
- Pas d'étoiles fixes ni de maisons arabes

---

## Acceptance Criteria

### AC1 — Aspects V1 uniquement
Seuls les 5 aspects majeurs ptolémaïques sont détectés : conjonction (0°), sextile (60°), carré (90°), trigone (120°), opposition (180°).

### AC2 — Cibles natales V1
Les cibles natales sont limitées aux 10 planètes natales + Asc natal + MC natal. Tout autre point natal est ignoré.

### AC3 — `enter_orb`, `exact`, `exit_orb`
Pour chaque aspect transit→natal :
- `enter_orb` : détecté quand l'orbe passe sous `orb_max(planete, aspect)` en descendant
- `exact` : détecté à l'orbe minimal du segment (changement de signe de la dérivée)
- `exit_orb` : détecté quand l'orbe repasse au-dessus de `orb_max`
- Ces 3 événements sont distincts et horodatés séparément
- Si le pas de 15 min est trop grossier, utiliser le raffinement à 1 min (appel à `TemporalSampler.refine_around`)

### AC4 — `applying` / `separating`
- `applying = True` si l'orbe décroît d'un pas à l'autre (planète s'approche)
- `separating = True` si l'orbe croît (planète s'éloigne)
- Chaque événement d'aspect porte `applying` ou `separating` (booléen dans `AstroEvent.metadata`)

### AC5 — `moon_sign_ingress`
Quand la Lune change de signe entre deux pas consécutifs, un événement `moon_sign_ingress` est créé avec :
- `body = "Moon"`, `target = None`
- `local_time` et `ut_time` interpolés entre les deux pas
- `metadata.from_sign`, `metadata.to_sign`

### AC6 — `asc_sign_change`
Quand l'Ascendant change de signe entre deux pas consécutifs, un événement `asc_sign_change` est créé.

### AC7 — `planetary_hour_change`
Les 24 heures planétaires de la journée sont calculées à partir des heures de lever/coucher solaire (depuis `DayGrid`). Chaque début d'heure planétaire produit un événement `planetary_hour_change` avec `metadata.ruler` (planète régissant l'heure).

### AC8 — Enrichissement complet de `AstroEvent`
Chaque événement porte : `event_type`, `ut_time`, `local_time`, `body`, `target`, `aspect`, `orb_deg`, `priority` (depuis `EventTypeData`), `base_weight` (depuis `EventTypeData`).

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── event_detector.py    ← EventDetector
```

### `event_detector.py` — extraits clés

```python
from app.prediction.schemas import AstroEvent, SamplePoint
from app.prediction.astro_calculator import StepAstroState
from app.prediction.temporal_sampler import DayGrid
from app.prediction.context_loader import LoadedPredictionContext

ASPECTS_V1 = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}

class EventDetector:
    def __init__(self, ctx: LoadedPredictionContext, natal_positions: dict[str, float]):
        self.ctx = ctx
        self.natal_positions = natal_positions  # {code: longitude_deg}

    def detect(
        self,
        steps: list[StepAstroState],
        day_grid: DayGrid,
    ) -> list[AstroEvent]:
        events = []
        events.extend(self._detect_aspects(steps))
        events.extend(self._detect_moon_ingress(steps))
        events.extend(self._detect_asc_sign_change(steps))
        events.extend(self._detect_planetary_hours(day_grid))
        return sorted(events, key=lambda e: e.ut_time)

    def _orb(self, transit_lon: float, natal_lon: float, aspect_deg: int) -> float:
        """Calcule l'orbe signé pour un aspect donné."""
        ...

    def _orb_max(self, planet_code: str, aspect_code: str) -> float:
        """Retourne l'orbe maximum pour cette planète/aspect depuis le contexte."""
        ...
```

### Calcul des heures planétaires

L'ordre des régents planétaires des heures suit la séquence traditionnelle Chaldéenne :
`Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon` (cycle de 7, répété sur 24h).
La durée d'une heure planétaire = `(sunset_ut - sunrise_ut) / 12` pour les heures diurnes,
et `(sunrise_ut_next_day - sunset_ut) / 12` pour les heures nocturnes.

---

## Tests

### Fichier : `backend/app/tests/unit/test_event_detector.py`

| Test | Description |
|------|-------------|
| `test_exact_aspect_detected` | Séquence de pas avec orbe à 0.05° → événement `exact` créé |
| `test_enter_orb_detected` | Orbe passe de 2.5° → 1.8° avec orb_max=2.0° → `enter_orb` |
| `test_exit_orb_detected` | Orbe passe de 1.8° → 2.5° avec orb_max=2.0° → `exit_orb` |
| `test_applying_when_orb_decreasing` | Orbe décroissant → `applying=True` |
| `test_separating_when_orb_increasing` | Orbe croissant → `separating=True` |
| `test_moon_sign_ingress_detected` | Lune passe de 29.5° Taureau à 0.5° Gémeaux → `moon_sign_ingress` |
| `test_asc_sign_change_detected` | Asc passe de 29.8° à 0.2° → `asc_sign_change` |
| `test_24_planetary_hours` | Journée complète → exactement 24 événements `planetary_hour_change` |
| `test_aspect_targets_v1_only` | Corps hors V1 dans natal_positions → ignoré |
| `test_minor_aspects_ignored` | Quinconx (150°) → aucun événement |
| `test_events_sorted_by_time` | Liste retournée triée par `ut_time` croissant |

---

## Nouveaux fichiers

- `backend/app/prediction/event_detector.py` ← CRÉER
- `backend/app/tests/unit/test_event_detector.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/prediction/schemas.py` — `AstroEvent`
- `backend/app/prediction/astro_calculator.py` — `StepAstroState`, `PlanetState` (33-4)
- `backend/app/prediction/temporal_sampler.py` — `DayGrid` (33-3)
- `backend/app/prediction/context_loader.py` — `LoadedPredictionContext` (33-2)
- `backend/app/infra/db/repositories/prediction_schemas.py` — `EventTypeData`, `AspectProfileData`
- `docs/model_de_calcul_journalier.md` — orbes V1, heures planétaires

---

## Checklist de validation

- [ ] `enter_orb`, `exact`, `exit_orb` détectés sur aspect test connu
- [ ] `applying` vrai sur orbe décroissante, `separating` vrai sur orbe croissante
- [ ] `moon_sign_ingress` créé lors d'un changement de signe lunaire
- [ ] `asc_sign_change` créé lors d'un changement de signe ascendant
- [ ] 24 événements `planetary_hour_change` sur journée complète
- [ ] Aspects mineurs (quinconx, etc.) non détectés
- [ ] Événements triés par `ut_time`
- [ ] Tous les tests unitaires passent
