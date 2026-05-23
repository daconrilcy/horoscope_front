# CS-227 — Calculation Graph Runner, Cache & Provenance

## Résumé

CS-227 introduit un runner topologique minimal pour exécuter un graphe de calcul déclaratif avec cache, provenance et erreurs explicites.

Après CS-225 et CS-226, le runtime sait décrire un graphe. Il doit maintenant pouvoir exécuter un graphe limité sans que chaque orchestrateur métier reconstruise manuellement l’ordre des appels.

La cible est volontairement conservatrice :

```text
definition + initial context + registry de calculateurs
→ validation
→ ordre topologique
→ exécution node par node
→ CalculationGraphExecutionResult
```

CS-227 ne migre pas encore le pipeline natal complet. Elle fournit le mécanisme d’exécution qui sera utilisé par CS-228.

---

## Contexte

Le besoin de graphe vient du fait que les futures techniques astrologiques vont composer des calculs existants :

- un transit réutilise un thème natal, des positions courantes, des aspects inter-chart ;
- une synastrie compose deux graphes nataux et un graphe d’aspects relationnels ;
- une profection réutilise maisons, annual lord, chronocrators et période ;
- un return réutilise recherche temporelle, thème événementiel et comparaison au natal ;
- une progression demande des positions dérivées et des aspects au natal.

Pour éviter un service principal géant, l’exécution doit être séparée de la définition.

---

## Objectifs

### Objectif fonctionnel

Créer un runner capable d’exécuter un graphe déclaratif simple.

Exemple cible :

```python
result = CalculationGraphRunner(registry).run(
    definition=definition,
    initial_context=CalculationGraphContext.from_values(
        julian_day=2451545.0,
        coordinates=coords,
        house_system="placidus",
    ),
)
```

Le résultat doit exposer :

```text
outputs
node_results
execution_order
cache_hits
provenance
errors
```

### Objectif architectural

Faire du runner une infrastructure de domaine pure :

- pas de FastAPI ;
- pas de DB ;
- pas de thread pool ;
- pas de LLM ;
- pas de dépendance au thème natal ;
- pas d’import dynamique magique.

Les calculateurs sont fournis explicitement par un registry.

---

## Périmètre inclus

CS-227 couvre :

1. La création de `CalculationGraphRunner`.
2. La création de `CalculationGraphContext`.
3. La création de `CalculationNodeResult`.
4. La création de `CalculationGraphExecutionResult`.
5. Un registry explicite de calculateurs.
6. Un cache en mémoire pour une exécution.
7. La provenance minimale : node, inputs consommés, output produit, calculator code.
8. La gestion des erreurs de dépendance manquante.
9. La gestion des erreurs de calculateur inconnu.
10. Les tests unitaires sur un graphe factice.

---

## Hors périmètre

CS-227 ne doit pas :

- migrer `build_natal_result` ;
- ajouter un cache persistant ;
- paralléliser les nodes ;
- appeler des APIs externes ;
- gérer des retries ;
- ajouter des métriques production ;
- ajouter un moteur de workflow généraliste ;
- ajouter Celery, Prefect, Airflow, networkx ou autre dépendance externe ;
- modifier les calculateurs astrologiques existants.

---

## Contrats attendus

### `CalculationGraphContext`

```python
@dataclass(frozen=True, slots=True)
class CalculationGraphContext:
    values: Mapping[str, object]

    def get_required(self, key: str) -> object:
        ...
```

Règle : le runner ne doit pas muter le contexte initial. Chaque output produit un nouveau contexte interne ou une copie contrôlée.

### `CalculationNodeCallable`

Type recommandé :

```python
CalculationNodeCallable = Callable[[CalculationGraphContext], object]
```

Option plus stricte autorisée :

```python
class CalculationNodeExecutor(Protocol):
    def execute(self, context: CalculationGraphContext) -> object:
        ...
```

### `CalculationNodeResult`

```python
@dataclass(frozen=True, slots=True)
class CalculationNodeResult:
    node_code: str
    output_key: str
    status: CalculationNodeStatus
    input_keys: tuple[str, ...]
    calculator: str
    cache_hit: bool = False
    error: str | None = None
```

### `CalculationGraphExecutionResult`

```python
@dataclass(frozen=True, slots=True)
class CalculationGraphExecutionResult:
    graph_code: str
    success: bool
    outputs: Mapping[str, object]
    node_results: tuple[CalculationNodeResult, ...]
    execution_order: tuple[str, ...]
    errors: tuple[CalculationGraphExecutionError, ...] = ()
```

---

## Règles d’exécution

### Validation avant exécution

Le runner doit appeler le validator CS-225 avant tout calcul.

Si le graphe est invalide :

```text
success=False
aucun calculateur exécuté
errors contient les erreurs de validation
```

### Registry explicite

Interdit :

```python
importlib.import_module(node.calculator)
eval(node.calculator)
globals()[node.calculator]
```

Autorisé :

```python
registry = CalculationNodeRegistry(
    calculators={
        "houses_runtime_builder": calculate_houses_node,
    }
)
```

### Cache d’exécution

Le cache est limité à une exécution :

- si un output existe déjà dans le contexte initial, le node peut être marqué `cache_hit=True` et ne pas être recalculé ;
- si deux nodes produisent le même output, le validator doit déjà l’avoir refusé ;
- aucun cache global ne doit être ajouté.

### Erreurs explicites

Exemples :

```text
Calculation node 'houses_runtime' cannot run: missing required input 'coordinates'.
Calculation node 'dignities' cannot run: calculator 'dignity_runtime_node' is not registered.
Calculation node 'dominance' failed: ValueError: ...
```

La trace Python complète peut rester loggée ailleurs, mais le résultat runtime doit porter un message stable et testable.

---

## Tests attendus

1. Exécution d’un graphe linéaire A -> B -> C.
2. Exécution d’un graphe avec deux branches convergentes.
3. Ordre topologique déterministe.
4. Le runner refuse un graphe invalide sans exécuter les calculateurs.
5. Erreur si un calculateur n’est pas enregistré.
6. Erreur si un input requis est absent.
7. Cache hit si un output est déjà présent.
8. Le contexte initial n’est pas muté.
9. La provenance liste inputs, output et calculator pour chaque node.
10. Aucune importation dynamique n’est utilisée.

---

## Critères d’acceptation

La story est acceptée si :

1. Le runner exécute un graphe valide en ordre topologique.
2. Les calculateurs sont résolus uniquement via registry explicite.
3. Les outputs sont collectés dans `CalculationGraphExecutionResult`.
4. Les erreurs sont explicites et testées.
5. Le cache reste local à l’exécution.
6. La provenance minimale est disponible.
7. Aucun calcul astrologique existant n’est modifié.
8. Aucun changement API, DB ou frontend n’est introduit.

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
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Scans anti-régression :

```powershell
rg -n "importlib|eval\\(|globals\\(\\)|locals\\(\\)" backend/app/domain/astrology/runtime -g "*.py"
rg -n "networkx|prefect|airflow|celery" backend/app backend/tests -g "*.py"
```

---

## Évidence finale attendue

```markdown
## CS-227 Final Evidence

### Runner
- Added CalculationGraphRunner.
- Added explicit calculator registry.
- Runner validates graph before execution.

### Execution
- Topological execution is deterministic.
- Outputs and node results are returned.
- Missing inputs and unknown calculators fail explicitly.

### Cache & Provenance
- Execution-local cache is supported.
- Node provenance includes inputs, output and calculator code.
- Initial context is not mutated.

### Scope
- No natal migration yet.
- No API, DB or frontend changes.
- No dynamic imports or external workflow dependency.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted runner tests
```

---

## Formulation courte pour Codex

```markdown
Implémente CS-227 — Calculation Graph Runner, Cache & Provenance.

Objectif:
Créer un runner topologique minimal pour exécuter les graphes déclaratifs CS-225/CS-226 avec registry explicite, cache local et provenance.

À faire:
- Ajouter CalculationGraphContext.
- Ajouter CalculationGraphRunner.
- Ajouter CalculationNodeRegistry.
- Ajouter CalculationNodeResult et CalculationGraphExecutionResult.
- Exécuter en ordre topologique après validation.
- Gérer erreurs de graph invalide, input manquant, calculator absent et exception node.
- Ajouter tests unitaires avec graphes factices.

Interdictions:
- Pas de migration build_natal_result.
- Pas de cache persistant.
- Pas de parallélisation.
- Pas d’import dynamique.
- Pas de dépendance externe workflow/graph.

Validation:
- ruff format .
- ruff check .
- pytest -q
- tests ciblés calculation graph runner.
```
