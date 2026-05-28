# CS-377 - Audit Review Adversariale Complete Theme Astral Prompt Contract Final

<!-- Commentaire global: ce brief cadre la revue adversariale finale de toutes les corrections theme astral avant cloture. -->

## Resume

Executer une revue adversariale complete apres CS-372 a CS-376 pour chercher activement tout ecart residuel dans le contrat `theme_astral`, les profils persistants, le payload LLM, les exemples, la documentation, les tests et les preuves.

## Contexte

Cette story est volontairement placee apres les corrections ciblees. Elle ne doit pas confirmer passivement la livraison: elle doit essayer de la casser.

## Objectif

Produire un audit final avec findings tries par severite et preuves fichier/ligne.

## Perimetre inclus

1. Relire les briefs CS-372 a CS-376.
2. Relire les diffs associes.
3. Verifier l'alignement `essential/expanded/complete` sur code, DB, tests, docs et exemples.
4. Verifier que `birth_context` est structure et non derive uniquement de `chart_id`.
5. Verifier que les exemples utilisent des sources interpretatives representatives et sourcees.
6. Verifier que le plan commercial reste backend-only.
7. Verifier que le legacy `chart_json`, `natal_data`, `llm_astrology_input_v1` ne peut pas alimenter `theme_astral`.
8. Verifier que la documentation ne contient plus de contradiction.
9. Verifier que les validations provider smoke sont opt-in si elles existent.
10. Verifier que les commandes negatives sont interpretees correctement: un `rg` sans resultat peut etre un succes attendu.
11. Produire un rapport d'audit adversarial.

## Hors perimetre

- Corriger les findings; cela appartient a CS-378.
- Appeler un provider LLM sauf si CS-376 l'a rendu opt-in et que les preconditions sont explicitement disponibles.
- Redefinir l'architecture.

## Sources obligatoires

- `_story_briefs/cs-372-*.md` a `_story_briefs/cs-376-*.md`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`
- `_condamad/reports/**`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/pyproject.toml`
- `backend/tests/**`

## Livrable attendu

Creer:

```text
_condamad/audits/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/05-audit-review-adversariale-finale-theme-astral-prompt-contract.md
```

Le rapport doit contenir:

1. Verdict global.
2. Findings par severite.
3. Preuve fichier/ligne pour chaque finding.
4. Matrice de conformite CS-372 a CS-376.
5. Matrice des scans positifs attendus et negatifs attendus.
6. Commandes executees.
7. Risques residuels.
8. Decision: pret pour cloture ou corrections requises.

## Criteres d'acceptation

1. Aucun axe critique n'est omis.
2. Les findings ne sont pas vagues: ils pointent des fichiers et lignes.
3. Les scans legacy et plan leakage sont interpretes, pas seulement listes.
4. Le rapport distingue bug, risque accepte, faux positif et hors perimetre.
5. Le rapport ne modifie pas le code.
6. Le rapport mentionne explicitement si CS-376 a ete execute avec provider, skippe par absence d'opt-in, ou non implemente.
7. Le rapport ouvre un finding si les exemples restent fondes sur des fixtures pauvres sans avertissement clair.

## Commandes de validation minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short
```

Scans:

```powershell
rg -n "deep|essential|expanded|complete|delivery_profile|birth_context|birth_date|birth_time_local|birth_place" app tests ..\_condamad\docs ..\_condamad\examples
rg -n "chart_json|natal_data|llm_astrology_input_v1|legacy|free|basic|premium|\"plan\"" app tests ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
```

Les hits legacy hors `theme_astral` doivent etre classes par domaine. Les hits `free/basic/premium` sont acceptables dans les noms de fichiers, tests de mapping backend et docs explicatives, mais pas comme valeurs LLM-visibles dans les payloads provider.

## Risques

Le risque principal est une revue trop complaisante. Cette story doit preferer les preuves negatives et les tentatives de rupture du contrat.
