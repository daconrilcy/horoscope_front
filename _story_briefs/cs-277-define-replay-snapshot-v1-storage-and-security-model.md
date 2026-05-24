# CS-277 — Define replay_snapshot_v1 Storage And Security Model

## Résumé

Définir le modèle de stockage et de sécurité de `replay_snapshot_v1`.

## Contexte

Le replay complet est utile pour support et debug, mais il peut contenir des données sensibles, versions de calcul, inputs et contexte d'exécution. Il doit être cadré avant implémentation.

## Objectif

Spécifier ce qui est stocké pour rejouer un calcul ou une génération, qui peut y accéder et combien de temps.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir le contenu minimal d'un snapshot.
2. Définir les données interdites ou masquées.
3. Définir les permissions.
4. Définir la rétention et purge.
5. Définir les liens avec diagnostics et audit IA.

## Hors périmètre

- Implémenter le replay.
- Exécuter des replays en production.
- Créer une UI.
- Modifier la politique RGPD sans validation.

## Critères d'acceptation

1. `replay_snapshot_v1` a un contrat de stockage documenté.
2. Les données sensibles sont identifiées.
3. Les accès sont limités aux rôles autorisés.
4. La rétention est décidée ou bloquée par décision DPO.
5. Le replay reste séparé de la trace redigée actuelle.

## Validation attendue

```powershell
rg -n "replay_snapshot_v1|snapshot|stockage|sécurité|rétention|audit IA|diagnostics" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-275 pour la politique initiale.
- CS-276 pour le diagnostic admin.

## Risques

Le risque principal est de stocker un snapshot trop complet sans cadre de sécurité. La story doit pouvoir conclure à `non approuvé` si nécessaire.



