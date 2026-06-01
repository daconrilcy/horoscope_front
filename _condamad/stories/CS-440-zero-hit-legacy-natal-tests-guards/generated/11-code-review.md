# Code Review CS-440

<!-- Commentaire global: cette revue d'implementation conserve les findings CS-440 et la decision de blocage. -->

## Verdict

BLOCKED

## Iterations

- Iteration 1: findings actionnables acceptes, correction appliquee.
- Iteration 2: review fraiche relancee apres correction, blocker restant confirme.

## Findings corriges

| ID | Severite | Finding | Correction | Preuve |
|---|---|---|---|---|
| CR-1 | High | Le guard CS-440 ne couvrait pas les tests et fixtures qui portent encore les anciens symboles. | Ajout de `test_legacy_natal_test_hits_are_explicitly_authorized` et d'un check de suppression des anciens noms de fixtures. | `pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py app/tests/unit/test_eval_harness_natal.py`. |
| CR-2 | Medium | Les fixtures d'evaluation portaient encore `natal_interpretation_short` et `natal_interpretation` comme noms actifs. | Renommage en `generic_structured_short` et `generic_structured_complete`; test harness mis a jour. | Scan `rg --files backend/app/tests/eval_fixtures` sans ancien nom. |

## Blocker restant

| ID | Severite | Finding | Preuve | Correction attendue |
|---|---|---|---|---|
| CR-3 | Blocker | CS-440 revendique une fermeture apres CS-436 a CS-439, mais CS-436, CS-437 et CS-438 sont encore `ready-to-dev`. | `_condamad/stories/story-status.md` lignes CS-436 a CS-438. | Implementer/fermer CS-436, CS-437 et CS-438 avant de clore CS-440. |
| CR-4 | Blocker | Des tests positifs Basic/free exercent encore le service/adaptateur legacy au lieu d'etre seulement extinction/rejet/readonly. | Scan `rg` sur `fake_generate_natal_interpretation`, `AIEngineAdapter.generate_natal_interpretation` et anciens tokens. | Supprimer ou rebasculer ces tests avec les suppressions fonctionnelles CS-436 a CS-438. |

## Validation

- PASS: `ruff format .` puis `ruff check .` dans `backend`.
- PASS: `pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short`.
- PASS: `pytest -q --long tests/unit/domain/theme_natal tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_public_reads.py --tb=short`.
- PASS: `pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx`.
- PASS: `pnpm --dir frontend lint`.
- PASS: runtime scans refresh controls, public `use_case_level`, and legacy fixture directories.

## Decision

Story non clean. Ne pas passer `_condamad/stories/story-status.md` a `done`.
