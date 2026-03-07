# Story 33-1 — Contrat d'entrée/sortie du moteur + orchestrateur de run

## Contexte & Périmètre

**Epic 33 / Story 33-1**
**Chapitre 33** — Fondations du moteur de calcul quotidien

Cette story pose le contrat d'API interne du moteur de prédiction astrologique journalier. Elle définit les schémas canoniques d'entrée et de sortie, ainsi qu'un service orchestrateur qui enchaîne les étapes du moteur sans encore réaliser le scoring complet.

C'est le point d'ancrage de toutes les stories suivantes : chaque composant du moteur (sampler, calculateur, détecteur, scorer) consomme l'entrée canonique et produit vers la structure de sortie définie ici.

---

## Hypothèses & Dépendances

- Les repositories DB existants sont stables et validés :
  - `PredictionReferenceRepository` (`backend/app/infra/db/repositories/prediction_reference_repository.py`)
  - `PredictionRulesetRepository` (`backend/app/infra/db/repositories/prediction_ruleset_repository.py`)
  - `DailyPredictionRepository` (`backend/app/infra/db/repositories/daily_prediction_repository.py`)
- Les schémas de données `PredictionContext`, `RulesetContext` sont déjà définis dans `backend/app/infra/db/repositories/prediction_schemas.py`
- Le thème natal utilisateur est déjà calculé et disponible sous forme d'objet `NatalResult` (depuis `app.domain.astrology.natal_calculation`)
- La librairie `pyswisseph` (ou équivalent) est disponible dans l'environnement backend
- Les dépendances Python sont gérées via `backend/pyproject.toml` uniquement

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Définir le schéma `EngineInput` (entrée canonique du moteur)
- Définir le schéma `EngineOutput` (sortie structurée du run)
- Créer `EngineOrchestrator` : service qui accepte un `EngineInput`, enchaîne les étapes (stubs pour l'instant), retourne un `EngineOutput`
- Calculer et stocker le `input_hash` dès la réception de l'entrée
- Assurer la conversion local → UT dès l'entrée

**Non-Objectifs :**
- Pas de calcul astronomique dans cette story (stub uniquement)
- Pas de scoring, pas de calibration
- Pas de persistance DB dans cette story
- Pas de frontend

---

## Acceptance Criteria

### AC1 — Schéma `EngineInput`
Le schéma `EngineInput` (dataclass ou Pydantic) contient au minimum :
- `natal_chart` : thème natal sérialisé (dict ou objet `NatalResult`)
- `local_date` : date locale (`datetime.date`)
- `timezone` : identifiant IANA (ex. `"Europe/Paris"`)
- `latitude` : float (latitude du jour)
- `longitude` : float (longitude du jour)
- `reference_version` : str (identifiant de la version de référence)
- `ruleset_version` : str (identifiant de la version de ruleset)
- `debug_mode` : bool (défaut `False`)

### AC2 — Schéma `EngineOutput`
Le schéma `EngineOutput` contient au minimum :
- `run_metadata` : objet avec `run_id` (nullable), `computed_at`, `debug_mode`
- `effective_context` : objet avec `house_system_requested`, `house_system_effective`, `timezone`, `input_hash`
- `sampling_timeline` : liste de `SamplePoint` (horodatage UT + local, vide à ce stade)
- `detected_events` : liste d'`AstroEvent` (vide à ce stade)
- `category_scores` : dict catégorie → score (vide à ce stade, placeholder)
- `time_blocks` : liste de blocs UX (vide à ce stade)
- `turning_points` : liste de pivots (vide à ce stade)

### AC3 — Hash d'entrée stable
Le `input_hash` est un SHA-256 hex digest calculé depuis un dict canonique sérialisé contenant au minimum :
- `natal` (thème natal, déterministe)
- `local_date` (ISO 8601)
- `timezone`
- `latitude`, `longitude`
- `reference_version`
- `ruleset_version`

À entrée identique, le hash est toujours identique. À entrée différente (même légèrement), le hash change.

### AC4 — Conversion local → UT
Le `EngineOrchestrator` convertit la `local_date` + `timezone` en intervalle UT (début/fin du jour local) avant tout calcul. Les temps affichés dans `EngineOutput` doivent toujours être restituables en heure locale.

### AC5 — `house_system_requested` vs `house_system_effective`
- `house_system_requested` = valeur issue du ruleset (ex. `"Placidus"`)
- `house_system_effective` = valeur effectivement utilisée (peut différer en cas de repli)
- Les deux champs sont toujours présents dans `effective_context`

### AC6 — Déterminisme
Un run avec le même `EngineInput` produit exactement le même `EngineOutput` (même hash, mêmes métadonnées, mêmes valeurs).

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
├── __init__.py
├── schemas.py           ← EngineInput, EngineOutput, SamplePoint, AstroEvent, ...
└── engine_orchestrator.py  ← EngineOrchestrator
```

### `schemas.py` — extraits clés

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

@dataclass
class EngineInput:
    natal_chart: dict[str, Any]
    local_date: date
    timezone: str
    latitude: float
    longitude: float
    reference_version: str
    ruleset_version: str
    debug_mode: bool = False

@dataclass
class EffectiveContext:
    house_system_requested: str
    house_system_effective: str
    timezone: str
    input_hash: str

@dataclass
class SamplePoint:
    ut_time: float          # Julian Day UT
    local_time: datetime    # heure locale restituée

@dataclass
class AstroEvent:
    event_type: str
    ut_time: float
    local_time: datetime
    body: str | None
    target: str | None
    aspect: str | None
    orb_deg: float | None
    priority: int
    base_weight: float

@dataclass
class EngineOutput:
    run_metadata: dict[str, Any]
    effective_context: EffectiveContext
    sampling_timeline: list[SamplePoint] = field(default_factory=list)
    detected_events: list[AstroEvent] = field(default_factory=list)
    category_scores: dict[str, Any] = field(default_factory=dict)
    time_blocks: list[Any] = field(default_factory=list)
    turning_points: list[Any] = field(default_factory=list)
```

### `engine_orchestrator.py` — structure

```python
class EngineOrchestrator:
    def run(self, engine_input: EngineInput) -> EngineOutput:
        input_hash = self._compute_hash(engine_input)
        ut_start, ut_end = self._local_date_to_ut_interval(
            engine_input.local_date, engine_input.timezone
        )
        # Stubs pour les étapes suivantes (33-2 à 33-6)
        ...
        return EngineOutput(
            run_metadata={...},
            effective_context=EffectiveContext(...),
        )

    def _compute_hash(self, engine_input: EngineInput) -> str:
        # SHA-256 sur dict canonique trié
        ...

    def _local_date_to_ut_interval(
        self, local_date: date, timezone: str
    ) -> tuple[float, float]:
        # Conversion via zoneinfo + ephem ou julday
        ...
```

---

## Tests

### Fichier : `backend/app/tests/unit/test_engine_orchestrator.py`

| Test | Description |
|------|-------------|
| `test_hash_stable` | Même input → même hash |
| `test_hash_changes_on_input_diff` | Input différent (1 champ) → hash différent |
| `test_local_to_ut_conversion` | Date locale Paris → intervalle UT cohérent (vérification par arrondi) |
| `test_output_contains_mandatory_fields` | `EngineOutput` contient tous les champs requis |
| `test_house_system_fields_present` | `house_system_requested` et `house_system_effective` présents |
| `test_determinism` | Appel ×2 avec même input → sorties identiques |
| `test_debug_mode_propagated` | `debug_mode=True` présent dans `run_metadata` |

---

## Nouveaux fichiers

- `backend/app/prediction/__init__.py` ← CRÉER
- `backend/app/prediction/schemas.py` ← CRÉER
- `backend/app/prediction/engine_orchestrator.py` ← CRÉER
- `backend/app/tests/unit/test_engine_orchestrator.py` ← CRÉER

## Fichiers existants à consulter (lecture seule)

- `backend/app/infra/db/repositories/prediction_schemas.py` — `PredictionContext`, `RulesetContext`
- `backend/app/infra/db/models/daily_prediction.py` — `DailyPredictionRunModel`
- `backend/app/infra/db/repositories/daily_prediction_repository.py` — `DailyPredictionRepository`

---

## Checklist de validation

- [ ] `EngineInput` accepte tous les champs requis
- [ ] `EngineOutput` contient tous les placeholders requis
- [ ] `input_hash` stable sur même input, différent sur input modifié
- [ ] Conversion local → UT sans exception pour `Europe/Paris`
- [ ] `house_system_requested` et `house_system_effective` toujours présents
- [ ] Tous les tests unitaires passent
- [ ] Pas de dépendance vers un LLM ou endpoint externe
