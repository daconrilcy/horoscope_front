# Frontend Before

- `/natal` rendait l'interpretation natale existante via `useNatalInterpretation`.
- Aucun wrapper frontend dedie ne consommait `POST /v1/astrology/projections`.
- Les disclaimers etaient deja rendus depuis `frontend/src/i18n/natalChart.ts`, pas depuis le payload d'interpretation.
- Les tests existants couvraient l'interpretation natale, mais pas les projections `beginner_summary_v1` et `client_interpretation_projection_v1`.
