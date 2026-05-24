# CS-282 — Expose Transit Projection Only After Proof Gate

## Résumé

Exposer une projection client de transits uniquement après validation du proof gate.

## Contexte

`transit_chart_v1` doit rester non public tant que runtime, preuve, doctrine, projection client, audit et garde-fous d'exposition ne sont pas prêts.

## Objectif

Implémenter l'exposition contrôlée des transits seulement si tous les prérequis sont validés.

Cette story ne peut pas être exécutée si CS-280 ou CS-281 n'ont pas produit leurs preuves attendues.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Vérifier le proof gate.
2. Implémenter l'accès client autorisé.
3. Ajouter les tests d'autorisation et d'exposition.
4. Ajouter les états client nécessaires.
5. Vérifier l'OpenAPI publique.
6. Vérifier explicitement les preuves issues de CS-280 et CS-281 avant toute exposition.

## Hors périmètre

- Exposer sans preuve validée.
- Exposer le runtime brut.
- Ajouter des fixed stars publiques.
- Contourner la segmentation par plan.

## Critères d'acceptation

1. La story est bloquée si le proof gate n'est pas validé.
2. L'API client expose uniquement une projection contrôlée.
3. Les tests empêchent l'exposition de données internes.
4. Les plans B2C sont respectés.
5. Les erreurs et modes dégradés sont gérés.
6. La story est bloquée si CS-280 ou CS-281 n'ont pas livré leurs preuves.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Prévoir aussi la validation frontend si une UI est ajoutée :

```powershell
cd ..\frontend
npm test -- --run
npm run lint
```

## Dépendances

- CS-279 à CS-281.
- CS-266 pour les garde-fous OpenAPI.

## Risques

Le risque principal est de publier les transits avant validation. Cette story doit rester conditionnelle et refuser l'exposition si un prérequis manque.



