# No Legacy / DRY Guardrails

## Canonical Responsibility

- Selection aspectable: `AspectChartObjectSelector`.
- Projection aspect body: `AspectBodyProjector`.
- Calcul geometrique: `calculate_major_aspects`.
- Construction des objets du theme: `build_chart_object_runtime_data`.

## Forbidden for CS-218

- Builder specialise par famille d'objet.
- Branche metier `object_type` dans les calculateurs.
- Source active parallele depuis `planet_positions`, `astral_points`, `angles`
  ou `fixed_stars` dans le moteur d'aspects.
- Fallback silencieux quand un objet aspectable n'a pas de longitude.
- Exception allowlist ou compatibilite transitoire.

## Guard Evidence Required

- Guard AST `test_chart_object_runtime_architecture.py`.
- Scans `RG-145`.
- Classification des hits:
  - `calculate_planet_positions` dans `calculators/natal.py` et `__init__.py`:
    hors moteur d'aspects, fonction de calcul natal pur existante.
  - noms de builders interdits dans `test_chart_object_runtime_architecture.py`:
    constantes de garde attendues.
  - `build_aspect_body_from_position` dans `aspects.py`: helper historique
    conserve hors flux natal CS-218, non appele par `natal_calculation.py`.

## Review Questions

- Le flux natal peut-il encore construire `aspect_positions` depuis
  `positions_raw` ou `points_raw`?
- Un objet aspectable invalide peut-il etre ignore silencieusement?
- Un nouveau calculateur branche-t-il par `object_type`?
