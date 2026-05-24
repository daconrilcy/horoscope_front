# CS-262 — Audit Existing Prompt Version And answer_id Storage

## Résumé

Auditer l'existant autour du stockage `answer_id`, versions de prompt, provider, modèle et snapshots de prompt.

## Contexte

Plusieurs champs nécessaires à `narrative_answer_audit_v1` existent peut-être déjà. Avant d'ajouter de nouveaux contrats ou migrations, il faut vérifier l'état réel.

## Objectif

Produire un audit ciblé des capacités existantes de traçabilité IA.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les modèles, tables, services et tests liés aux réponses IA.
2. Vérifier l'existence de `answer_id`.
3. Vérifier le stockage de `prompt_version`, provider et modèle.
4. Vérifier la conservation du prompt complet ou d'une référence suffisante.
5. Identifier les écarts avec CS-259.

## Hors périmètre

- Corriger les écarts.
- Ajouter une migration.
- Modifier les prompts.
- Changer la politique RGPD.

## Critères d'acceptation

1. Un document d'audit existe.
2. Chaque champ requis par CS-259 est marqué présent, partiel ou absent.
3. Les emplacements code/db concernés sont cités.
4. Les risques de migration sont listés.
5. Aucune modification applicative n'est réalisée.

## Validation attendue

```powershell
rg -n "answer_id|prompt_version|provider|model|prompt" .\backend .\docs .\_condamad
git status --short -- backend/app backend/tests frontend/src
```

## Dépendances

- CS-259 pour le contrat cible.

## Risques

Le risque principal est de concevoir un doublon de stockage alors qu'une surface partielle existe déjà. L'audit doit précéder l'implémentation.



