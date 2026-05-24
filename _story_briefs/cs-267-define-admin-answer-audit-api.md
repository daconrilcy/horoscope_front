# CS-267 — Define admin_answer_audit API

## Résumé

Définir l'API admin permettant de consulter les audits de réponses narratives IA.

## Contexte

L'admin doit pouvoir analyser les réponses, preuves, versions et rejets. Cette surface est distincte des endpoints client et du debug de calcul.

## Objectif

Spécifier `admin_answer_audit_v1` comme API protégée de consultation et diagnostic.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les cas d'usage admin.
2. Définir les champs consultables.
3. Définir les filtres : statut, plan, date, provider, modèle.
4. Définir les règles de masquage des données de naissance.
5. Définir les erreurs et permissions.

## Hors périmètre

- Implémenter l'interface admin.
- Implémenter le replay complet.
- Donner accès aux clients.
- Fusionner avec le debug calcul.

## Critères d'acceptation

1. L'API admin est documentée comme surface interne protégée.
2. Elle expose les preuves techniques uniquement à l'admin autorisé.
3. Les données sensibles sont masquées selon politique.
4. Elle permet de consulter les réponses rejetées.
5. Elle reste séparée de `admin_chart_diagnostics_v1`.

## Validation attendue

```powershell
rg -n "admin_answer_audit|réponses rejetées|evidence_refs|masquage|admin" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-259 pour le contrat d'audit.
- CS-261 pour le workflow de rejet.
- CS-288 pour la persistance réelle de `narrative_answer_audit_v1`.
- CS-289 pour la validation réelle des `evidence_refs`.
- CS-290 pour le workflow réel de rejet.

## Risques

Le risque principal est de créer un endpoint admin trop large qui mélange audit IA, debug calcul et données personnelles brutes.



