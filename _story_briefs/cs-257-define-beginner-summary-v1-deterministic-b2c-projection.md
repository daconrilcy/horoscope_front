# CS-257 — Define beginner_summary_v1 Deterministic B2C Projection

## Résumé

Définir `beginner_summary_v1` comme projection B2C simple, déterministe et compréhensible pour les usages free/basic.

## Contexte

Les clients B2C ne doivent pas voir les données techniques complètes. La projection client simple doit exposer une synthèse astrologique lisible, issue des faits structurés, sans runtime brut ni debug.

## Objectif

Spécifier la projection de base affichable au client, avec un niveau de détail limité et stable.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les champs client autorisés : signes principaux, ascendant si disponible, maison dominante, thèmes dominants.
2. Définir les états `loading`, `empty`, `degraded` et `unavailable`.
3. Définir le comportement si l'heure de naissance manque.
4. Définir le lien avec `structured_facts_v1`.
5. Définir les messages d'erreur contrôlés.

## Hors périmètre

- Exposer des traces ou payloads runtime.
- Ajouter une narration LLM longue.
- Implémenter les écrans frontend.
- Définir les projections premium.

## Critères d'acceptation

1. `beginner_summary_v1` est documentée comme projection B2C déterministe.
2. Les données techniques complètes sont exclues.
3. Le mode dégradé sans heure de naissance est décrit.
4. Les différences avec `structured_facts_v1` sont explicites.
5. La projection reste compatible free/basic sans exposer d'audit technique.

## Validation attendue

```powershell
rg -n "beginner_summary_v1|B2C|free|basic|heure de naissance|mode dégradé" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-256 pour `structured_facts_v1`.
- CS-255 pour les surfaces produit.

## Risques

Le risque principal est de transformer une projection débutant en mini projection expert. Le contrat doit rester lisible, limité et non technique.



