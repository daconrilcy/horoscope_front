# CS-225 — Calculation Graph Runtime Contracts

## Résumé

CS-225 introduit le socle contractuel d’un graphe de calcul déclaratif pour le runtime astrologique.

Le pipeline natal est aujourd’hui orchestré procéduralement dans `natal_calculation.py`. Cette approche reste acceptable pour un thème natal simple, mais elle devient fragile dès que le moteur doit supporter des dépendances croisées, des techniques temporelles, les transits, la synastrie, les profections, les directions, les progressions et les returns.

La cible n’est pas encore de remplacer tout le pipeline. CS-225 doit seulement créer les contrats typés permettant de déclarer :

```text
node houses depends on jd, coords, house_system
node house_rulers depends on houses, chart_objects
node signature depends on signs_runtime, houses_runtime, aspects_runtime
```

Le graphe doit rendre les dépendances explicites, testables et inspectables avant toute migration large.

---

## Contexte

Les stories CS-217 à CS-224 ont fait converger le runtime vers `NatalResult.chart_objects` et des payloads spécialisés : aspects, motion/visibility, dignités, dominance, maisons, rulerships et étoiles fixes.

Il reste cependant un manque structurel : les dépendances entre calculs sont implicites dans l’ordre du code.

Exemples actuels ou attendus :

- les maisons dépendent du jour julien, des coordonnées et du système de maisons ;
- les positions en maison dépendent des objets du thème et des maisons ;
- les maîtrises dépendent des maisons, signes, référentiels et objets ;
- les dignités dépendent des objets, signes, maisons, secte et conditions avancées ;
- la dominance dépend des objets, aspects, dignités et maisons ;
- la signature dépend des signes runtime, maisons runtime et aspects runtime ;
- la synastrie dépend de deux graphes nataux plus des aspects inter-chart ;
- les transits dépendent d’un thème natal, d’un thème courant et d’un instant de calcul.

Sans représentation déclarative, chaque nouvelle technique risque d’ajouter une séquence procédurale ad hoc dans un service principal.

---

## Objectifs

### Objectif fonctionnel

Créer des contrats runtime pour décrire un graphe de calcul astrologique sans encore exécuter toute l’application via ce graphe.

Exemple cible :

```python
CalculationGraphDefinition(
    graph_code="natal_chart_v1",
    nodes=(
        CalculationNodeDefinition(
            code="houses",
            output_key="houses_runtime",
            depends_on=("julian_day", "coordinates", "house_system"),
            calculator="houses_runtime_builder",
        ),
        CalculationNodeDefinition(
            code="house_rulers",
            output_key="house_rulerships_runtime",
            depends_on=("houses_runtime", "chart_objects"),
            calculator="house_ruler_resolver",
        ),
    ),
)
```

### Objectif architectural

Installer une frontière claire :

```text
contrats de graphe déclaratif
→ validation des dépendances
→ exécution future par runner topologique
```

CS-225 ne doit pas créer un nouveau monolithe. Elle prépare les types et les validations minimales qui permettront aux stories suivantes de déclarer puis d’exécuter des graphes de calcul.

---

## Périmètre inclus

CS-225 couvre :

1. La création de contrats de graphe de calcul.
2. La création de types pour les clés d’entrée, sorties et dépendances.
3. La définition de statuts de node : déclaré, prêt, exécuté, échoué, ignoré.
4. La validation des dépendances manquantes, cycles et doublons.
5. La distinction entre dépendance obligatoire et dépendance optionnelle.
6. La distinction entre donnée d’entrée, résultat calculé et projection de compatibilité.
7. La compatibilité avec les contrats `ChartObjectRuntimeData` existants.
8. Des tests unitaires des contrats et validations.
9. Une documentation courte du modèle de graphe.

---

## Hors périmètre

CS-225 ne doit pas :

- migrer `build_natal_result` vers le graphe ;
- exécuter un graphe complet en production ;
- ajouter des transits, progressions, directions ou synastrie ;
- changer l’API publique ;
- modifier le frontend ;
- ajouter une dépendance externe de graph processing ;
- persister le graphe en base ;
- remplacer les contrats `AstrologicalGraphNodeType` existants liés au graphe astrologique sémantique.

Point important : le graphe de calcul n’est pas le graphe astrologique sémantique. Le premier orchestre des calculs, le second représente des relations astrologiques comme `occupies`, `rules`, `aspects`.

---

## Contrats attendus

### `CalculationGraphDefinition`

```python
@dataclass(frozen=True, slots=True)
class CalculationGraphDefinition:
    graph_code: str
    version: str
    nodes: tuple[CalculationNodeDefinition, ...]
    required_inputs: tuple[CalculationInputDefinition, ...] = ()
```

Responsabilités :

- nommer un graphe stable ;
- porter une version explicite ;
- exposer les nodes dans un ordre déclaratif ;
- permettre une validation indépendante de l’exécution.

### `CalculationNodeDefinition`

```python
@dataclass(frozen=True, slots=True)
class CalculationNodeDefinition:
    code: str
    output_key: str
    depends_on: tuple[str, ...]
    calculator: str
    optional_depends_on: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
```

Règles :

- `code` est unique dans le graphe ;
- `output_key` est unique dans le graphe ;
- `depends_on` référence des inputs ou des outputs de nodes ;
- `calculator` est un identifiant stable, pas une fonction importée dynamiquement dans CS-225.

### `CalculationInputDefinition`

```python
@dataclass(frozen=True, slots=True)
class CalculationInputDefinition:
    key: str
    value_type: str
    required: bool = True
```

Exemples de clés :

```text
julian_day
coordinates
house_system
runtime_reference
zodiac_mode
birth_chart
target_datetime
```

### `CalculationGraphValidationResult`

```python
@dataclass(frozen=True, slots=True)
class CalculationGraphValidationResult:
    graph_code: str
    is_valid: bool
    errors: tuple[CalculationGraphValidationError, ...]
```

Les erreurs doivent être déterministes et explicites :

```text
Calculation node 'house_rulers' depends on unknown key 'houses'.
Calculation graph 'natal_chart_v1' contains a cycle: houses -> signature -> houses.
Calculation graph 'natal_chart_v1' declares duplicate output_key 'chart_objects'.
```

---

## Composants techniques recommandés

### `calculation_graph_contracts.py`

Emplacement recommandé :

```text
backend/app/domain/astrology/runtime/calculation_graph_contracts.py
```

Ce module contient uniquement les dataclasses, enums et erreurs de contrat.

### `calculation_graph_validator.py`

Emplacement recommandé :

```text
backend/app/domain/astrology/runtime/calculation_graph_validator.py
```

Responsabilités :

- vérifier les codes non vides ;
- vérifier les doublons ;
- vérifier les dépendances inconnues ;
- détecter les cycles ;
- produire un ordre topologique théorique sans exécuter les calculateurs.

### Documentation

Emplacement recommandé :

```text
docs/architecture/astrology-calculation-graph.md
```

Le document doit expliquer la différence entre :

- calculation graph : orchestration technique des calculs ;
- astrological graph : représentation métier des objets et relations astrologiques ;
- `chart_objects` : surface runtime canonique des objets du thème.

---

## Tests attendus

1. Un graphe minimal valide avec inputs `julian_day`, `coordinates`, `house_system` et node `houses`.
2. Erreur sur node sans code.
3. Erreur sur output dupliqué.
4. Erreur sur dépendance inconnue.
5. Erreur sur cycle direct.
6. Erreur sur cycle indirect.
7. Support des dépendances optionnelles sans erreur bloquante.
8. Ordre topologique déterministe.
9. Documentation présente et mentionnant calculation graph vs astrological graph.

---

## Critères d’acceptation

La story est acceptée si :

1. Les contrats de graphe de calcul existent.
2. Les nodes déclarent explicitement leurs inputs, outputs et dépendances.
3. Les validations détectent dépendances inconnues, doublons et cycles.
4. Aucune exécution métier n’est introduite dans les contrats.
5. Le graphe de calcul est clairement distingué du graphe astrologique sémantique.
6. Aucun changement d’API, DB ou frontend n’est introduit.
7. Les tests unitaires du validator passent.
8. La documentation d’architecture existe.

---

## Validation technique

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Tests ciblés :

```powershell
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Scans anti-régression :

```powershell
rg -n "networkx|igraph|graphlib" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "CalculationGraphDefinition|CalculationNodeDefinition" backend/app/domain/astrology/runtime backend/tests
```

La première recherche doit confirmer qu’aucune dépendance externe de graphe n’est introduite. `graphlib` standard library peut être accepté uniquement si explicitement justifié ; une implémentation simple locale est préférable au départ.

---

## Évidence finale attendue

```markdown
## CS-225 Final Evidence

### Contracts
- Added calculation graph contracts.
- Added explicit node dependencies and output keys.
- Calculation graph is distinct from astrological graph.

### Validation
- Unknown dependencies are rejected.
- Duplicate nodes and outputs are rejected.
- Cycles are rejected.
- Topological order is deterministic.

### Scope
- No natal pipeline migration yet.
- No API, DB or frontend changes.
- No external graph dependency.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted calculation graph tests
```

---

## Formulation courte pour Codex

```markdown
Implémente CS-225 — Calculation Graph Runtime Contracts.

Objectif:
Créer les contrats et validations d’un graphe de calcul déclaratif pour le runtime astrologique, sans migrer encore le pipeline natal.

À faire:
- Ajouter CalculationGraphDefinition, CalculationNodeDefinition, CalculationInputDefinition.
- Ajouter un validator détectant doublons, dépendances inconnues et cycles.
- Produire un ordre topologique déterministe.
- Documenter la différence calculation graph / astrological graph / chart_objects.
- Ajouter tests unitaires.

Interdictions:
- Pas de migration de build_natal_result.
- Pas de changement API/front/DB.
- Pas de dépendance externe de graphe.
- Pas de calcul astrologique nouveau.

Validation:
- ruff format .
- ruff check .
- pytest -q
- tests ciblés calculation graph.
```
