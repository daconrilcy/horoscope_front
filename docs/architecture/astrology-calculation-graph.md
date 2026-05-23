# Graphe de calcul astrologique

Ce document borne le modele CS-225. Le `calculation graph` est une surface
technique declarative: il nomme les entrees, les sorties et les dependances des
calculs du runtime astrologique. Il n'execute aucun calcul astrologique et
n'importe pas de fonction calculatrice.

## Frontieres

Le `calculation graph` orchestre des dependances futures comme
`julian_day -> houses_runtime -> house_rulerships_runtime`. Son objectif est de
rendre l'ordre de calcul inspectable avant l'arrivee d'un runner topologique.

L'`astrological graph` est different: il represente des relations metier entre
objets astrologiques, par exemple `occupies`, `rules` ou `aspects`. Les contrats
`AstrologicalGraphNodeType` et `AstrologicalGraphEdgeType` restent donc separes.

`chart_objects` reste la surface runtime canonique des objets exploitables du
theme natal. Un futur node pourra consommer `chart_objects`, mais CS-225 ne
remplace ni `NatalResult.chart_objects`, ni les payloads de maisons, maitrises,
aspects, dignites, dominance, mouvement, visibilite ou etoiles fixes.

## Contrats

Un graphe declare:

- `CalculationInputDefinition` pour les entrees disponibles;
- `CalculationNodeDefinition` pour un calcul, sa sortie et ses dependances;
- `CalculationGraphDefinition` pour nommer le graphe et sa version;
- `CalculationGraphValidationResult` pour restituer erreurs et ordre theorique.

Le champ `calculator` est un identifiant stable. Il n'est pas un import dynamique
et ne declenche aucune execution.

## Validation

Le validator CS-225 detecte les champs obligatoires vides, les doublons de
nodes, les doublons de sorties, les dependances obligatoires inconnues et les
cycles directs ou indirects.

Les dependances optionnelles peuvent viser une sortie absente sans rendre le
graphe invalide. Quand une dependance optionnelle vise une sortie declaree, elle
participe a l'ordre topologique theorique.

## Hors scope

CS-225 ne migre pas `build_natal_result`, ne change pas l'API publique, ne cree
pas de migration DB, ne modifie pas le frontend et n'ajoute aucune dependance de
graph processing.
