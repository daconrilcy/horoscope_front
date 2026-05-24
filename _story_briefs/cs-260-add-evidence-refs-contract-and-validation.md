# CS-260 — Add evidence_refs Contract And Validation

## Résumé

Définir le contrat `evidence_refs` et les validations associées pour chaque section narrative auditée.

## Contexte

Chaque affirmation importante d'une réponse IA doit pouvoir être reliée à des faits ou signaux autorisés. Les `evidence_refs` servent à auditer les réponses sans exposer les preuves techniques au client.

## Objectif

Spécifier un format de preuve section par section, utilisable par l'audit admin et la validation anti-hallucination.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir la structure d'une référence de preuve.
2. Associer les preuves aux sections narratives.
3. Définir les sources autorisées : faits structurés, signaux interprétatifs, versions de projection.
4. Définir les erreurs de validation.
5. Définir la différence entre preuve technique admin et élément d'appui vulgarisé client.
6. Exiger qu'une `evidence_ref` pointe vers une source validée et hashée, pas seulement vers une chaîne décorative.

## Hors périmètre

- Créer un viewer admin.
- Implémenter un moteur sémantique complet.
- Exposer les preuves techniques aux clients.
- Modifier les calculs astrologiques.

## Critères d'acceptation

1. `evidence_refs` est documenté comme contrat versionné.
2. Chaque section auditée peut porter ses preuves.
3. Les sources de preuves sont contrôlées.
4. Une preuve manquante peut déclencher un statut non fondé.
5. Une `evidence_ref` sans source validée et hashée est invalide.
6. Les preuves client restent vulgarisées si exposées.

## Validation attendue

```powershell
rg -n "evidence_refs|preuve|section|grounding|hash|source validée|vulgarisé|admin" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-259 pour l'audit de réponse.
- CS-256 pour les faits structurés.

## Risques

Le risque principal est de créer des références symboliques non vérifiables. Les preuves doivent pointer vers des sources versionnées et hashables.



