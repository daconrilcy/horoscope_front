# CS-248 — Add Calculation Graph Execution Trace Contract

## Résumé

Définir le contrat de trace d'exécution du graphe de calcul afin de distinguer clairement trace, provenance et replay.

Cette story remappe `SC-ARCH-003`.

## Contexte

CS-245 identifie un manque d'observabilité stable pour les graphes. Le runner peut exécuter et produire de la provenance, mais la plateforme a besoin d'un contrat de trace redacted qui explique ce qui s'est passé sans exposer le runtime brut au public.

## Objectif

Créer une trace interne versionnée qui couvre :

- graph code et version ;
- run id ou correlation id interne ;
- ordre des nodes ;
- statut de chaque node ;
- durée ou métrique technique non sensible ;
- inputs déclarés sans payload brut sensible ;
- outputs référencés sans dump complet ;
- cache hit/miss si disponible ;
- erreurs normalisées ;
- références de provenance.

## Périmètre inclus

1. Définir les types de trace.
2. Brancher le runner pour produire la trace en succès, échec et cache.
3. Redacter les données sensibles ou volumineuses.
4. Ajouter des tests succès, erreur, cache et absence d'exposition brute.
5. Documenter la différence entre `trace`, `provenance` et `replay snapshot`.

## Hors périmètre

- Exposer la trace via une route publique.
- Créer une UI admin.
- Persister les traces sans décision explicite.
- Transformer la trace en replay complet.
- Modifier le frontend.

## Contrat attendu

La trace doit être stable et limitée :

```text
execution_trace.version
execution_trace.graph_code
execution_trace.graph_version
execution_trace.nodes[].code
execution_trace.nodes[].status
execution_trace.nodes[].cache_status
execution_trace.nodes[].input_keys
execution_trace.nodes[].output_keys
execution_trace.nodes[].error_kind
execution_trace.redaction_policy
```

## Critères d'acceptation

1. Un run réussi produit une trace ordonnée.
2. Un échec de node produit une trace exploitable sans payload brut.
3. Les cache hits sont visibles sans exposer les valeurs cachées.
4. Les termes `trace`, `provenance` et `replay` sont distincts dans le contrat.
5. Les tests vérifient qu'aucune projection publique brute n'est ajoutée.
6. La trace reste interne par défaut.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les tests ciblés du runner et des contrats de trace.

## Dépendances

- CS-246 pour le registre de familles.
- CS-247 pour les manifestes et schémas IO.

## Risques

Le risque principal est de confondre debug interne et surface produit. Toute exposition admin ou persistence durable doit être une story séparée avec politique de rétention.
