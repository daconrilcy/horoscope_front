# CS-283 — Define B2C Projection Entitlement Policy

## Résumé

Définir la politique d'accès B2C aux projections astrologiques pour les plans free, basic et premium.

## Contexte

Les plans B2C ne doivent pas se différencier par l'exposition de runtime technique. Il faut néanmoins formaliser quelles projections et quelles profondeurs de contenu chaque plan peut demander, afin que l'API et les tests d'autorisation disposent d'une matrice claire.

## Objectif

Créer une matrice d'entitlements par plan B2C et par projection.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Mapper chaque projection B2C autorisée aux plans free/basic/premium.
2. Définir les projections interdites aux clients.
3. Définir les erreurs plan insuffisant.
4. Définir les règles d'audit IA déclenchées par basic/premium/long/sensitive.
5. Définir les limites ou quotas si une décision produit existe déjà.

## Hors périmètre

- Implémenter un système de paiement.
- Implémenter une API B2B.
- Exposer les projections internes.
- Modifier le frontend.

## Critères d'acceptation

1. Chaque projection client est mappée à free, basic ou premium.
2. Les projections internes restent interdites aux clients B2C.
3. Les réponses basic/premium déclenchent l'audit IA.
4. Les erreurs plan insuffisant sont contrôlées.
5. Les futurs tests d'autorisation API peuvent s'appuyer sur la matrice.

## Validation attendue

```powershell
rg -n "entitlement|free|basic|premium|plan insuffisant|projection interne" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-256 pour `structured_facts_v1`.
- CS-257 pour `beginner_summary_v1`.
- CS-258 pour `client_interpretation_projection_v1`.

## Risques

Le risque principal est d'implémenter les plans directement dans les routes sans matrice produit explicite. La politique doit être lisible avant les contrôles d'accès.



