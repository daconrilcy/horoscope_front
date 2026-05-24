# CS-275 — Decide admin_chart_diagnostics Retention / Redaction / Replay Policy

## Résumé

Décider la politique de rétention, redaction et replay avant d'implémenter `admin_chart_diagnostics_v1`.

## Contexte

Le debug calcul et l'audit réponse IA sont séparés. Le replay complet n'est pas encore implémenté et nécessite une décision de stockage, input, version et rétention.

## Objectif

Produire une décision formelle sur ce qui peut être conservé, masqué, consulté et rejoué.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les données de diagnostic calcul.
2. Définir les données à masquer.
3. Définir la rétention cible ou les décisions DPO ouvertes.
4. Définir les prérequis de replay.
5. Définir les logs de consultation admin.

## Hors périmètre

- Implémenter le diagnostic.
- Implémenter le replay.
- Modifier les calculs.
- Exposer les diagnostics aux clients.

## Critères d'acceptation

1. La politique de rétention est décidée ou marquée explicitement ouverte.
2. Les données de naissance sont traitées comme sensibles.
3. Le replay est séparé du diagnostic courant.
4. Les consultations admin doivent être journalisées.
5. Les surfaces client sont exclues.

## Validation attendue

```powershell
rg -n "admin_chart_diagnostics|rétention|redaction|replay|données de naissance|DPO" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-271 pour les permissions.
- CS-272 pour la séparation des endpoints admin.

## Risques

Le risque principal est d'implémenter du replay avant d'avoir validé stockage et rétention. Cette story doit trancher ou bloquer.



