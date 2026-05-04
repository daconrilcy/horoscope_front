# Astro Foundation Before

## Baseline

Avant CS-010, `PublicAstroFoundationPolicy` resolvait les evenements ainsi:

- `evidence.metadata["astro_events"]` si present;
- sinon `core.events` si `engine_output` etait fourni;
- pas de lecture de `core.detected_events`.

Pour les aspects dominants, la policy filtrait uniquement:

```python
e.event_type == "aspect"
```

## Effet observe

- Un moteur exposant seulement `core.detected_events` pouvait produire `astro_foundation = None`.
- Les evenements `aspect_exact_to_angle`, `aspect_exact_to_luminary` et `aspect_exact_to_personal` pouvaient apparaitre dans les mouvements majeurs, mais pas dans `dominant_aspects`.

## Schema public attendu

Le schema public ne devait pas changer. La correction attendue porte uniquement sur le remplissage des champs existants de `astro_foundation`.
