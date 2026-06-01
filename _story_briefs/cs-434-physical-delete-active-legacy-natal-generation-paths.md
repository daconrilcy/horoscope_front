# CS-434 - Physical Delete Active Legacy Natal Generation Paths

<!-- Commentaire global: ce brief cadre la suppression physique des chemins actifs de generation natale legacy avant cutover final. -->

## Resume

Supprimer ou neutraliser physiquement les chemins legacy encore generateurs apres mise en place du
runtime contractuel. Les anciennes donnees peuvent rester lisibles en mode compat readonly/debug,
mais aucun endpoint public ne doit pouvoir generer via legacy.

## Perimetre Inclus

1. Supprimer les branches publiques de generation:
   - `natal_interpretation_short`;
   - `natal_long_free` si encore generateur;
   - `natal_interpretation` comme contrat commun Basic/Premium.
2. Supprimer l'injection `basic_natal_prompt_payload` dans prompt premium.
3. Supprimer les fallbacks publics deterministes.
4. Archiver ou supprimer seeds obsoletes selon classification CS-426.
5. Supprimer tests/mocks qui maintiennent le legacy comme nominal.
6. Garder compat readonly strictement non generatrice si necessaire.
7. Ajouter scans anti-retour.
8. Produire une allowlist historique obligatoire des hits qui restent acceptes hors runtime public.

## Hors Perimetre

- Nouveau runtime.
- Redesign frontend.
- Migration de masse des anciennes donnees.
- Suppression de `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/ops/llm/bootstrap`
- `backend/scripts`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de facade/wrapper legacy.
  - `RG-018` - pas de fallback prompt pour familles supportees.
  - `RG-021` - fallbacks restants classifies.
  - `RG-149` - cartographie prompt-generation conservee.
  - `RG-150` - rejets non publics.
  - `RG-171` - Basic ne route pas par anciennes cles.
- Required regression evidence:
  - Scans zero-hit des symboles interdits en runtime public.
  - Tests API/gateway contractuels.
- Rapport before/after de suppression.
- Allowlist historique:
  `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- Allowed differences:
  - Suppression de code legacy actif.
  - Tests legacy nominaux supprimes ou reclasses historical.

## Criteres D'acceptation

1. Aucun endpoint public ne peut generer via `natal_interpretation_short`.
2. Aucun endpoint public ne peut generer via `natal_long_free`.
3. Basic ne peut plus utiliser `natal_interpretation` premium.
4. `PROMPT_FALLBACK_CONFIGS` ne porte aucune cle canonique theme natal generateur public.
5. Les seeds obsoletes sont archives/supprimes/classes.
6. Les tests legacy nominaux sont supprimes ou transformes en guards anti-retour.
7. La compat readonly legacy ne peut pas appeler le provider.
8. Tout hit restant sur les symboles legacy est documente dans `legacy-allowlist.md` avec:
   `symbol | file | reason | allowed_context | non_generative_proof | owner`.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration tests/integration -k "theme_natal or legacy or gateway" --tb=short
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation|template_source=.*fallback_default" backend/app backend/tests
rg -n "EXIGENCE PREMIUM|AstroResponse_v3" backend/app/domain backend/app/services backend/tests
rg -n "use_case_level|variant_code|forceRefresh" backend/app frontend/src
Test-Path _condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md
```

## Dependances

- CS-426.
- CS-431.
- CS-432.
- CS-433 recommande pour frontend.

## Risques

Le risque est de supprimer des surfaces encore necessaires a la lecture historique. La classification
CS-426 doit distinguer `readonly` et `delete` avant suppression.
