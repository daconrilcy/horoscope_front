# CS-255 — Archi Synthèse De L'Architecture Produit En Place

## Résumé

Produire une synthèse d'architecture produit de l'état réellement en place après la livraison CS-237 à CS-254.

Cette story part du rapport d'implémentation `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md` et consolide, en un document lisible, les décisions, primitives, contrats, garde-fous, limites et prochaines décisions produit/techniques.

## Contexte

La séquence CS-237 à CS-254 a livré :

- des audits de couverture, exposition runtime, payloads, gouvernance, précision astronomique, readiness graph et besoins produit ;
- une architecture de transition canonique autour de `ChartObjectRuntimeData` et `CalculationGraph` ;
- des implémentations backend de registry, manifest, trace, taxonomie, preuve astronomique, gouvernance doctrinale, sélection temporelle et contrat d'entrée IA/narration ;
- une roadmap de primitives produit publiques sans exposition brute des surfaces internes.

Le besoin actuel est de rendre cette architecture compréhensible comme architecture produit en place, pour guider les stories suivantes sans relire tous les audits, stories et fichiers d'évidence.

## Objectif

Créer un document de synthèse qui explique l'architecture produit actuelle, ses frontières et ses décisions structurantes.

Le document doit répondre clairement à :

- quelles primitives internes sont désormais canoniques ;
- quelles surfaces sont publiques, internes, admin/debug ou LLM-only ;
- comment le calcul, l'interprétation, la narration IA et les projections produit sont séparés ;
- quelles familles astrologiques sont prêtes, sélectionnées, bloquées ou seulement cadrées ;
- quels garde-fous empêchent l'exposition brute ou l'inversion des dépendances ;
- quelles décisions produit/doctrine/sécurité restent ouvertes.

## Livrable attendu

Créer un document sous :

```text
docs/architecture/product-architecture-current-state.md
```

Le document doit être une synthèse d'architecture produit, pas une répétition exhaustive du delivery report.

## Sources obligatoires

La story doit lire et citer explicitement :

- `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md`
- `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- les fichiers `generated/10-final-evidence.md` de CS-246 à CS-254 quand une assertion d'implémentation ou de validation est reprise.

## Structure attendue

Le document doit contenir au minimum :

1. `Résumé exécutif`
2. `Architecture produit en place`
3. `Primitives canoniques internes`
4. `Surfaces produit et niveaux d'exposition`
5. `Frontières calcul / interprétation / narration`
6. `Familles astrologiques et statut produit`
7. `Garde-fous et validations`
8. `Limites et décisions ouvertes`
9. `Prochaines stories recommandées`

## Périmètre inclus

1. Synthétiser les décisions livrées par CS-237 à CS-254.
2. Cartographier les primitives internes : registry, graph manifest, trace, taxonomy, astronomical proof, doctrine governance, temporal selection, AI narrative input contract.
3. Cartographier les projections produit autorisées et les surfaces interdites en public.
4. Décrire les dépendances directionnelles attendues : calcul -> faits -> signaux -> narration/projection.
5. Identifier les limites résiduelles : fixed stars, debug astrologue, runtime temporel public, preuve ephemeris, gouvernance doctrine.
6. Proposer les prochaines stories prioritaires à partir des risques résiduels du rapport.
7. Ajouter des références précises vers les fichiers sources.

## Hors périmètre

- Modifier le backend applicatif.
- Modifier le frontend.
- Ajouter un endpoint, serializer, route ou contrat OpenAPI.
- Ajouter une migration, seed ou donnée de référence.
- Implémenter une projection publique.
- Décider à la place du produit une politique `fixed_star_contacts` ou `astrologer_debug_data`.
- Réécrire les audits ou le rapport de livraison.

## Critères d'acceptation

1. `docs/architecture/product-architecture-current-state.md` existe.
2. Le document cite le rapport d'implémentation CS-237..CS-254 comme source principale.
3. Les primitives internes canoniques livrées par CS-246 à CS-254 sont toutes mentionnées avec leur rôle.
4. Les surfaces publiques, internes, admin/debug et LLM-only sont séparées explicitement.
5. `ChartObjectRuntimeData`, `chart_objects` et les traces brutes ne sont jamais présentés comme API publiques.
6. La frontière calcul / interprétation / narration est expliquée avec le sens de dépendance autorisé.
7. Les familles `natal_chart_v1` et `transit_chart_v1` sont distinguées entre runtime en place, chemin sélectionné et exposition publique non encore livrée.
8. Les décisions ouvertes du rapport sont reprises sans les résoudre artificiellement.
9. Les prochaines stories recommandées sont formulées comme actions concrètes et dépendantes des décisions restantes.
10. Aucun fichier applicatif n'est modifié.

## Validation attendue

Validation documentaire :

```powershell
Test-Path .\docs\architecture\product-architecture-current-state.md
rg -n "CS-237|CS-254|ChartObjectRuntimeData|CalculationGraph|structured_facts|beginner_summary|expert_technical_projection|llm_input" .\docs\architecture\product-architecture-current-state.md
rg -n "interne|publique|admin|debug|LLM|narration|interprétation|calcul" .\docs\architecture\product-architecture-current-state.md
rg -n "fixed_star_contacts|astrologer_debug_data|transit_chart_v1|needs-user-decision" .\docs\architecture\product-architecture-current-state.md
```

Validation de non-modification applicative :

```powershell
git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations
```

## Dépendances

- CS-237 à CS-244 pour les constats d'audit.
- CS-245 pour l'architecture de transition canonique.
- CS-246 à CS-254 pour les primitives backend et contrats réellement livrés.
- `docs/architecture/official-product-primitives-public-projections.md` pour les projections produit officielles.

## Risques

Le risque principal est de produire un document trop narratif qui mélange architecture cible et état livré. La synthèse doit distinguer strictement :

- ce qui est déjà en place ;
- ce qui est seulement cadré ;
- ce qui est bloqué par décision produit, doctrine ou sécurité ;
- ce qui ne doit pas être exposé publiquement.

## Formulation courte pour Codex

```markdown
Réalise CS-255.

À partir de `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`, crée `docs/architecture/product-architecture-current-state.md`.

Le document doit synthétiser l'architecture produit actuellement en place après CS-237 à CS-254 : primitives internes, surfaces publiques/interne/admin/LLM, frontière calcul/interprétation/narration, familles astrologiques, garde-fous, limites et prochaines décisions.

Interdictions :
- pas de modification backend ;
- pas de modification frontend ;
- pas d'endpoint ;
- pas de migration ;
- pas d'exposition brute de `ChartObjectRuntimeData`, `chart_objects` ou traces internes ;
- ne pas résoudre artificiellement les décisions `needs-user-decision`.
```
