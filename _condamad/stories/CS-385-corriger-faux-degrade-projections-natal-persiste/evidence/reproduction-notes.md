# Reproduction CS-385 — faux degrade projections natales

## Contexte utilisateur

- Email: `daconrilcy@hotmail.com`
- Plan: `basic`
- Symptome UI: « Lecture partielle : des données de naissance manquent. »

## Donnees observees (2026-05-29)

### Profil de naissance

- `birth_date`: `1973-04-24`
- `birth_time`: `11:00`
- `birth_place_resolved_id`: `1`
- `birth_timezone`: `Europe/Paris`
- `detect_degraded_natal_mode`: `None`

### Theme natal persiste

- `chart_id`: `2a5c914a-6922-4be1-bca1-55561bd79b4d`
- `chart_objects`: `0`
- `planet_positions`: `10`
- `houses`: `12`
- `prepared_input.birth_time_local`: `11:00`

### Pipeline structured_facts / projections

```json
{
  "missing_data": {
    "chart_id": "2a5c914a-6922-4be1-bca1-55561bd79b4d",
    "sign_balances": "available",
    "empty_collections": [
      "advanced_condition_facts",
      "fixed_star_contacts",
      "houses",
      "positions"
    ]
  },
  "structural_facts_houses_count": 0,
  "beginner_summary_state": "degraded",
  "client_interpretation_state": "degraded"
}
```

## Cause racine

1. `NatalResult.chart_objects` est un champ interne exclu du JSON persiste.
2. Au reload DB, `chart_objects` est vide.
3. `ChartInterpretationInputBuilder` ne lit que `chart_objects`.
4. `structured_facts_v1` expose des collections vides.
5. `_has_missing_birth_time()` infere `no_time` via `empty_collections=["houses"]`.
6. Les builders B2C retournent `state=degraded`.
7. Le frontend affiche le bandeau « Lecture partielle ».

## Correction attendue

Rehydrater les objets interpretatifs depuis les collections historiques persistees
(`planet_positions`, `houses`, etc.) via le builder canonique, puis baser la
detection `no_time` sur une precision explicite de naissance quand disponible.
