# CS-406 - Router Basic Complete Vers Une Assembly Natale V3

<!-- Commentaire global: ce brief cadre la correction structurelle du routage LLM Basic pour les lectures natales completes. -->

## Resume

Corriger le chemin `POST /natal/interpretation` pour qu'un utilisateur `basic` demandant
`level=complete` n'utilise plus l'assembly `natal/interpretation/free` ni le prompt court
`natal_interpretation_short`. Le flux Basic complete doit resoudre une assembly V3 explicite
pour `natal/interpretation/basic`, basee sur le use case `natal_interpretation`, le schema
`AstroResponse_v3` et un profil d'execution Basic dedie.

## Contexte

L'echec observe n'est pas un echec aleatoire du LLM V3. Le plan Basic est actuellement
normalise en `free` avant resolution d'assembly:

```text
POST /natal/interpretation plan=basic, level=complete
Gateway normalize_plan_scope(basic) -> free
Assembly natal/interpretation/free
Prompt natal_interpretation_short
Schema gateway AstroResponse_v1
Service tente AstroResponseV3, echoue, puis retombe V2/V1
Projection narrative complete rejetee ensuite par CS-396
```

La correction doit etre ciblee: ne pas transformer globalement `basic` en `premium` pour
`chat`, `guidance` ou d'autres familles. Le probleme concerne la lecture natale complete,
pas tous les usages Basic.

## Analyse Code Actuel

Evidence consultee:

- `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.
- `backend/app/domain/llm/governance/feature_taxonomy.py` - `normalize_plan_scope()` ne
  reconnait que `premium`, `pro`, `ultra`, `full`; `basic` tombe donc sur `free`.
- `backend/app/domain/llm/runtime/gateway.py` - `_resolve_plan()` normalise le plan avant
  `AssemblyRegistry.get_active_config_sync()`.
- `backend/app/domain/llm/runtime/adapter.py` - `generate_natal_interpretation()` mappe
  `natal_interpretation` et `natal_interpretation_short` vers la subfeature
  `interpretation`, puis transmet `natal_input.plan`.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - le service
  construit `NatalExecutionInput(plan=user_plan)` avec `user_plan` issu des entitlements.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` - seules les assemblies
  `natal/interpretation/free -> natal_interpretation_short` et
  `natal/interpretation/premium -> natal_interpretation` sont seedees.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` -
  `natal_interpretation` pointe sur `AstroResponse_v3`, tandis que
  `natal_interpretation_short` pointe sur `AstroResponse_v1`.

## Objectif

Garantir:

```text
Basic + complete + natal/interpretation => assembly Basic V3
Free + complete + variant free_short => experience courte explicite
Premium + complete => assembly Premium V3 inchangee
Basic chat/guidance => comportement existant preserve tant qu'aucune assembly Basic dediee n'existe
```

## Perimetre Inclus

1. Ajouter une assembly seedee `("natal", "interpretation", "basic", "natal_interpretation")`.
2. Creer ou mettre a jour le profil d'execution `natal/interpretation/basic` avec un modele,
   budget et verbosity explicites pour Basic, sans heriter du profil free par defaut.
3. Introduire une normalisation contextualisee cote gateway pour que `basic` soit conserve
   uniquement dans le chemin runtime natal complet (`feature=natal`, `subfeature=interpretation`,
   `use_case=natal_interpretation`, contexte `level=complete` quand disponible).
4. Ne pas modifier le mapping global `basic -> free` pour les familles qui n'ont pas de
   contrat Basic explicite.
5. Ajouter une garde prouvant qu'une simple addition de seed ne suffit pas: la resolution doit
   appeler `AssemblyRegistry` avec `plan="basic"` sur ce chemin.
6. Ajouter des tests de resolution prouvant que Basic complete resout
   `natal/interpretation/basic` et que Free/Premium restent stables.
7. Ajouter une garde contre la regression ou `basic` redeviendrait `free` sur ce chemin.
8. Mettre a jour les fixtures ou helpers de seed necessaires sans creer de `requirements.txt`.

## Hors Perimetre

- Changer les droits commerciaux, quotas ou prix Basic/Premium.
- Ajouter une nouvelle famille LLM.
- Modifier le prompt V3 lui-meme, sauf si le seed doit pointer vers le prompt publie existant.
- Mapper globalement `basic` vers `premium` dans `normalize_plan_scope()`.
- Corriger le rendu frontend.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - conserver la classification explicite du processus natal moderne et ne pas
    promouvoir de payload legacy prompt-visible.
  - `RG-150` - ne pas exposer les rejets comme interpretations publiques.
  - `RG-152` - les lectures completes acceptees restent sous contrat
    `narrative_natal_reading_v1`.
  - `RG-155` - Basic/Premium ne doivent pas etre projetes avec padding, sources vides ou
    chapitres dupliques.
  - `RG-156` - la richesse editoriale Basic doit continuer d'utiliser
    `llm_astrology_input_v1.shaping.support_elements`.
  - `RG-157` - la correction ne doit pas consommer de quota avant acceptation.
- Required regression evidence:
  - `pytest -q backend/tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal"`
  - `pytest -q backend/tests/llm_orchestration/test_execution_profile_taxonomy.py`
  - `pytest -q backend/tests/integration/test_admin_llm_catalog.py -k "natal and basic"`
  - `pytest -q backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py` (nouveau test attendu)
  - `rg -n '"natal", "interpretation", "basic"' backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- Allowed differences:
  - Une nouvelle assembly publiee `natal/interpretation/basic/fr-FR` apparait.
  - Les metriques et logs Basic complete montrent `natal_interpretation` au lieu de
    `natal_interpretation_short`.

## Criteres D'acceptation

1. `basic` ne resout plus `natal/interpretation/free` pour une lecture natale `complete`.
2. L'assembly Basic complete pointe vers le prompt/use case `natal_interpretation`.
3. L'assembly Basic complete pointe vers `AstroResponse_v3`.
4. L'execution profile Basic est explicite et ne depend pas d'un fallback Premium implicite.
5. L'execution profile Basic ne retombe pas sur le profil free `gpt-4o-mini` par defaut; le
   modele, le budget et la verbosity sont un choix produit explicite pour V3.
6. Free continue d'utiliser son experience courte explicite.
7. Premium continue d'utiliser `natal_interpretation` sans regression.
8. Chat et Guidance Basic ne changent pas de scope sauf assembly Basic dediee existante.
9. Les tests echouent si `normalize_plan_scope(basic)` redevient le seul chemin pour
   `natal/interpretation/basic`.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "basic or natal" --tb=short
python -B -m pytest -q tests/llm_orchestration/test_execution_profile_taxonomy.py --tb=short
python -B -m pytest -q tests/integration/test_admin_llm_catalog.py -k "natal and basic" --tb=short
python -B -m pytest -q tests/unit/test_seed_66_20_taxonomy_basic_natal.py --tb=short
rg -n '"natal", "interpretation", "basic"' app/ops/llm/bootstrap/seed_66_20_taxonomy.py
```

## Dependances

- CS-396.
- CS-397.
- CS-398.

## Risques

Le risque principal est un correctif trop large qui ferait passer tout Basic en Premium dans
le gateway. La correction doit rester taxonomique et ciblee sur `natal/interpretation`
complete.
