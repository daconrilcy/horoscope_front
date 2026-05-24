# CS-256 — Define structured_facts_v1 Stable Hashable Fact Projection

## Résumé

Définir `structured_facts_v1` comme projection socle, stable, hashable et non narrative des faits astrologiques.

## Contexte

Après CS-254, le backend calcule des faits, dérive des signaux, puis expose uniquement des projections contrôlées. `structured_facts_v1` doit devenir le socle commun pour les projections client, les projections admin/expert, l'entrée LLM, l'audit des réponses, les `evidence_refs` et les futures projections API.

## Objectif

Formaliser le contrat de `structured_facts_v1` sans en faire une UX client B2C.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir le rôle de `structured_facts_v1`.
2. Lister les familles de faits autorisées : positions, maisons, aspects principaux, dominantes et métadonnées de source.
3. Définir les règles de stabilité et de hash.
4. Définir le lien avec `AINarrativeInputContract`.
5. Définir les exclusions : narration, debug brut, traces runtime, payloads internes.

## Hors périmètre

- Implémenter une projection.
- Exposer une API publique.
- Modifier le frontend.
- Ajouter du contenu narratif LLM.

## Critères d'acceptation

1. Le contrat `structured_facts_v1` est documenté comme projection factuelle stable.
2. La projection est explicitement non narrative.
3. La projection est hashable pour audit IA.
4. Le client B2C n'est pas présenté comme consommateur direct obligatoire.
5. Les primitives internes `ChartObjectRuntimeData`, `chart_objects` et traces brutes restent hors surface publique.

## Validation attendue

```powershell
rg -n "structured_facts_v1|hash|non narrative|ChartObjectRuntimeData|AINarrativeInputContract" .\docs .\_condamad .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-254 pour le contrat d'entrée IA/narration.
- CS-255 pour la synthèse d'architecture produit.

## Risques

Le risque principal est de confondre le socle de faits avec une projection client. Le brief doit maintenir la frontière faits -> signaux -> narration.



