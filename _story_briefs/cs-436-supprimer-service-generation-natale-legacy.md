# CS-436 - Supprimer Le Service De Generation Natale Legacy

<!-- Commentaire global: ce brief cadre la suppression du dernier chemin backend capable d'appeler le provider natal legacy. -->

## Resume

Supprimer le chemin generatif restant dans `NatalInterpretationService` et retirer
`AIEngineAdapter.generate_natal_interpretation` comme point d'entree executable pour
le theme natal public ou premium. Apres cette story, le theme natal ne doit plus
disposer d'un service generatif historique capable de contourner les contrats
`theme_natal`.

Le but n'est pas de casser la relecture d'anciennes lignes, mais de separer
physiquement:

- lecture historique readonly;
- projection/formatage d'anciennes interpretations;
- generation contractuelle moderne via `ThemeNatalBasicFullReadingRuntime` et futurs
  runtimes premium explicites.

## Perimetre Inclus

1. Extraire ou conserver uniquement les fonctions readonly necessaires a la lecture
   historique des `UserNatalInterpretationModel`.
2. Supprimer le flux `NatalInterpretationService.interpret(...)` comme generateur
   provider-capable.
3. Supprimer les branches qui construisent `NatalExecutionInput` depuis:
   - `level`;
   - `variant_code`;
   - `use_case_key=natal_interpretation`;
   - `module`;
   - `question`.
4. Retirer l'appel provider legacy:
   `AIEngineAdapter.generate_natal_interpretation(...)`.
5. Supprimer physiquement `AIEngineAdapter.generate_natal_interpretation`; ne pas
   conserver de methode stub, alias, facade ou garde runtime qui maintiendrait le
   symbole comme API interne disponible.
6. Remplacer les tests nominaux du service legacy par des tests d'extinction:
   - l'ancien service ne peut pas appeler le provider;
   - Basic/Premium publics passent par `theme_natal` contracts;
   - toute tentative interne legacy echoue avant provider.
7. Documenter les fonctions readonly restantes dans une allowlist reduite, avec une
   decision d'expiration et un proprietaire de suppression.
8. Supprimer les imports, DTO et helpers qui n'existent plus que pour nourrir
   l'ancien appel provider.

## Hors Perimetre

- Construire le runtime Premium complet.
- Migrer les donnees historiques.
- Supprimer les routes GET/PDF historiques, qui seront traitees par CS-438.
- Renommer les champs entitlement globaux `variant_code` hors theme natal.
- Toucher `_condamad/run-state.json`.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/theme_natal_product_actions.py`
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`
- `backend/app/domain/theme_natal/generation_contracts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-001` - pas de facade ou wrapper legacy de remplacement.
  - `RG-005` - les routeurs ne doivent pas absorber la logique retiree du service.
  - `RG-006` - les contrats restent hors couche API.
  - `RG-018` - pas de fallback prompt natal supporte.
  - `RG-149` - la cartographie prompt-generation doit rester exacte.
  - `RG-150` - les rejets restent hors interpretations publiques.
  - `RG-164` - Basic reste selectionne via son owner moderne.
  - `RG-167` - Basic complete persiste/reutilise le runtime Basic moderne.
  - `RG-168` - le contrat public Basic reste strict.
  - `RG-173` - toute generation publique passe par product+LLM contracts.
- Non-applicable invariants:
  - `RG-153`, `RG-154`, `RG-158`, `RG-170` - la story ne modifie pas encore le DOM front.
- Required regression evidence:
  - Scan zero-hit des appels provider legacy depuis le runtime natal public.
  - Tests backend prouvant que les anciens chemins echouent avant provider.
  - Tests product-action et runtime Basic toujours verts.
- Allowed differences:
  - Suppression de fonctions, tests et mocks nominaux legacy.
  - Maintien de helpers readonly uniquement si CS-438 les supprime ou les absorbe
    ensuite dans la surface `theme_natal`; aucun helper conserve ne peut appeler
    le provider.

## Criteres D'acceptation

1. Aucun code public ou service product-action ne peut appeler
   `NatalInterpretationService.interpret(...)`.
2. Aucun chemin runtime natal ne peut instancier `NatalExecutionInput` pour
   `use_case_key=natal_interpretation`.
3. `AIEngineAdapter.generate_natal_interpretation(...)` est absent de
   `backend/app`; aucun stub, alias ou remplacement legacy n'est accepte.
4. Aucun test nominal ne mocke encore `generate_natal_interpretation` pour prouver
   une generation Basic ou Free.
5. Les anciennes lignes `UserNatalInterpretationModel` restent relisibles uniquement
   par un service/projection readonly.
6. Les erreurs legacy restantes mentionnent une migration vers
   `/v1/theme-natal/readings` mais ne construisent aucun payload provider.
7. Les scans ne trouvent plus `generate_natal_interpretation` dans `backend/app`
   hors preuves de migration non runtime explicitement justifiees.
8. Les tests product-action, slots, Basic runtime et contract-bound gateway restent
   verts.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/theme_natal tests/integration/test_theme_natal_public_api_product_actions.py tests/integration/test_theme_natal_basic_full_reading_runtime.py tests/integration/test_theme_natal_reading_slots.py tests/integration/test_theme_natal_concurrency.py --tb=short
python -B -m pytest -q tests/llm_orchestration/test_contract_bound_llm_gateway.py tests/llm_orchestration/test_contract_bound_rejection_workflow.py --tb=short
```

Scans:

```powershell
rg -n "AIEngineAdapter\.generate_natal_interpretation|async def generate_natal_interpretation|generate_natal_interpretation\(" backend/app
rg -n "use_case_key=.*natal_interpretation|natal_interpretation.*plan.*basic|legacy_basic_natal_generation_disabled" backend/app/services backend/app/domain
rg -n "patch\.object\(AIEngineAdapter, \"generate_natal_interpretation\"|fake_generate_natal_interpretation" backend/tests backend/app/tests
```

## Dependances

- CS-426 a CS-435 livres.
- CS-437 peut suivre ou etre menee en parallele uniquement si les scans provider
  restent independants.

## Risques

Le risque principal est de supprimer une fonction encore utilisee pour relire une
ancienne interpretation. Toute conservation doit etre readonly, nommee comme telle,
et interdite d'appel provider par test.
