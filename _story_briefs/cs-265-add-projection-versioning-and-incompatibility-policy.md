# CS-265 — Add Projection Versioning And Incompatibility Policy

## Résumé

Définir la politique de versioning et d'incompatibilité des projections.

## Contexte

Le produit n'exige pas une compatibilité backward stricte à ce stade, mais chaque projection doit porter une version explicite. Un changement breaking doit passer en v2.

## Objectif

Formaliser les règles de version, dépréciation, incompatibilité source et recalcul éventuel.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir `projection_version` comme obligatoire.
2. Définir les changements breaking.
3. Définir la gestion des versions inconnues ou dépréciées.
4. Définir la politique si `source_versions` est incompatible.
5. Définir les logs admin.

## Hors périmètre

- Maintenir cinq versions historiques.
- Implémenter une migration de données.
- Modifier les projections existantes.
- Définir une API publique stable B2B.

## Critères d'acceptation

1. La politique de versioning est documentée.
2. Les versions inconnues ou dépréciées sont bloquées et loguées.
3. Les incompatibilités source sont bloquantes sauf recalcul autorisé.
4. Le passage v1 -> v2 est clairement décrit.
5. L'absence de compatibilité forte est assumée tant que le produit n'est pas stable/public.

## Validation attendue

```powershell
rg -n "projection_version|v1|v2|dépréciée|source_versions|incompatible|recalcul" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-263 pour le contrat API.
- CS-264 pour la persistance et le hash.

## Risques

Le risque principal est de modifier silencieusement une projection v1. Toute rupture doit créer une nouvelle version.



