# CS-372 - Aligner Delivery Profiles DB Provider Theme Astral

<!-- Commentaire global: ce brief cadre la correction de l'ecart entre les profils provider theme astral et les profils persistants/versionnes en base. -->

## Resume

Corriger l'ecart de contrat entre les profils provider `free/basic/premium` resolus en `essential/expanded/complete` et les profils persistants/versionnes actuellement limites a `essential/deep`.

## Contexte

La revue a identifie un ecart structurel:

- le provider builder expose trois depths LLM-visibles: `essential`, `expanded`, `complete`;
- la famille persistante/versionnee ne connait que `essential` et `deep`;
- les tests de persistence verrouillent cette divergence.

Cet ecart contredit l'objectif: les structures et contrats doivent etre enregistres en base, versionnes, et alignes avec les payloads reels envoyables au LLM.

## Objectif

Faire de `essential`, `expanded`, `complete` la source coherente des profils de livraison `theme_astral` dans:

- les constantes de contrat;
- les seeds DB;
- les assemblies publiees;
- les tests de persistence;
- les exemples et docs si impactes.

## Perimetre inclus

1. Lire `theme_astral_contracts.py`, les seeds et les tests de persistence.
2. Decider la nomenclature canonique finale: `essential`, `expanded`, `complete`.
3. Aligner `THEME_ASTRAL_DELIVERY_PROFILES` sur les trois depths provider.
4. Aligner les assemblies seedees et la lecture active.
5. Supprimer ou migrer `deep` s'il n'a plus de role canonique.
6. Archiver ou invalider toute assembly active `deep` existante au prochain seed.
7. Adapter les tests pour prouver les trois profils actifs.
8. Verifier que les profils restent non commerciaux cote LLM.
9. Mettre a jour la documentation, les exemples et le rapport de livraison impactes.

## Hors perimetre

- Changer les noms commerciaux `free/basic/premium` cote backend.
- Exposer `free/basic/premium` au LLM.
- Modifier le provider LLM.
- Modifier une autre feature que `theme_astral`.

## Sources obligatoires

- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/tests/integration/test_theme_astral_prompt_contract_persistence.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `_condamad/docs/prompt-generation-cartography/theme-astral-llm-json-structure-v1.md`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/structure-comparison.md`
- `_condamad/reports/cs-361-cs-362-cs-363-cs-364-cs-365-cs-366-cs-367-cs-368-cs-369-cs-370-cs-371-delivery-report.md`

## Criteres d'acceptation

1. Les profils persistants actifs sont `essential`, `expanded`, `complete`.
2. Les profils provider resolus depuis `free/basic/premium` referencent ces memes depths.
3. Aucun depth `deep` ne reste actif pour `theme_astral`, sauf mention historique non runtime.
4. Les seeds publient une assembly par depth canonique.
5. `resolve_active_theme_astral_prompt_contract` accepte les trois depths canoniques.
6. Les tests prouvent que les trois depths sont persistants, versionnes et lisibles.
7. Les payloads provider n'exposent toujours pas `free/basic/premium`.
8. La documentation et les exemples ne contredisent plus la DB.
9. Un test prouve que `deep` n'est plus publie actif apres seed, meme si une ancienne ligne existe.
10. Toute mention restante de `deep` est historique, explicitement non runtime, ou supprimee.

## Commandes de validation minimales

Depuis la racine du repository:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_theme_astral_prompt_contract_persistence.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short
```

Scans:

```powershell
rg -n "essential|expanded|complete|deep|THEME_ASTRAL_DELIVERY_PROFILES|THEME_ASTRAL_PROVIDER_DELIVERY_PROFILES" app tests
rg -n "deep" app/domain/llm/configuration/theme_astral_contracts.py app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py tests/integration/test_theme_astral_prompt_contract_persistence.py
rg -n '"plan"\s*:|"free"\s*:|"basic"\s*:|"premium"\s*:' ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\free-provider-payload.json ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\basic-provider-payload.json ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1\premium-provider-payload.json
```

Le scan `deep` doit etre interprete: il doit echouer ou ne retourner que des mentions historiques non runtime. Le scan JSON des labels commerciaux doit ne retourner aucun resultat.

## Risques

Le risque principal est de corriger seulement les tests ou seulement le provider. La correction doit aligner la chaine complete: contrat domaine, seed DB, lecture active, tests et docs.
