# CS-428 - Public Reading Slots And LLM Generation Runs

<!-- Commentaire global: ce brief cadre la persistence separee entre slots publics acceptes et tentatives LLM techniques. -->

## Resume

Creer la persistence cible qui separe les lectures publiques acceptees des runs LLM techniques.
Une reponse provider rejetee, un retry, un fallback ou une generation concurrente ne doit jamais
modifier une lecture publique deja acceptee.

## Perimetre Inclus

1. Definir le modele conceptuel `ThemeNatalReadingSlot`.
2. Definir le modele conceptuel `LlmGenerationRun`.
3. Ajouter les migrations/tables ou equivalents retenus par l'architecture.
4. Imposer une unicite slot par:
   - `user_id`;
   - `chart_id`;
   - `feature`;
   - `reading_kind`;
   - `product_plan`;
   - `output_variant`;
   - `persona_profile_id`;
   - `contract_version`.
5. Definir les statuts:
   - `empty`;
   - `generating`;
   - `accepted`;
   - `rejected`;
   - `failed_retriable`;
   - `superseded`.
6. Definir le mecanisme d'idempotence/concurrence:
   - contrainte unique DB;
   - transaction;
   - lock applicatif ou `SELECT ... FOR UPDATE` selon support DB.
7. Persister `client_request_id` sur le run LLM ou sur une table d'idempotence.
8. Garantir que GET/list public ne voit que `accepted`.

Precision portabilite DB:

- Si le moteur de test/dev est SQLite, l'idempotence doit etre prouvee par contrainte unique,
  transaction et gestion explicite de `IntegrityError`.
- Si le moteur cible supporte `SELECT ... FOR UPDATE`, le lock pessimiste peut etre utilise en
  complement, mais il ne doit pas etre le seul mecanisme prouve par les tests SQLite.

## Hors Perimetre

- Appel provider.
- Nouveau prompt.
- Cutover frontend.
- Suppression legacy.
- Migration de masse des anciennes interpretations.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-011` - tests DB via helpers/fixtures canoniques.
  - `RG-150` - rejets exclus des routes publiques.
  - `RG-152` - pas de fuites techniques publiques.
  - `RG-155` - pas de padding pour masquer invalides.
  - `RG-157` - quota apres acceptation uniquement.
  - `RG-168` - contrat public Basic strict.
- Required regression evidence:
- Tests migration/schema.
- Tests slot accepted-only.
- Tests concurrence/idempotence.
- Tests `client_request_id`.
- Allowed differences:
  - Nouvelles tables/migrations pour slots/runs.

## Criteres D'acceptation

1. Un slot public accepte est distinct d'un run LLM.
2. Un run rejete ne peut pas etre retourne par GET/list public.
3. Une regeneration ne remplace pas l'ancien public payload avant acceptation.
4. Deux demandes concurrentes sur le meme slot ne creent pas deux slots publics.
5. Le quota n'est pas consomme deux fois en concurrence.
6. `chart_id` est present dans toute cle d'unicite/cache.
7. `created_at` et `accepted_at` ne masquent pas une mise a jour de payload.
8. Deux requetes avec le meme `client_request_id` retournent le meme etat logique.
9. Une repetition du meme `client_request_id` ne cree pas de nouveau run.
10. Deux requetes sans meme `client_request_id` mais visant le meme slot restent protegees par la
    contrainte unique du slot et retournent le slot existant ou son etat `generating`.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration -k "theme_natal and slot" --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
```

Scans:

```powershell
rg -n "ThemeNatalReadingSlot|LlmGenerationRun|accepted_at|source_generation_run_id" backend/app backend/tests
rg -n "client_request_id|idempot" backend/app backend/tests
rg -n "UserNatalInterpretationModel\\.user_id == user_id,[\\s\\S]*UserNatalInterpretationModel\\.level" backend/app/services/llm_generation/natal
```

## Dependances

- CS-427 pour la decision produit.

## Risques

Le risque principal est une implementation qui garde une seule table mixant audit et public. Cette
story impose une separation structurelle.
