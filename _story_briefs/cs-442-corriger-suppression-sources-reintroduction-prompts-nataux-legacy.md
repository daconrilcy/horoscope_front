# CS-442 - Corriger La Suppression Des Sources De Reintroduction Prompts Nataux Legacy

<!-- Commentaire global: ce brief cadre le rattrapage CS-437 apres constat de residus seeds/catalogues/admin. -->

## Resume

Rattraper l'echec de suppression des sources de reintroduction des anciens prompts
natals. La review a montre que `backend/app/services/llm_generation/admin_prompts.py`
propose encore `natal_long_free`, et que plusieurs tests/catalogues continuent a
porter `natal_interpretation_short` ou `natal_long_free` comme exemples nominaux.

Cette story corrige CS-437: aucun catalogue, seed, bootstrap, script ou helper
admin ne doit pouvoir recreer les anciens use cases natals comme runtime.

## Constats De Depart

- `_condamad/stories/story-status.md` marque `CS-437` `ready-to-dev`.
- `backend/app/services/llm_generation/admin_prompts.py` retourne encore
  `natal_long_free`.
- Des tests admin/catalogue utilisent encore `natal_interpretation_short` ou
  `natal_long_free` comme fixture positive.
- CS-440 reste bloque tant que ces sources sont encore nominales.

## Perimetre Inclus

1. Supprimer `natal_long_free` de `admin_prompts.py`.
2. Supprimer des catalogues, registries et bootstrap toute entree permettant de
   recreer:
   - `natal_interpretation_short`;
   - `natal_long_free`;
   - `natal_interpretation` comme Basic ou Free.
3. Supprimer ou deplacer hors runtime les scripts qui seedent les anciens prompts.
4. Remplacer les fixtures positives admin/catalogue par:
   - cles generiques non natales;
   - cles `theme_natal` contractuelles;
   - tests de rejet explicites.
5. Mettre a jour la cartographie prompt-generation.
6. Verifier que `basic_natal_prompt_payload` reste seulement dans son owner moderne
   `theme_astral`, pas comme pont vers `natal_interpretation`.

## Hors Perimetre

- Supprimer le runtime provider legacy: traite par CS-441.
- Supprimer les routes publiques historiques: traite par CS-443.
- Supprimer les documents historiques `_condamad`.
- Modifier `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `backend/app/services/llm_generation/admin_prompts.py`
- `backend/app/domain/llm/prompting`
- `backend/app/domain/llm/configuration`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de shim ou facade legacy.
  - `RG-018` - pas de fallback prompt natal supporte.
  - `RG-021` - tout fallback restant est classifie, aucune cle canonique ajoutee.
  - `RG-023` - ownership des scripts.
  - `RG-149` - cartographie prompt-generation exacte.
  - `RG-171` - Basic ne route pas par anciennes cles.
  - `RG-173` - pas de raw old use case public.
  - `RG-174` - zero public/runtime hit legacy.
- Required regression evidence:
  - Scans zero-hit dans catalogues/seeds/scripts/admin prompts.
  - Tests prompt governance et legacy extinction.
  - Diff de cartographie prompt-generation.
- Allowed differences:
  - Suppression de scripts et seeds obsoletes.
  - Renommage de fixtures admin/catalogue vers des cles non natales.

## Criteres D'acceptation

1. `admin_prompts.py` ne contient plus `natal_long_free`.
2. Aucun script ou bootstrap executable ne seed
   `natal_interpretation_short` ou `natal_long_free`.
3. Aucun catalogue runtime ne conserve ces cles comme fallback executable.
4. `natal_interpretation` n'est plus mappe a Basic ou Free dans une taxonomie runtime.
5. Les tests admin/catalogue n'utilisent plus les anciens use cases natals comme
   fixtures positives.
6. La cartographie prompt-generation indique que le natal moderne passe par
   `theme_natal` contracts.
7. Les hits restants sur anciens symboles sont limites aux preuves `_condamad` ou
   tests d'extinction.
8. CS-440 `CR-3` et `CR-4` sont resolus pour la partie catalogues/seeds/prompts.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py --tb=short
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/domain/llm/prompting backend/app/domain/llm/configuration backend/app/ops/llm/bootstrap backend/scripts backend/app/services/llm_generation/admin_prompts.py
rg -n "natal_interpretation_short|natal_long_free" backend/tests backend/app/tests
rg -n "theme_natal|natal_interpretation_short|natal_long_free|admin-only" _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md
```

## Dependances

- Peut etre implementee en parallele de CS-441.
- Doit etre terminee avant CS-444.

## Risques

Certains tests admin utilisent les anciens use cases comme donnees commodes. Les
remplacements doivent etre semantiquement neutres pour l'admin LLM, sans garder un
use case natal supprime comme exemple nominal.
