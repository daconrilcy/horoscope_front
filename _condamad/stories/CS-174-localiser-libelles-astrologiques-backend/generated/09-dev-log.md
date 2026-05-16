# Dev Log - CS-174

## 2026-05-16

- Préflight: dépôt propre au départ (`git status --short` sans sortie).
- Capsule `generated/` créée car absente.
- Implémentation:
  - ajout de `AstrologyTranslationResolver` et `AstrologyLabels`;
  - enrichissement du chart JSON avec les champs de libellés localisés;
  - migration du catalogue d'évidence et des contextes LLM natals vers `AstrologyLabels`;
  - suppression de `SIGN_NAMES_FR` et de la liste locale `SIGNS` des surfaces ciblees;
  - ajout de tests resolver, consommateurs et guards anti-réintroduction.
- Validation ciblée sous venv:
  - `ruff check . --fix`, `ruff format .`, `ruff check .`;
  - `pytest -q app/tests/unit/test_astrology_translation_resolver.py app/tests/unit/test_chart_json_builder.py`;
  - `pytest -q app/tests/unit/test_natal_context_localization.py tests/unit/domain/astrology/test_zodiac.py`;
  - `pytest -q app/tests/unit/test_astrology_localization_guardrails.py`;
  - scans négatifs `SIGN_NAMES_FR` / imports resolver dans `app/domain/astrology`.
- Revue indépendante:
  - Finding accepté: import croisé entre tests corrigé via `app/tests/helpers/natal_result_factory.py`.
  - Finding accepté: `ChartResultService.persist_trace` résout maintenant `AstrologyLabels` via le resolver au lieu d'utiliser le fallback technique direct.
  - Finding accepté: guard anti-réintroduction élargi à `app/services/**` avec exception PDF exacte.
  - Finding accepté: test chat follow-up corrigé pour accepter l'argument `labels`; validation des services LLM modifiés ajoutée.
