# Story 60.7 : Ajouter la section "Fondements astrologiques"

Status: review

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

- [x] T1 — Créer `PublicAstroFoundationPolicy` dans `public_projection.py` (AC: 1)
  - [x] T1.1 Créer classe `PublicAstroFoundationPolicy` avec méthode `build(engine_output, domain_mapping) -> dict | None`
  - [x] T1.2 Retourner `None` si `engine_output` ne contient pas d'événements astro (cas dégradé)

- [x] T2 — Extraire `key_movements` (AC: 3, 7)
  - [x] T2.1 Lire `backend/app/prediction/schemas.py` — `AstroEvent` (ou équivalent) : `body`, `event_type`, `target`, `priority`, `orb_deg`
  - [x] T2.2 Identifier la source des événements dans `engine_output` (probablement `V3EvidencePack.metadata` ou `engine_output.events_by_step`)
  - [x] T2.3 Sélectionner les 5 événements à plus haute `priority` (seuil minimum: priority ≥ 50)
  - [x] T2.4 Créer `EFFECT_LABELS: dict[str, str]` — mapping `event_type` → label lisible :
    - `"transit_to_natal"` → "Transit sur point natal"
    - `"lunar_sign_change"` → "Lune en [signe]"
    - `"exact_aspect"` → "Aspect exact"
    - `"station_direct"` → "Planète repart directe"
    - `"station_retrograde"` → "Planète entre en rétrograde"
  - [x] T2.5 Traduire `body` en nom français (soleil, lune, mercure, vénus, mars, jupiter, saturne, uranus, neptune, pluton)

- [x] T3 — Extraire `activated_houses` (AC: 4)
  - [x] T3.1 Identifier depuis quel objet récupérer les maisons activées — probablement `V3EvidencePack.v3_natal_structural` ou `domain_router._build_house_index()`
  - [x] T3.2 Créer `HOUSE_SIGNIFICATIONS: dict[int, dict]` pour les 12 maisons
  - [x] T3.3 Sélectionner max 3 maisons les plus activées (weight ≥ threshold)

- [x] T4 — Extraire `dominant_aspects` (AC: 5, 6)
  - [x] T4.1 Identifier les aspects les plus actifs depuis `engine_output` (chercher dans `AstroEvent` avec `event_type == "aspect"`)
  - [x] T4.2 Créer `ASPECT_TONALITY: dict[str, str]`
  - [x] T4.3 Créer `ASPECT_EFFECT_LABELS: dict[str, str]` (description courte par type)
  - [x] T4.4 Limiter à 4 aspects maximum

- [x] T5 — Construire `headline` et `interpretation_bridge` (AC: 2, 8, 9)
  - [x] T5.1 `headline` = synthèse de `day_climate.label` + premier key_movement
  - [x] T5.2 `interpretation_bridge` = connexion entre faits astro et conclusions page

- [x] T6 — Vérifier la cohérence (AC: 8)
  - [x] T6.1 Si `day_climate.tone == "negative"` et `astro_foundation` présent → s'assurer que `interpretation_bridge` ne dit pas "tout est positif"
  - [x] T6.2 Log warning si incohérence détectée

- [x] T7 — Intégrer dans `assemble()` et DTO (AC: 1)
  - [x] T7.1 Appeler `PublicAstroFoundationPolicy.build()` dans `assemble()`
  - [x] T7.2 Créer DTOs Pydantic dans `predictions.py` : `DailyPredictionKeyMovement`, `DailyPredictionActivatedHouse`, `DailyPredictionDominantAspect`, `DailyPredictionAstroFoundation`
  - [x] T7.3 Ajouter `astro_foundation: DailyPredictionAstroFoundation | None = None` dans `DailyPredictionResponse`

- [x] T8 — Tests (AC: 10)
  - [x] T8.1 Test : `key_movements` max 5 items
  - [x] T8.2 Test : aspect `trine` → tonality `"fluidité"`
  - [x] T8.3 Test : aspect `square` → tonality `"ajustement"`
  - [x] T8.4 Test : `astro_foundation = None` si pas d'événements (gracieux)
  - [x] T8.5 Test : `activated_houses` max 3 items, clefs 1-12

## Dev Notes
...
### File List

- `backend/app/prediction/public_astro_vocabulary.py` (NEW)
- `backend/app/prediction/public_projection.py` (MOD)
- `backend/app/api/v1/routers/predictions.py` (MOD)
- `backend/tests/unit/prediction/test_public_astro_foundation.py` (NEW)
