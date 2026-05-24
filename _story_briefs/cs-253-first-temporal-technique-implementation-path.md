# CS-253 — Select First Temporal Technique Implementation Path

## Résumé

Sélectionner le premier chemin d'implémentation d'une technique temporelle, sans l'ouvrir tant que la preuve astronomique CS-250 n'est pas terminée ou explicitement risk-accepted.

Cette story remappe `SC-ARCH-006`.

## Gate obligatoire

CS-253 ne doit pas démarrer comme implémentation publique si CS-250 n'est pas `done` ou si une risk acceptance produit écrite n'autorise pas une expérimentation non publique.

## Contexte

CS-245 classe les familles temporelles comme prochaines extensions possibles : transits, synastrie, returns, progressions, composite, profections et forecasting. Le registre doit éviter une implémentation opportuniste qui contourne `CalculationGraph`, les `chart_objects` ou la preuve astronomique.

## Objectif

Décider et cadrer une seule première technique temporelle :

- famille choisie ;
- justification produit ;
- inputs requis ;
- graphe requis ;
- objets et relations requis ;
- projection publique ou non publique ;
- dépendances de preuve astronomique ;
- critères de fin.

## Périmètre inclus

1. Comparer les candidates temporelles.
2. Sélectionner une technique ou documenter le blocage.
3. Définir le chemin d'implémentation minimal.
4. Refuser le batch multi-techniques.
5. S'appuyer sur le registre CS-246 et les manifestes CS-247.
6. Produire les tests/scans attendus pour prouver qu'une seule famille est ouverte.

## Hors périmètre

- Implémenter toutes les techniques.
- Ouvrir une API ou UI publique sans contrat produit.
- Contourner CS-250.
- Ajouter une narration LLM.

## Critères d'acceptation

1. La technique choisie est unique.
2. Les raisons de non-sélection des autres familles sont documentées.
3. Les inputs multi-date, multi-chart ou relationnels sont explicites.
4. Le blocage CS-250 est respecté.
5. Les tests ou scans prouvent qu'aucune famille temporelle non choisie n'est implémentée par opportunisme.
6. Si la story implémente un premier squelette, il reste non public tant que les gates ne sont pas fermés.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les tests ciblés de sélection ou de squelette selon le scope final retenu.

## Dépendances

- CS-250 obligatoire sauf risk acceptance.
- CS-246, CS-247 et CS-248 recommandées avant tout runtime temporel réel.
- CS-251 si une projection publique est envisagée.

## Risques

Le risque principal est de faire entrer une technique temporelle par le code avant que le produit et l'astronomie soient prêts. La story doit s'arrêter sur un blocage propre plutôt que de contourner le gate.
