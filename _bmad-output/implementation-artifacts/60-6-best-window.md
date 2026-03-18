# Story 60.6 : Exposer explicitement la meilleure fenêtre du jour

Status: ready-for-dev

## Story

En tant qu'utilisateur,
je veux voir la meilleure opportunité temporelle du jour mise en avant clairement avec une explication,
afin de savoir exactement quand agir sans parcourir toute la page.

## Acceptance Criteria

1. Le payload expose `best_window: dict | None` — `null` si aucune fenêtre favorable n'est détectée.
2. `best_window` contient : `time_range: str` (HH:MM–HH:MM), `label: str`, `why: str`, `recommended_actions: list[str]` (max 3 items).
3. `label` est un libellé court accrocheur (ex: "Votre meilleur créneau", "Fenêtre d'opportunité", "Pic du jour").
4. `why` est une phrase explicative courte (max 20 mots) justifiant pourquoi ce créneau est favorable.
5. `recommended_actions` sont 2–3 suggestions d'action courtes liées aux domaines dominants du créneau.
6. La `best_window` est déterminée depuis les `decision_windows` existantes en sélectionnant la fenêtre `window_type="favorable"` avec le `score` le plus élevé.
7. Si la meilleure fenêtre est aussi un turning point (`pivot`), le champ `is_pivot: bool = True` est ajouté.
8. `day_climate.best_window_ref` (Story 60.3) pointe vers le même créneau.
9. Le champ `summary.best_window` existant est conservé (rétrocompat).
10. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Créer `PublicBestWindowPolicy` dans `public_projection.py` (AC: 1, 6)
  - [ ] T1.1 Lire `backend/app/prediction/decision_window_builder.py` — `DecisionWindow` dataclass, méthode `build_v3()`
  - [ ] T1.2 Lire `backend/app/prediction/schemas.py` — `DecisionWindow.window_type`, `.score`, `.dominant_categories`, `.intensity`, `.confidence`
  - [ ] T1.3 Créer classe `PublicBestWindowPolicy` avec méthode `build(decision_windows: list[DecisionWindow], domain_mapping) -> dict | None`
  - [ ] T1.4 Sélection : filtrer `window_type="favorable"`, trier par `score` décroissant, prendre le premier
  - [ ] T1.5 Si vide → retourner `None`

- [ ] T2 — Construire `label` (AC: 3)
  - [ ] T2.1 Logique basée sur `intensity` du window :
    - Intensity ≥ 14 → "Pic du jour"
    - Intensity ∈ [10, 14) → "Votre meilleur créneau"
    - Intensity < 10 → "Fenêtre favorable"
  - [ ] T2.2 Fallback → "Moment favorable"

- [ ] T3 — Construire `why` (AC: 4)
  - [ ] T3.1 Templates basés sur domaine dominant + orientation :
    ```python
    WHY_TEMPLATES = {
        "pro_ambition": "Les conditions pro sont au maximum de leur dynamique.",
        "relations_echanges": "Les échanges sont fluides et réceptifs.",
        "energie_bienetre": "Votre vitalité est à son pic.",
        "argent_ressources": "Les décisions financières bénéficient d'un soutien fort.",
        "vie_personnelle": "L'énergie créative et personnelle est au sommet.",
    }
    # Fallback générique
    DEFAULT_WHY = "Les conditions astrologiques convergent favorablement."
    ```
  - [ ] T3.2 Domaine dominant = premier item de `dominant_categories` mappé vers clef publique

- [ ] T4 — Construire `recommended_actions` (AC: 5)
  - [ ] T4.1 Créer `WINDOW_ACTIONS: dict[str, list[str]]` par domaine public dans `public_label_catalog.py`
  - [ ] T4.2 Exemples :
    - `pro_ambition` → ["Prendre des décisions importantes", "Négocier ou conclure", "Avancer sur un projet bloqué"]
    - `relations_echanges` → ["Avoir une conversation difficile", "Proposer, inviter, connecter", "Résoudre un conflit"]
    - `energie_bienetre` → ["Faire du sport", "S'aérer, sortir", "Commencer une nouvelle habitude"]
    - `argent_ressources` → ["Signer, valider, investir", "Réviser un budget", "Contacter un prestataire"]
    - `vie_personnelle` → ["Lancer un projet créatif", "Passer du temps en famille", "Se faire plaisir"]
  - [ ] T4.3 Prendre les 3 premiers items pour le domaine dominant

- [ ] T5 — Détecter `is_pivot` (AC: 7)
  - [ ] T5.1 Vérifier si `window_type` de la meilleure fenêtre est aussi `"pivot"` ou si un turning point tombe dans la plage
  - [ ] T5.2 `is_pivot = True` uniquement si les deux sont vrais

- [ ] T6 — Cohérence avec `day_climate.best_window_ref` (AC: 8)
  - [ ] T6.1 `day_climate.best_window_ref` = formatter `start_local–end_local` de la best window
  - [ ] T6.2 Coordonner avec Story 60.3 pour réutiliser le même formattage

- [ ] T7 — Intégrer dans `assemble()` et DTO (AC: 9)
  - [ ] T7.1 Appeler `PublicBestWindowPolicy.build()` avant `PublicDayClimatePolicy` (pour que day_climate puisse référencer best_window_ref)
  - [ ] T7.2 Ajouter `best_window: dict | None` dans le dict de retour
  - [ ] T7.3 Conserver `summary.best_window` existant
  - [ ] T7.4 Créer `DailyPredictionBestWindow(BaseModel)` dans `predictions.py`
  - [ ] T7.5 Ajouter `best_window: DailyPredictionBestWindow | None = None` dans `DailyPredictionResponse`

- [ ] T8 — Tests (AC: 10)
  - [ ] T8.1 Test : aucune fenêtre favorable → retourne `None`
  - [ ] T8.2 Test : plusieurs fenêtres favorables → retourne celle avec le plus grand `score`
  - [ ] T8.3 Test : `recommended_actions` ≤ 3 items
  - [ ] T8.4 Test : `why` non vide pour chaque domaine public
  - [ ] T8.5 Test : `time_range` au format "HH:MM–HH:MM"
  - [ ] T8.6 Test : `summary.best_window` (existant) toujours présent dans `DailyPredictionSummary`

## Dev Notes

### DecisionWindow — champs disponibles
```python
@dataclass(frozen=True)
class DecisionWindow:
    start_local, end_local: datetime
    window_type: str      # "favorable"/"prudence"/"pivot"
    score: float
    confidence: float     # [0-1]
    dominant_categories: list[str]  # codes internes
    orientation: str | None   # V3: "rising"/"falling"/"stable"/"volatile"
    intensity: float | None   # V3: [0-20]
```
Source: `backend/app/prediction/schemas.py`

### Relation avec summary.best_window existant
`summary.best_window` actuel contient : `{"start": ..., "end": ..., "type": "favorable", "categories": [...]}`. C'est conservé. Le nouveau `best_window` est plus riche (label, why, recommended_actions).

### Ordre d'appel dans assemble()
```
1. PublicCategoryPolicy
2. PublicDecisionWindowPolicy (decision_windows existant)
3. PublicBestWindowPolicy  ← nouveau, consomme decision_windows
4. PublicTurningPointPolicy (turning_point)
5. PublicDayClimatePolicy  ← consomme best_window pour best_window_ref
6. PublicTimeWindowPolicy  (time_windows)
7. PublicDomainRankingPolicy (domain_ranking)
```

### Project Structure Notes
- Modification: `backend/app/prediction/public_projection.py` (nouvelle `PublicBestWindowPolicy`)
- Modification: `backend/app/prediction/public_label_catalog.py` (WINDOW_ACTIONS)
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Dépend de: Story 60.1 (map_internal_to_public), Story 60.3 (best_window_ref dans day_climate)

### References
- [Source: backend/app/prediction/decision_window_builder.py#build_v3] — logique V3 windows
- [Source: backend/app/prediction/schemas.py#DecisionWindow] — structure window
- [Source: backend/app/prediction/public_projection.py#PublicDecisionWindowPolicy] — politique actuelle
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
