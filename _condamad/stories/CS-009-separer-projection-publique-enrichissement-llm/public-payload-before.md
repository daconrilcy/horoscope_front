# Public Payload Before

Runtime source: ancien `backend/app/prediction/public_projection.py` charge depuis `git show HEAD:backend/app/prediction/public_projection.py`, execute sur le snapshot deterministe de `test_public_projection.py`.

Resultat de comparaison:

```json
{
  "same": true,
  "keys": [
    "meta",
    "summary",
    "day_climate",
    "daily_synthesis",
    "astro_events_intro",
    "daily_advice",
    "has_llm_narrative",
    "best_window",
    "time_windows",
    "turning_point",
    "astro_foundation",
    "astro_daily_events",
    "categories",
    "categories_internal",
    "domain_ranking",
    "timeline",
    "turning_points",
    "decision_windows",
    "micro_trends"
  ],
  "time_window_labels": [
    "Phase de repos",
    "Virage de la journée",
    "Rythme fluide",
    "Temps de bilan"
  ]
}
```

Invariant: la forme publique V4 est identique sur ce cas sans generation LLM.
