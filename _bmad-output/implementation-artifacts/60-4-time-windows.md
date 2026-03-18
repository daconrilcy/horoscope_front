# Story 60.4 : Refondre la projection des fenêtres temporelles

Status: review

## Story

En tant qu'utilisateur,
je veux voir des cartes horaires qui expriment chacune un régime temporel distinct et une action implicite,
afin de ne plus voir quatre cartes répétant "équilibré" et de comprendre comment agir à chaque moment de ma journée.

## Acceptance Criteria

1. Le payload expose `time_windows: list[TimeWindowPublic]` — chaque item contient : `time_range: str`, `label: str`, `regime: str`, `top_domains: list[str]` (max 2 clefs publiques), `action_hint: str`.
2. `regime` est une valeur parmi : `récupération`, `mise_en_route`, `progression`, `fluidité`, `prudence`, `pivot`, `recentrage`, `retombée`.
3. `label` est un libellé court non technique distinct pour chaque fenêtre (interdit : "équilibré" seul).
4. `action_hint` est une courte phrase d'action (max 8 mots, ex: "Avancez sur vos priorités", "Évitez les décisions engageantes").
5. Les 4 fenêtres de la journée (matin, après-midi, soirée, nuit) doivent être sémantiquement distinctes.
6. Le `regime` dérive directement de l'`orientation` V3 du bloc temporel : `rising → progression`, `falling → retombée`, `volatile → prudence`, `stable → fluidité` ; et si le bloc contient un turning point → `pivot`.
7. `top_domains` contient les clefs publiques (60.1) des domaines dominants de la fenêtre.
8. Le champ `timeline` existant est conservé (rétrocompat).
9. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [x] T1 — Créer `PublicTimeWindowPolicy` dans `public_projection.py` (AC: 1, 6)
  - [x] T1.1 Lire entièrement `backend/app/prediction/decision_window_builder.py` (méthode `build_v3()`, classe `DecisionWindow`)
  - [x] T1.2 Lire `backend/app/prediction/schemas.py` — `V3TimeBlock.orientation`, `V3TimeBlock.dominant_themes`
  - [x] T1.3 Créer classe `PublicTimeWindowPolicy` avec méthode `build(time_blocks: list[V3TimeBlock], turning_points, domain_mapping) -> list[dict]`
  - [x] T1.4 Mapper `orientation` → `regime` :
    ```python
    ORIENTATION_TO_REGIME = {
        "rising": "progression",
        "falling": "retombée",
        "volatile": "prudence",
        "stable": "fluidité",
    }
    # Si bloc contient turning point → override vers "pivot"
    ```
  - [x] T1.5 Enrichir avec `recentrage` (fin de journée + tone neutre/négatif) et `récupération` (nuit) via heure du bloc

- [x] T2 — Construire les labels dynamiques (AC: 3, 5)
  - [x] T2.1 Créer `REGIME_LABELS: dict[str, list[str]]` dans `public_label_catalog.py` (pool de labels par régime)
  - [x] T2.2 Exemples :
    - `progression` → ["Moment porteur", "Cap sur l'action", "Élan favorable"]
    - `fluidité` → ["Rythme fluide", "Douceur active", "Progression régulière"]
    - `prudence` → ["Fenêtre sensible", "Ralentir le rythme", "Gérer avec soin"]
    - `pivot` → ["Virage de la journée", "Moment charnière", "Tournant"]
    - `récupération` → ["Phase de repos", "Recharge tranquille"]
    - `retombée` → ["Retour au calme", "L'élan s'apaise"]
    - `mise_en_route` → ["Démarrage progressif", "Mise en mouvement"]
    - `recentrage` → ["Temps de bilan", "Ralenti créatif"]
  - [x] T2.3 Choisir le label en fonction de `top_domains` dominant (si pro_ambition → label orienté action, etc.)

- [x] T3 — Construire `action_hint` (AC: 4)
  - [x] T3.1 Créer `ACTION_HINTS: dict[str, str]` par régime (hint générique)
  - [x] T3.2 Exemples :
    - `progression` → "Avancez sur vos priorités"
    - `fluidité` → "Maintenez le cap"
    - `prudence` → "Évitez les décisions engageantes"
    - `pivot` → "Observez avant d'agir"
    - `recentrage` → "Faites le point"
    - `retombée` → "Laissez poser"
    - `récupération` → "Reposez-vous"
    - `mise_en_route` → "Lancez doucement"

- [x] T4 — Mapper `top_domains` vers clefs publiques (AC: 7)
  - [x] T4.1 `V3TimeBlock.dominant_themes` contient des codes internes
  - [x] T4.2 Appeler `map_internal_to_public()` (Story 60.1) sur chaque code
  - [x] T4.3 Déduplication (plusieurs internes → même public)
  - [x] T4.4 Garder max 2 domaines publics par fenêtre

- [x] T5 — Formatter `time_range` (AC: 1)
  - [x] T5.1 Formatter `start_local` → `end_local` en `"HH:MM–HH:MM"` (locale française, format 24h)
  - [x] T5.2 Si bloc couvre minuit → `"23:00–01:00"` (ne pas casser)

- [x] T6 — Intégrer dans `assemble()` et DTO (AC: 8)
  - [x] T6.1 Appeler `PublicTimeWindowPolicy.build()` dans `PublicPredictionAssembler.assemble()`
  - [x] T6.2 Ajouter `time_windows: list[...]` dans le dict de retour
  - [x] T6.3 Conserver `timeline` existant (rétrocompat)
  - [x] T6.4 Créer `DailyPredictionTimeWindow(BaseModel)` dans `predictions.py`
  - [x] T6.5 Ajouter `time_windows: list[DailyPredictionTimeWindow] | None = None` dans `DailyPredictionResponse`

- [x] T7 — Tests (AC: 9)
  - [x] T7.1 Test : orientation `rising` → regime `"progression"`
  - [x] T7.2 Test : bloc avec turning_point → regime `"pivot"` (override)
  - [x] T7.3 Test : 4 fenêtres → 4 régimes différents (pas de doublon)
  - [x] T7.4 Test : `top_domains` ≤ 2 items
  - [x] T7.5 Test : `action_hint` non vide pour chaque régime

## Dev Notes

### Problème actuel
`PublicTimelinePolicy` actuelle génère des blocs `timeline` avec `summary` libre. Le `tone_code` (positive/negative/mixed/neutral) est plat et peu distinctif. Résultat côté front : 4 cartes quasi identiques affichant "Nuit équilibrée", "Matin équilibré", etc.

### V3TimeBlock — champs disponibles
```python
@dataclass(frozen=True)
class V3TimeBlock:
    block_index: int
    start_local, end_local: datetime
    orientation: str  # "rising"/"falling"/"stable"/"volatile"
    intensity: float  # [0-20]
    confidence: float  # [0-1]
    dominant_themes: list[str]  # codes internes
    summary: str
```
Source: `backend/app/prediction/schemas.py`

### Détection des nuits / heures spéciales
- Bloc commençant entre 00:00–05:59 → `récupération` (override sauf pivot)
- Bloc commençant entre 06:00–09:59 → `mise_en_route` possible (si orientation stable)
- Bloc finissant entre 21:00–23:59 → `recentrage` possible (si orientation falling/stable)

### Interaction avec turning points
Un bloc peut contenir un turning point si `V3TurningPoint.local_time` est dans la plage `[start_local, end_local]`. Dans ce cas, `regime = "pivot"` override tout autre régime.

### DecisionWindowBuilder.build_v3()
Crée déjà des `DecisionWindow` avec `window_type` (favorable/prudence/pivot). La nouvelle story crée une projection _narrative_ sur les mêmes blocs, avec plus de sémantique. Les deux coexistent.

### Project Structure Notes
- Modification: `backend/app/prediction/public_projection.py` (nouvelle `PublicTimeWindowPolicy`)
- Modification ou création: `backend/app/prediction/public_label_catalog.py`
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Dépend de: Story 60.1 (map_internal_to_public)

### References
- [Source: backend/app/prediction/decision_window_builder.py#build_v3] — logique V3 windows
- [Source: backend/app/prediction/schemas.py#V3TimeBlock] — structure blocs temporels
- [Source: backend/app/prediction/public_projection.py#PublicTimelinePolicy] — politique actuelle
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
- `backend/tests/unit/prediction/test_public_time_window.py` (NEW)
