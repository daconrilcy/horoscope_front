# CS-431 - Contract Bound LLM Gateway And Rejection Workflow

<!-- Commentaire global: ce brief cadre le gateway LLM pilote par snapshot contractuel et le rejet strict des sorties invalides. -->

## Resume

Faire evoluer le gateway LLM pour recevoir un `ResolvedGenerationContractSnapshot` au lieu d'un
ancien `use_case` brut pour le theme natal. Le gateway execute un contrat deja resolu; il ne choisit
plus le prompt Basic/Premium par heuristique.

## Perimetre Inclus

1. Definir `ResolvedGenerationContractSnapshot`.
2. Brancher le gateway sur:
   - engine profile;
   - prompt contract;
   - output schema;
   - data contract.
3. Interdire l'injection de `basic_natal_prompt_payload` dans un prompt premium historique.
4. Implementer parsing JSON strict.
5. Implementer rejection workflow:
   - JSON invalide;
   - schema invalide;
   - fait invente;
   - contradiction astrologique;
   - fuite technique;
   - texte mecanique/vide.
6. Autoriser repair unique seulement pour erreurs de forme simples.
7. Persister les rejets dans `llm_generation_runs`, jamais dans les lectures publiques.
8. Garantir que le gateway ne devient pas proprietaire des regles metier theme natal:
   - il execute un contrat;
   - il applique des validateurs fournis par le contrat;
   - les validateurs specifiques theme natal restent dans un module dedie, injecte via le contrat
     ou le runtime de lecture natale.

## Hors Perimetre

- Frontend.
- Cutover endpoint public.
- Suppression physique de tous les fichiers legacy.
- Appels provider live obligatoires en tests.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-018` - pas de fallback prompt pour familles supportees.
  - `RG-021` - fallbacks classes.
  - `RG-149` - cartographie prompt-generation.
  - `RG-150` - rejets non publics.
  - `RG-152` - pas de fuite technique.
  - `RG-155` - invalides rejetes hors public.
  - `RG-166` - drafts invalides repares une fois puis rejetes.
  - `RG-171` - Basic ne route pas par anciennes cles natal.
- Required regression evidence:
  - Tests gateway snapshot contractuel.
  - Tests rejection workflow.
  - Scan anti `basic_natal_prompt_payload` dans `natal_interpretation`.
- Allowed differences:
  - Nouveau chemin gateway contractuel pour theme natal.

## Criteres D'acceptation

1. Le gateway theme natal accepte un snapshot contractuel, pas un use case legacy brut.
2. Basic ne peut pas rendre un prompt contenant `EXIGENCE PREMIUM` ou `AstroResponse_v3`.
3. Une sortie JSON invalide est reparee une fois ou rejetee.
4. Une invention factuelle est rejetee sans repair de fond.
5. Une fuite technique est rejetee.
6. Les rejets sont audit-only et absents des routes publiques.
7. Les logs contiennent versions/hashes de contrat.
8. Aucune regle metier theme natal nouvelle n'est codee directement dans le gateway hors
   orchestration generique contrat/validator.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration tests/integration -k "gateway or rejection or generation_contract or theme_natal" --tb=short
```

Scans:

```powershell
rg -n "basic_natal_prompt_payload.*natal_interpretation|natal_interpretation.*basic_natal_prompt_payload" backend/app backend/tests
rg -n "ThemeNatal|natal_reading|basic_full_reading" backend/app/domain/llm/runtime/gateway.py
rg -n "EXIGENCE PREMIUM|AstroResponse_v3|fallback_default" backend/app/domain/llm backend/app/services/llm_generation/natal backend/tests
```

## Dependances

- CS-429.
- CS-430.

## Risques

Le risque est de laisser le gateway corriger un mauvais routage produit. Cette story force le
gateway a executer un contrat deja resolu et a echouer en cas d'incoherence.
