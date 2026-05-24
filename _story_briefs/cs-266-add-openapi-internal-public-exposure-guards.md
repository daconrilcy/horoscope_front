# CS-266 — Add OpenAPI Internal/Public Exposure Guards

## Résumé

Ajouter les garde-fous d'exposition OpenAPI entre projections publiques et projections internes.

## Contexte

Les projections internes admin/expert et techno/debug ne doivent pas apparaître comme surfaces client publiques. L'OpenAPI des projections internes n'est pas publique.

## Objectif

Définir puis implémenter les protections empêchant l'exposition accidentelle des contrats internes.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Cartographier endpoints publics et internes.
2. Ajouter des tests ou scans OpenAPI.
3. Vérifier que les projections techniques ne sont pas dans le schéma public.
4. Vérifier les règles d'autorisation.
5. Documenter la séparation public/interne.
6. Ajouter des scans de tokens interdits dans l'OpenAPI publique.

## Hors périmètre

- Implémenter les projections expert.
- Créer un portail développeur B2B.
- Modifier la stratégie d'auth globale.
- Exposer les traces runtime.

## Critères d'acceptation

1. Les projections internes sont absentes de l'OpenAPI publique.
2. Les endpoints internes sont protégés.
3. Les tests empêchent une régression d'exposition.
4. Les erreurs d'accès sont contrôlées.
5. La documentation distingue OpenAPI publique et interne.
6. L'OpenAPI publique ne contient pas : `ChartObjectRuntimeData`, `chart_objects`, `CalculationGraph`, `execution_trace`, `replay_snapshot`, `llm_input`, `expert_technical_projection`, `astrology_full_data`, `admin_chart_diagnostics`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter un scan explicite des tokens interdits :

```powershell
rg -n "ChartObjectRuntimeData|chart_objects|CalculationGraph|execution_trace|replay_snapshot|llm_input|expert_technical_projection|astrology_full_data|admin_chart_diagnostics" .\backend
```

## Dépendances

- CS-263 pour l'endpoint générique.
- CS-265 pour les versions de projection.

## Risques

Le risque principal est de documenter ou générer par erreur une surface interne dans le contrat public. Les scans doivent être automatisables.



