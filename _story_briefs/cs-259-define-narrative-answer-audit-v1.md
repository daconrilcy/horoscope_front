# CS-259 — Define narrative_answer_audit_v1

## Résumé

Définir `narrative_answer_audit_v1` pour auditer les réponses LLM basic, premium, longues ou sensibles.

## Contexte

Le LLM est rédacteur, jamais source de vérité astrologique. Les réponses payantes, longues ou sensibles doivent être rattachées aux faits, signaux, versions de prompt, provider, modèle et preuves utilisées.

## Objectif

Spécifier le contrat d'audit des réponses narratives IA.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les champs obligatoires : `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`, `projection_version`, `projection_hash`.
2. Ajouter `llm_input_version`, `llm_input_hash`, `prompt_version`, `provider`, `model`.
3. Définir `grounding_status`.
4. Définir la conservation du prompt complet ou du couple `prompt_ref` + payload.
5. Définir le stockage des réponses rejetées.
6. Définir les catégories `answer_type` : `basic`, `premium`, `long`, `sensitive`, `free_short`.

## Hors périmètre

- Implémenter la persistance.
- Définir la rétention RGPD finale.
- Créer un écran admin.
- Modifier les prompts.

## Critères d'acceptation

1. Le contrat d'audit est versionné.
2. Toutes les réponses basic, premium, longues ou sensibles sont dans le périmètre.
3. Les hash de projection et d'entrée LLM sont obligatoires.
4. Les statuts `grounded`, `partial`, `ungrounded`, `rejected`, `not_checked` sont définis.
5. `answer_type` ou `response_category` permet de distinguer `basic`, `premium`, `long`, `sensitive` et `free_short`.
6. Le client ne voit pas les preuves techniques.

## Validation attendue

```powershell
rg -n "narrative_answer_audit_v1|answer_id|answer_type|projection_hash|llm_input_hash|grounding_status|rejected" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-254 pour `AINarrativeInputContract`.
- CS-256 pour `structured_facts_v1`.

## Risques

Le risque principal est de stocker une narration sans pouvoir prouver ses sources. Le contrat doit rendre l'audit traçable avant l'industrialisation LLM.



