# CS-378 - Corriger Findings Review Adversariale Finale Theme Astral

<!-- Commentaire global: ce brief cadre la correction finale des findings issus de la revue adversariale theme astral. -->

## Resume

Corriger tous les findings actionnables issus de CS-377, puis relancer les validations jusqu'a obtenir une cloture propre du contrat `theme_astral`.

## Contexte

CS-377 doit produire une revue adversariale finale. Cette story existe pour eviter que les findings restent documentes mais non corriges.

## Objectif

Atteindre un etat final ou:

- aucun finding critique, majeur ou moyen ne reste ouvert;
- les findings mineurs sont corriges ou explicitement acceptes;
- les tests et docs correspondent au code;
- les payloads exemples sont regeneres si necessaire;
- le rapport de correction prouve la fermeture.

## Perimetre inclus

1. Lire le rapport CS-377.
2. Classer chaque finding: corriger, accepter, faux positif, hors perimetre.
3. Corriger le code, les tests, les docs et les exemples impactes.
4. Ajouter des tests de regression pour chaque bug corrige.
5. Regenerer les exemples si le contrat ou les donnees changent.
6. Relancer lint et tests.
7. Relancer CS-377 ou une revue ciblee equivalente sur les fichiers modifies.
8. Produire une note de cloture.

## Hors perimetre

- Ajouter de nouvelles features.
- Reprendre l'architecture complete sauf finding bloquant.
- Masquer un finding par modification du rapport.
- Appeler un provider LLM sans opt-in explicite.

## Sources obligatoires

- Audit CS-377 final
- Tous les fichiers modifies par CS-372 a CS-376
- `backend/tests/**`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`

## Livrable attendu

Creer:

```text
_condamad/reports/cs-378-corrections-review-adversariale-finale-theme-astral.md
```

Le rapport doit contenir:

1. Liste des findings CS-377.
2. Decision pour chaque finding.
3. Correction appliquee.
4. Tests ajoutes ou modifies.
5. Commandes executees.
6. Resultat final.
7. Risques residuels acceptes.

## Criteres d'acceptation

1. Tous les findings CS-377 ont une decision tracee.
2. Aucun finding Critical/High/Medium actionnable ne reste ouvert.
3. Les corrections sont couvertes par tests ou validations documentees.
4. `ruff format`, `ruff check` et les tests cibles passent.
5. Si le contrat change, les exemples et docs sont mis a jour.
6. Le worktree ne contient pas de modification hors perimetre non expliquee.
7. Une re-review post-correction prouve que les findings corriges ne restent pas ouverts.
8. Si un finding est accepte, son risque residuel a un owner et une justification.

## Commandes de validation minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short
```

Si des changements plus larges touchent le runtime LLM:

```powershell
python -B -m pytest -q tests --tb=short
```

Validation documentaire et exemples:

```powershell
Get-Content ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\free-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\basic-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\premium-provider-payload.json | ConvertFrom-Json | Out-Null
rg -n "\{\{|TODO|TBD|Quand CS-371 sera implemente" ..\_condamad\docs ..\_condamad\examples
```

Re-review minimale:

```powershell
rg -n "Critical|High|Medium|open|invalide|corrections requises" ..\_condamad\audits\theme-astral-prompt-contract ..\_condamad\reports\cs-378-corrections-review-adversariale-finale-theme-astral.md
```

## Risques

Le risque principal est de traiter CS-378 comme une formalite. Cette story ne doit etre terminee que si les findings de CS-377 sont vraiment fermes ou explicitement acceptes avec justification.
