# Audit des limites routeur / logique / services

## Périmètre

Audit AC16, AC17 et AC18 sur les deux fichiers explicitement ciblés par la story.

## Décisions

| Fichier cible | Responsabilité avant | Refactor appliqué | Limite verrouillée |
|---|---|---|---|
| `router_logic/admin/llm/prompts.py` | Catalogue, snapshots release, diff release, preview runtime, exécution manuelle, audit | Extraction de `release_snapshots.py` et `manual_execution.py` | Garde de taille maximale et imports directs depuis les nouveaux propriétaires |
| `routers/ops/entitlement_mutation_audits.py` | Routes HTTP, filtrage diff/review, pagination, appels services et mapping réponse | `list_mutation_audits` délègue son flux à `build_mutation_audit_list_response` dans `router_logic` | Garde vérifiant que le handler ne porte plus le `select` métier de ce flux |

## Logique métier résiduelle

- Les endpoints restants de `routers/ops/entitlement_mutation_audits.py` continuent d'appeler les services existants `CanonicalEntitlement*Service`.
- Les accès DB directs encore présents dans ce routeur concernent surtout les endpoints suppression rules, retry/history et review history. Ils sont inventoriés par scan et restent des candidats de découpage ultérieur si la story est élargie.
- Le découpage effectué évite de renommer les URLs actives et ne crée aucun wrapper d'ancien chemin Python.

## Gardes automatisés

- `test_target_api_files_stay_below_responsibility_limits` empêche les deux fichiers cibles de revenir à leur taille multi-responsabilités initiale.
- `test_ops_entitlement_audit_list_route_delegates_business_flow` bloque le retour du flux de liste mutation-audits directement dans le routeur.
- `test_api_v1_error_model_uses_base_class_inheritance` verrouille le modèle d'erreur centralisé par héritage.
