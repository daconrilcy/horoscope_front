# CS-360 - Audit Admin Manual Execution Provider Capable

<!-- Commentaire global: ce brief cadre l'audit approfondi de la surface admin manual execution provider-capable. -->

## Resume

Creuser la surface `admin manual execution`, qui est admin-only mais provider-capable, afin de decider s'il faut la documenter comme surface admin supportee, la restreindre, migrer ses samples, ou la decommissionner.

Ce brief contient `audit` dans son nom car il demande un audit.

## Contexte

CS-353 a prouve que `execute_admin_catalog_sample_payload` construit un `LLMExecutionRequest` depuis un sample payload admin et appelle `LLMGateway.execute_request`. Les samples natals peuvent contenir `chart_json`. CS-354/CS-355 ont laisse la politique ouverte. Le dernier choix utilisateur demande de ne garder aucune dette, mais indique que l'admin-only reste a creuser car le comportement n'est pas clair.

## Objectif

Produire une decision sourcee sur admin manual execution:

- surface admin supportee a documenter et guarder;
- surface a restreindre;
- surface a migrer vers des sample payloads non legacy;
- surface a decommissionner.

## Perimetre inclus

1. Auditer le routeur admin LLM prompts.
2. Auditer les contrats `AdminCatalogManualExecute*`.
3. Auditer les sample payloads et leurs validations.
4. Auditer les permissions et logs/audit events.
5. Auditer les tests d'integration admin LLM.
6. Identifier si `chart_json` est necessaire, tolerable temporairement ou a migrer.
7. Produire une recommandation d'implementation.

## Hors perimetre

- Changer la politique sans preuve.
- Faire un appel provider reel.
- Modifier les droits admin sans story d'implementation dediee.
- Promouvoir admin manual execution comme flux public.

## Sources obligatoires

- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/services/api_contracts/admin/llm/prompts.py`
- `backend/app/services/llm_generation/admin_sample_payloads.py`
- `backend/app/api/v1/routers/admin/llm/sample_payloads.py`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/integration/test_admin_llm_sample_payloads.py`
- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`

## Livrable attendu

Creer:

```text
_condamad/audits/admin-manual-llm-execution/<YYYY-MM-DD-HHMM>/01-admin-manual-execution-provider-capable-audit.md
```

Le rapport doit contenir:

1. Resume executif.
2. Trace route -> sample payload -> gateway.
3. Matrice permissions, logs et audit.
4. Matrice sample payloads et carriers legacy.
5. Decision recommandee: documenter, restreindre, migrer ou decommissionner.
6. Stories candidates d'implementation.

## Criteres d'acceptation

1. Le rapport prouve si la surface est seulement admin ou exposable indirectement.
2. Le rapport distingue sample payload CRUD et execution live provider.
3. La place de `chart_json` dans les samples est documentee.
4. La recommandation ne conserve aucune dette implicite.
5. Une suite d'implementation est proposee si restriction, migration ou decommission est retenue.

## Validation attendue

```powershell
rg -n "ADMIN_MANUAL_EXECUTE_ROUTE_PATH|execute_admin_catalog_sample_payload|AdminCatalogManualExecute|sample_payload|chart_json|LLMGateway" backend/app backend/tests
rg -n "admin manual execution|admin-only|provider-capable" _condamad/docs/prompt-generation-cartography _condamad/audits/admin-manual-llm-execution
```

Les commandes Python doivent etre executees apres activation du venv.

## Risques

Le risque principal est de traiter cette surface comme simple outil admin alors qu'elle peut executer un appel provider reel a partir de payloads de test ou de preview.
