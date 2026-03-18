# Story 60.5 : Isoler le point de bascule comme objet narratif propre

Status: review

## Story

En tant qu'utilisateur,
je veux voir un bloc dédié qui m'explique clairement ce qui change et quoi faire à ce moment charnière,
afin de ne pas confondre le turning point avec la meilleure fenêtre et de comprendre immédiatement l'impact sur ma journée.

## Acceptance Criteria

1. Le payload expose `turning_point: dict | None` — objet unique (le turning point le plus significatif), `null` si aucun turning point significatif.
2. `turning_point` contient : `time: str` (HH:MM), `title: str`, `change_type: str`, `affected_domains: list[str]` (clefs publiques, max 3), `what_changes: str`, `do: str`, `avoid: str`.
3. `title` est non technique (ex: "Retour au calme", "Virage côté pro", "Montée en puissance") — jamais un code de catégorie brut.
4. `change_type` reprises les valeurs Story 43.1 : `"emergence"`, `"recomposition"`, `"attenuation"`.
5. `what_changes` est une phrase courte (max 15 mots) décrivant l'effet concret du turning point.
6. `do` et `avoid` sont des listes de 2–3 actions courtes (max 4 mots chacune).
7. `affected_domains` utilise les clefs publiques (Story 60.1), pas les codes internes.
8. Le bloc n'est rendu que si au moins un turning point a `severity ≥ 0.3` et `confidence ≥ 0.5`.
9. Le champ `turning_points` existant (liste complète) est conservé (rétrocompat).
10. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Créer `PublicTurningPointPolicy` dans `public_projection.py` (AC: 1, 8)
  - [x] T1.1 Lire `backend/app/prediction/turning_point_detector.py` — `V3TurningPoint`, champs disponibles : `local_time, reason, change_type, primary_driver, movement, category_deltas, categories_impacted, severity, confidence`
  - [x] T1.2 Lire `backend/app/prediction/schemas.py` — `V3TurningPoint`, `V3Movement`, `V3CategoryDelta`
  - [x] T1.3 Créer classe `PublicTurningPointPolicy` avec méthode `build(turning_points: list[V3TurningPoint], domain_mapping) -> dict | None`
  - [x] T1.4 Sélection : filtrer `severity >= 0.3 AND confidence >= 0.5`, prendre le premier (plus ancien ou plus fort selon `severity`)
  - [x] T1.5 Si liste vide après filtre → retourner `None`

- [x] T2 — Construire le `title` non technique (AC: 3)
  - [x] T2.1 Logique basée sur `change_type` + domaine dominant :
    ```python
    TITLE_TEMPLATES = {
        ("emergence", "pro_ambition"): "Montée en puissance côté pro",
        ("emergence", "relations_echanges"): "Ouverture relationnelle",
        ("emergence", "energie_bienetre"): "Regain d'énergie",
        ("recomposition", ...): "Virage ...",
        ("attenuation", ...): "Retour au calme",
    }
    # Fallback générique par change_type
    FALLBACK_TITLES = {
        "emergence": "Montée en puissance",
        "recomposition": "Virage de la journée",
        "attenuation": "Retour au calme",
    }
    ```
  - [x] T2.2 Domaine dominant = premier item de `affected_domains` (domaine public le plus impacté)

- [x] T3 — Construire `what_changes` (AC: 5)
  - [x] T3.1 Utiliser `V3Movement.direction` + `V3Movement.strength` pour orienter la description
  - [x] T3.2 Templates par `change_type` :
    - `"emergence"` → "L'énergie monte et [domaine] devient prioritaire."
    - `"recomposition"` → "Le focus se déplace vers [domaine]."
    - `"attenuation"` → "La tension retombe et laisse place à l'intégration."
  - [x] T3.3 Fallback : `V3TurningPoint.summary` existant (tronqué à 80 chars)

- [x] T4 — Construire `do` et `avoid` (AC: 6)
  - [x] T4.1 Créer `DO_AVOID_CATALOG: dict[(change_type, domain), tuple[str, str]]` dans `public_label_catalog.py`
  - [x] T4.2 Exemples :
    - `("emergence", "pro_ambition")` → do="Avancez, décidez, lancez", avoid="Reporter, attendre"
    - `("recomposition", "relations_echanges")` → do="Écouter, dialoguer", avoid="Imposer, forcer"
    - `("attenuation", any)` → do="Clôturer, ranger, ralentir", avoid="Forcer une décision"
  - [x] T4.3 Fallback générique si pas de correspondance exacte

- [x] T5 — Mapper `affected_domains` (AC: 7)
  - [x] T5.1 `V3TurningPoint.categories_impacted` contient des codes internes
  - [x] T5.2 Appeler `map_internal_to_public()` sur chaque code
  - [x] T5.3 Déduplique + garde max 3 domaines publics

- [x] T6 — Formatter `time` (AC: 2)
  - [x] T6.1 `V3TurningPoint.local_time.strftime("%H:%M")`

- [x] T7 — Intégrer dans `assemble()` et DTO (AC: 9)
  - [x] T7.1 Appeler `PublicTurningPointPolicy.build()` dans `assemble()`
  - [x] T7.2 Ajouter `turning_point: dict | None` dans le dict de retour
  - [x] T7.3 Conserver `turning_points` (liste) inchangé
  - [x] T7.4 Créer `DailyPredictionTurningPointPublic(BaseModel)` dans `predictions.py`
  - [x] T7.5 Ajouter `turning_point: DailyPredictionTurningPointPublic | None = None` dans `DailyPredictionResponse`

- [x] T8 — Tests (AC: 10)
  - [x] T8.1 Test : turning point avec `severity=0.2` → retourne `None`
  - [x] T8.2 Test : turning point with `severity=0.4, confidence=0.6` → retourne objet
  - [x] T8.3 Test : `affected_domains` contient des clefs publiques (pas internes)
  - [x] T8.4 Test : `affected_domains` max 3 items
  - [x] T8.5 Test : `title` non vide pour chaque combinaison change_type
  - [x] T8.6 Test : `turning_points` (liste) toujours présent dans le payload

## Dev Notes

### Seuils de sélection (AC: 8)
- `severity ≥ 0.3` : évite les micro-pivots
- `confidence ≥ 0.5` : évite les détections incertaines
- Ces seuils sont cohérents avec `TurningPointDetector` (`MIN_V3_CONFIDENCE = 0.5`)

### V3TurningPoint — champs disponibles (Story 43.1 + 44.1)
```python
change_type: str          # emergence/recomposition/attenuation
categories_impacted: list[str]  # codes internes
previous_categories: list[str]
next_categories: list[str]
primary_driver: V3PrimaryDriver | None
movement: V3Movement | None    # strength, direction, deltas
category_deltas: list[V3CategoryDelta]
severity: float           # [0-1]
confidence: float         # [0-1]
local_time: datetime
```
Source: `backend/app/prediction/schemas.py`

### Différence avec best_window (Story 60.6)
- `turning_point` = ce qui CHANGE dans la journée (narrative d'un avant/après)
- `best_window` = le meilleur MOMENT pour agir (opportunité temporelle)
- Un turning point peut coïncider avec une best_window mais ils restent deux objets distincts

### existing turning_points vs nouveau turning_point
- `turning_points` (liste) → inchangé, contient tous les turning points détectés avec toutes données techniques
- `turning_point` (singulier) → nouveau, sélection narrative du plus significatif

### Project Structure Notes
- Modification: `backend/app/prediction/public_projection.py` (nouvelle `PublicTurningPointPolicy`)
- Modification: `backend/app/prediction/public_label_catalog.py` (DO_AVOID_CATALOG)
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Dépend de: Story 60.1 (map_internal_to_public), Story 43.1 (V3TurningPoint enrichi)

### References
- [Source: backend/app/prediction/turning_point_detector.py#V3TurningPoint] — structure turning point
- [Source: backend/app/prediction/schemas.py#V3TurningPoint,V3Movement] — champs disponibles
- [Source: backend/app/prediction/public_projection.py#PublicTurningPointPolicy] — politique actuelle
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/prediction/public_label_catalog.py` (MOD)
- `backend/app/prediction/public_projection.py` (MOD)
- `backend/app/api/v1/routers/predictions.py` (MOD)
- `backend/tests/unit/prediction/test_public_main_turning_point.py` (NEW)
