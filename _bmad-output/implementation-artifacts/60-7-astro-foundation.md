# Story 60.7 : Ajouter la section "Fondements astrologiques"

Status: ready-for-dev

## Story

En tant qu'utilisateur curieux de comprendre les mécanismes,
je veux voir une section qui explique la mécanique astrologique qui soutient l'interprétation,
afin de comprendre pourquoi le moteur dit ce qu'il dit, sans avoir besoin d'être astrologue.

## Acceptance Criteria

1. Le payload expose `astro_foundation: dict | None` — présent si des données astrologiques sont disponibles.
2. `astro_foundation` contient :
   - `headline: str` — une phrase synthétique reliant astrologie et lecture
   - `key_movements: list[dict]` — 3 à 5 événements clés (transit, aspect exact, changement signe lunaire)
   - `activated_houses: list[dict]` — maisons activées avec signification métier accessible
   - `dominant_aspects: list[dict]` — 2 à 4 aspects avec traduction de tonalité
   - `interpretation_bridge: str` — texte court reliant les faits astro aux conclusions de la page
3. Chaque `key_movement` contient : `planet: str`, `event_type: str`, `target: str | None`, `orb_deg: float | None`, `effect_label: str`.
4. Chaque `activated_house` contient : `house_number: int`, `house_label: str`, `domain_label: str` (signification publique).
5. Chaque `dominant_aspect` contient : `aspect_type: str`, `planet_a: str`, `planet_b: str | None`, `tonality: str`, `effect_label: str`.
6. `tonality` dans `dominant_aspect` suit les règles : trigone/sextile → "fluidité", carré/opposition → "ajustement", conjonction → "intensification".
7. `key_movements` est limité à 5 items maximum (sélection des plus significatifs par priorité).
8. `astro_foundation` ne contredit jamais le `day_climate.tone` et les domaines affichés.
9. Toutes les formulations sont lisibles par un non-expert (pas de termes techniques sans traduction).
10. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Créer `PublicAstroFoundationPolicy` dans `public_projection.py` (AC: 1)
  - [ ] T1.1 Créer classe `PublicAstroFoundationPolicy` avec méthode `build(engine_output, domain_mapping) -> dict | None`
  - [ ] T1.2 Retourner `None` si `engine_output` ne contient pas d'événements astro (cas dégradé)

- [ ] T2 — Extraire `key_movements` (AC: 3, 7)
  - [ ] T2.1 Lire `backend/app/prediction/schemas.py` — `AstroEvent` (ou équivalent) : `body`, `event_type`, `target`, `priority`, `orb_deg`
  - [ ] T2.2 Identifier la source des événements dans `engine_output` (probablement `V3EvidencePack.metadata` ou `engine_output.events_by_step`)
  - [ ] T2.3 Sélectionner les 5 événements à plus haute `priority` (seuil minimum: priority ≥ 50)
  - [ ] T2.4 Créer `EFFECT_LABELS: dict[str, str]` — mapping `event_type` → label lisible :
    - `"transit_to_natal"` → "Transit sur point natal"
    - `"lunar_sign_change"` → "Lune en [signe]"
    - `"exact_aspect"` → "Aspect exact"
    - `"station_direct"` → "Planète repart directe"
    - `"station_retrograde"` → "Planète entre en rétrograde"
  - [ ] T2.5 Traduire `body` en nom français (soleil, lune, mercure, vénus, mars, jupiter, saturne, uranus, neptune, pluton)

- [ ] T3 — Extraire `activated_houses` (AC: 4)
  - [ ] T3.1 Identifier depuis quel objet récupérer les maisons activées — probablement `V3EvidencePack.v3_natal_structural` ou `domain_router._build_house_index()`
  - [ ] T3.2 Créer `HOUSE_SIGNIFICATIONS: dict[int, dict]` pour les 12 maisons :
    ```python
    {
      1: {"label": "Maison I", "domain": "Identité et présence"},
      2: {"label": "Maison II", "domain": "Ressources et valeurs"},
      3: {"label": "Maison III", "domain": "Communication et mobilité"},
      4: {"label": "Maison IV", "domain": "Foyer et ancrage"},
      5: {"label": "Maison V", "domain": "Créativité et plaisirs"},
      6: {"label": "Maison VI", "domain": "Travail quotidien et santé"},
      7: {"label": "Maison VII", "domain": "Relations et associations"},
      8: {"label": "Maison VIII", "domain": "Transformations et profondeur"},
      9: {"label": "Maison IX", "domain": "Philosophie et horizons"},
      10: {"label": "Maison X", "domain": "Ambition et rôle public"},
      11: {"label": "Maison XI", "domain": "Collectif et réseaux"},
      12: {"label": "Maison XII", "domain": "Intériorité et ressources cachées"},
    }
    ```
  - [ ] T3.3 Sélectionner max 3 maisons les plus activées (weight ≥ threshold)

- [ ] T4 — Extraire `dominant_aspects` (AC: 5, 6)
  - [ ] T4.1 Identifier les aspects les plus actifs depuis `engine_output` (chercher dans `AstroEvent` avec `event_type == "aspect"`)
  - [ ] T4.2 Créer `ASPECT_TONALITY: dict[str, str]` :
    - `trine`, `sextile` → `"fluidité"`
    - `square`, `opposition` → `"ajustement"`
    - `conjunction` → `"intensification"`
    - `quincunx` → `"adaptation"`
  - [ ] T4.3 Créer `ASPECT_EFFECT_LABELS: dict[str, str]` (description courte par type)
  - [ ] T4.4 Limiter à 4 aspects maximum

- [ ] T5 — Construire `headline` et `interpretation_bridge` (AC: 2, 8, 9)
  - [ ] T5.1 `headline` = synthèse de `day_climate.label` + premier key_movement
    - Ex: "Mercure en trigone facilite les échanges — journée de progression"
    - Fallback: "Le ciel du jour soutient [top_domain public]"
  - [ ] T5.2 `interpretation_bridge` = connexion entre faits astro et conclusions page
    - Ex: "Ces transits expliquent pourquoi le secteur Pro est particulièrement actif aujourd'hui."
    - Cohérence : si day_climate.tone == "positive" → bridge positif

- [ ] T6 — Vérifier la cohérence (AC: 8)
  - [ ] T6.1 Si `day_climate.tone == "negative"` et `astro_foundation` présent → s'assurer que `interpretation_bridge` ne dit pas "tout est positif"
  - [ ] T6.2 Log warning si incohérence détectée

- [ ] T7 — Intégrer dans `assemble()` et DTO (AC: 1)
  - [ ] T7.1 Appeler `PublicAstroFoundationPolicy.build()` dans `assemble()`
  - [ ] T7.2 Créer DTOs Pydantic dans `predictions.py` : `DailyPredictionKeyMovement`, `DailyPredictionActivatedHouse`, `DailyPredictionDominantAspect`, `DailyPredictionAstroFoundation`
  - [ ] T7.3 Ajouter `astro_foundation: DailyPredictionAstroFoundation | None = None` dans `DailyPredictionResponse`

- [ ] T8 — Tests (AC: 10)
  - [ ] T8.1 Test : `key_movements` max 5 items
  - [ ] T8.2 Test : aspect `trine` → tonality `"fluidité"`
  - [ ] T8.3 Test : aspect `square` → tonality `"ajustement"`
  - [ ] T8.4 Test : `astro_foundation = None` si pas d'événements (gracieux)
  - [ ] T8.5 Test : `activated_houses` max 3 items, clefs 1-12

## Dev Notes

### Source des données astrologiques
L'objet `engine_output` dans `assemble()` contient le résultat de `EngineOrchestrator`. Identifier dans `engine_orchestrator.py` comment accéder aux `AstroEvent` détectés (via `event_detector_factory`).

Structure probable d'un `AstroEvent` :
```python
body: str          # planète
event_type: str    # "transit_to_natal", "aspect", "lunar_sign_change"...
target: str | None # point natal ou autre planète
aspect: str | None # "trine", "square", etc.
orb_deg: float
priority: int      # [0-100], filtrer ≥ 50 pour key_movements
phase: str | None  # "applying"/"separating"
```

### Principe de sélectivité
Ne PAS exporter tous les transits (le moteur en calcule des dizaines). Critères de sélection :
1. `priority >= 50` pour key_movements
2. `orb_deg <= 3` pour les aspects dominants
3. Maximum 3 maisons activées (celles avec le plus fort poids dans domain_router)

### Maisons et domain_router
`domain_router._build_house_index()` produit `dict[house_number, dict[category_code, weight]]`. Les maisons avec les poids les plus élevés sur les domaines publics dominants sont les "activated_houses".

### Project Structure Notes
- Modification: `backend/app/prediction/public_projection.py` (nouvelle `PublicAstroFoundationPolicy`)
- Nouveau fichier ou extension: `backend/app/prediction/public_astro_vocabulary.py` (HOUSE_SIGNIFICATIONS, ASPECT_TONALITY, EFFECT_LABELS)
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveaux DTOs)
- Dépend de: Story 60.1 (domaines publics), Story 60.3 (day_climate.tone pour cohérence)

### References
- [Source: backend/app/prediction/engine_orchestrator.py] — structure engine_output
- [Source: backend/app/prediction/domain_router.py#_build_house_index] — maisons et poids
- [Source: backend/app/prediction/schemas.py#V3EvidencePack] — données disponibles
- [Source: backend/app/services/astro_context_builder.py] — AstroContextData (Epic 59.4, transits)
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
