# CS-444 - Clore CS-440 Zero Hit Apres Corrections Legacy Natal

<!-- Commentaire global: ce brief cadre la cloture finale de CS-440 une fois les corrections CS-441 a CS-443 livrees. -->

## Resume

Clore CS-440 apres les corrections fonctionnelles. Cette story ne doit pas
supprimer elle-meme le runtime, les prompts ou l'API legacy: elle verifie que
CS-441, CS-442 et CS-443 ont ferme les blockers, puis remplace les allowlists
temporaires par des scans zero-hit stricts et met les preuves CS-440 a jour.

## Constats De Depart

- CS-440 est `ready-to-review`, pas `done`.
- `generated/11-code-review.md` de CS-440 est `BLOCKED`.
- `CR-3` bloque tant que CS-436/437/438, ou leurs corrections CS-441/442/443,
  ne sont pas livrees.
- `CR-4` bloque tant que des tests positifs utilisent encore
  `AIEngineAdapter.generate_natal_interpretation` ou les anciens use cases natals.

## Perimetre Inclus

1. Verifier que CS-441, CS-442 et CS-443 sont `done` avec review clean.
2. Rerun les scans CS-440 qui etaient `FAIL/BLOCKED`.
3. Supprimer ou reduire les allowlists CS-434/CS-435/CS-440 aux seules preuves
   `_condamad` et tests d'extinction.
4. Mettre a jour `legacy-natal-zero-hit-audit.md`.
5. Mettre a jour `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`
   pour retirer la formulation de fermeture partielle.
6. Mettre a jour `generated/10-final-evidence.md` et `generated/11-code-review.md`
   de CS-440 avec un verdict clean si les validations passent.
7. Verifier que `RG-174` reste exact et assez strict.
8. Produire un rapport final de fermeture CS-440.

## Hors Perimetre

- Implementer les suppressions fonctionnelles manquantes.
- Supprimer les rapports historiques d'analyse ou les briefs.
- Modifier le frontend hors corrections de tests/guards.
- Modifier `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`
- `_story_briefs/cs-442-corriger-suppression-sources-reintroduction-prompts-nataux-legacy.md`
- `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_condamad/stories/story-status.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de facade legacy.
  - `RG-018` - pas de fallback prompt natal supporte.
  - `RG-021` - fallbacks classes ou supprimes.
  - `RG-149` - cartographie prompt-generation exacte.
  - `RG-153`, `RG-154`, `RG-170` - DOM natal moderne conserve.
  - `RG-173` - public LLM generation via product+LLM contracts.
  - `RG-174` - zero public/runtime hit legacy.
- Required regression evidence:
  - Revue clean CS-440.
  - Scans zero-hit stricts.
  - Tests backend architecture/LLM/theme_natal.
  - Tests frontend natal.
- Allowed differences:
  - Suppression des allowlists temporaires.
  - Renommage de tests pour expliciter leur role d'extinction.

## Criteres D'acceptation

1. CS-441, CS-442 et CS-443 sont `done` ou explicitement remplaces par des preuves
   equivalentes acceptees.
2. `rg -n "generate_natal_interpretation" backend/app` est zero-hit.
3. `rg -n "/v1/natal/interpretation|/v1/natal/interpretations" backend/app/api/v1/routers/public frontend/src`
   est zero-hit.
4. `rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src`
   est zero-hit, sauf si le hit est dans un test d'extinction hors runtime.
5. Aucun test positif ne mocke l'ancien runtime generation.
6. `generated/11-code-review.md` de CS-440 passe de `BLOCKED` a `CLEAN`.
7. `generated/10-final-evidence.md` de CS-440 marque AC2, AC3 et AC4 `PASS`.
8. `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` ne dit plus
   que CS-440 ne peut pas etre clos.
9. `story-status.md` marque CS-440 `done` seulement apres validations et review clean.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py --tb=short
python -B -m pytest -q tests/unit/domain/theme_natal tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_public_reads.py --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalPublicDomGuard.test.tsx natalInterpretation.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "generate_natal_interpretation" backend/app
rg -n "/v1/natal/interpretation|/v1/natal/interpretations" backend/app/api/v1/routers/public frontend/src
rg -n "natal_interpretation_short|natal_long_free|shouldRefreshShortAfterBasicUpgrade|forceRefresh" backend/app frontend/src
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation|patch\.object\(AIEngineAdapter, `"generate_natal_interpretation`"" backend/tests backend/app/tests
```

## Dependances

- CS-441.
- CS-442.
- CS-443.

## Risques

Le risque est de declarer CS-440 clean en ne durcissant que les guards. Cette story
doit refuser tout `PASS_WITH_LIMITATIONS`, allowlist runtime ou blocage reporte.
