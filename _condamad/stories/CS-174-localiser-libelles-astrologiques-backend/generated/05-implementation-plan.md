# Implementation Plan - CS-174

1. Ajouter `AstrologyTranslationResolver` et `AstrologyLabels` sous `services/reference_data`.
2. Brancher `build_chart_json`, le catalogue d'evidence et `NatalInterpretationService` sur les libelles resolus.
3. Brancher les helpers natals LLM et `AstroContextBuilder` sur `AstrologyLabels`.
4. Supprimer les exports `SIGN_NAMES_FR` et la liste locale `SIGNS`.
5. Ajouter les tests resolver, consommateurs et guardrails.
6. Executer format, lint, tests et scans requis.
