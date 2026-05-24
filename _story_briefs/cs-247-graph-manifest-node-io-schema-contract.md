# CS-247 — Add Graph Manifest And Node IO Schema Contract

## Résumé

Ajouter un manifeste de graphe et un contrat de schéma d'entrées/sorties par node pour rendre `CalculationGraph` inspectable, comparable et prêt pour les familles non natales.

Cette story remappe `SC-ARCH-002`.

## Contexte

CS-225 à CS-228 ont introduit les contrats et l'exécution du graphe natal. CS-245 montre qu'il manque encore un manifeste stable et une description des IO de nodes. Sans ce contrat, les graphes futurs peuvent être exécutables mais difficiles à auditer, comparer ou exposer en debug contrôlé.

## Objectif

Définir un contrat interne décrivant :

- l'identité du graphe ;
- sa version ;
- ses inputs globaux ;
- les nodes déclarés ;
- les entrées consommées par chaque node ;
- les sorties produites ;
- les types ou familles de types attendus ;
- les dépendances optionnelles ;
- la politique de compatibilité.

## Périmètre inclus

1. Créer le modèle de manifeste de graphe.
2. Créer le contrat de node IO schema.
3. Brancher `natal_chart_v1` sur un manifeste complet.
4. Valider que chaque node du graphe natal déclare ses inputs et outputs.
5. Prévoir la comparaison de manifestes pour détecter les changements contractuels.
6. Ajouter les tests de validation, doublons, références manquantes et compatibilité.

## Hors périmètre

- Changer l'API publique.
- Ajouter une UI de debug.
- Persister les manifestes en DB.
- Implémenter un moteur temporel.
- Choisir un langage externe de schéma sans nécessité.

## Contrat attendu

Le manifeste doit être lisible par les tests et par de futures stories d'audit :

```text
graph_code
graph_version
family_code
required_inputs
nodes[].code
nodes[].input_schema
nodes[].output_schema
nodes[].depends_on
compatibility_policy
```

Les types peuvent être descriptifs si le runtime actuel ne dispose pas d'un modèle de typage complet, mais ils doivent être stables et validés.

## Critères d'acceptation

1. `natal_chart_v1` possède un manifeste validé.
2. Chaque node a un contrat d'entrée et de sortie.
3. La validation détecte les outputs dupliqués, inputs inconnus et schémas absents.
4. Les tests couvrent un manifeste valide et plusieurs manifestes invalides.
5. Aucune surface publique brute n'est exposée.
6. Le choix de schéma est documenté dans le code ou dans une note proche du contrat.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les tests ciblés du manifeste et du validateur.

## Dépendances

- CS-246 doit avoir défini les familles de graphes.
- CS-248 consommera ce contrat pour la trace.

## Risques

Le risque principal est de créer un schéma trop théorique. Le manifeste doit décrire le graphe réellement exécuté, puis laisser les extensions temporelles ajouter leurs besoins.
