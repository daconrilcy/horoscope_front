# CS-441 - Corriger La Suppression Du Runtime Generate Natal Legacy

<!-- Commentaire global: ce brief cadre le rattrapage CS-436 apres constat que le runtime legacy reste present. -->

## Resume

Rattraper l'echec de suppression du runtime generatif natal legacy. La review
d'implementation a prouve que `AIEngineAdapter.generate_natal_interpretation`
existe encore dans `backend/app/domain/llm/runtime/adapter.py` et que
`NatalInterpretationService` l'appelle encore. Cette story doit supprimer ce
chemin executable, pas seulement le classer ou le proteger par un guard.

Cette story est une correction de livraison de CS-436. Elle ne remplace pas le
runtime `theme_natal`; elle retire le dernier point d'entree provider-capable
qui permettrait de contourner les contrats produit et generation modernes.

## Constats De Depart

- `_condamad/stories/story-status.md` marque `CS-436` `ready-to-dev`.
- `backend/app/domain/llm/runtime/adapter.py` contient encore
  `async def generate_natal_interpretation`.
- `backend/app/services/llm_generation/natal/interpretation_service.py` appelle
  encore `AIEngineAdapter.generate_natal_interpretation`.
- Des tests positifs mockent encore `generate_natal_interpretation`.

## Perimetre Inclus

1. Supprimer physiquement `AIEngineAdapter.generate_natal_interpretation` de
   `backend/app/domain/llm/runtime/adapter.py`.
2. Supprimer tout appel applicatif a `AIEngineAdapter.generate_natal_interpretation`.
3. Retirer du runtime natal les branches qui construisent une generation via:
   - `NatalExecutionInput`;
   - `use_case_key=natal_interpretation`;
   - `variant_code` comme selecteur de prompt;
   - `level` comme selecteur de runtime provider.
4. Remplacer les tests positifs legacy par:
   - tests de rejet avant provider;
   - tests de lecture readonly historique sans provider;
   - tests de runtime contractuel `theme_natal`.
5. Mettre a jour les guards CS-440 pour que le scan
   `generate_natal_interpretation` soit zero-hit dans `backend/app`.
6. Produire une preuve before/after des scans bloquants.

## Hors Perimetre

- Supprimer les catalogues, seeds ou scripts legacy: traite par CS-442.
- Supprimer l'API publique historique: traite par CS-443.
- Changer les calculs astrologiques.
- Modifier `_condamad/run-state.json`.
- Conserver un stub, alias, wrapper ou garde runtime nomme
  `generate_natal_interpretation`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`
- `backend/app/domain/theme_natal/generation_contracts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - aucune facade legacy de remplacement.
  - `RG-005` - ne pas deplacer le runtime retire dans une route.
  - `RG-006` - conserver la frontiere API/service/domain.
  - `RG-018` - pas de fallback prompt natal supporte.
  - `RG-149` - cartographie prompt-generation a mettre a jour si le flux disparait.
  - `RG-150` - les rejets ne deviennent pas lectures publiques.
  - `RG-164` - Basic reste sous owner moderne.
  - `RG-167` - Basic complete utilise le runtime Basic moderne.
  - `RG-173` - generation publique par product+LLM contracts.
  - `RG-174` - zero public/runtime hit legacy.
- Required regression evidence:
  - Scan zero-hit `generate_natal_interpretation` dans `backend/app`.
  - Tests theme natal modernes toujours verts.
  - Tests readonly historiques prouvant aucune invocation provider.
- Allowed differences:
  - Suppression de tests/mocks positifs legacy.
  - Suppression de code mort rendu inaccessible par les contrats `theme_natal`.

## Criteres D'acceptation

1. `rg -n "generate_natal_interpretation" backend/app` retourne aucun hit.
2. Aucun test positif ne mocke `AIEngineAdapter.generate_natal_interpretation`.
3. `NatalInterpretationService` ne contient plus d'appel provider legacy.
4. Toute tentative de generation via ancien service echoue avant construction
   d'une requete provider ou n'existe plus comme API interne.
5. Les lectures historiques readonly restent lisibles sans provider.
6. Le runtime Basic contractuel continue de produire/persister via slots publics.
7. CS-440 `CR-4` est resolu pour la partie runtime/adaptateur.
8. Les preuves before/after sont ajoutees dans la story.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/theme_natal tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_public_reads.py --tb=short
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short
```

Scans:

```powershell
rg -n "generate_natal_interpretation" backend/app
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation|patch\.object\(AIEngineAdapter, `"generate_natal_interpretation`"" backend/tests backend/app/tests
rg -n "NatalExecutionInput\(|use_case_key=.*natal_interpretation" backend/app/services/llm_generation/natal backend/app/domain/llm/runtime
```

## Dependances

- Peut etre implementee avant CS-442 et CS-443.
- Doit etre terminee avant la cloture CS-444.

## Risques

Le risque principal est de casser une lecture historique en supprimant un helper
qui etait aussi utilise pour projeter du readonly. La correction doit separer
strictement lecture readonly et generation provider avant suppression.
