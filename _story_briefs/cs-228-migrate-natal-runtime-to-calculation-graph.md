# CS-228 — Migrate Natal Runtime to Calculation Graph

## Résumé

CS-228 migre progressivement le runtime natal vers le calculation graph.

Après CS-225 à CS-227, le backend dispose de contrats, d’une définition de graphe natal et d’un runner. CS-228 branche l’exécution du thème natal sur ce mécanisme, en gardant le comportement public stable.

Le but n’est pas de réécrire toute l’astrologie. Le but est d’extraire l’orchestration du service principal afin que les futurs domaines, comme transits, synastrie, profections, directions, progressions et returns, puissent composer des graphes au lieu d’empiler de nouvelles séquences procédurales.

---

## Contexte

`build_natal_result` orchestre aujourd’hui de nombreuses étapes :

```text
préparation date/lieu
positions planétaires
points astraux
maisons
signes runtime
chart_objects
positions en maison
rulerships
étoiles fixes
aspects
conditions avancées
dignités
dominance
signature
projections historiques
NatalResult
```

L’ordre exact est devenu une connaissance implicite. CS-228 doit déplacer cette connaissance dans `natal_chart_v1` et utiliser le runner pour produire les outputs canoniques.

---

## Objectifs

### Objectif fonctionnel

Faire produire `build_natal_result` par le graphe de calcul natal, ou par une façade qui délègue les étapes majeures au runner.

Résultat attendu :

```python
result = build_natal_result(...)
assert isinstance(result, NatalResult)
assert result.chart_objects
assert result.houses
assert result.aspects
```

Les sorties publiques doivent rester compatibles.

### Objectif architectural

Réduire le rôle de `natal_calculation.py` :

```text
avant: orchestration complète + calculs + projections
après: préparation des inputs + appel du graphe + assemblage compatible
```

Le service principal ne doit plus grossir à chaque nouvelle technique.

---

## Périmètre inclus

CS-228 couvre :

1. La création d’adapters de nodes pour les calculateurs natals existants.
2. Le branchement du runner sur `natal_chart_v1`.
3. La production des outputs canoniques nécessaires à `NatalResult`.
4. La conservation des projections historiques.
5. La comparaison de non-régression entre ancien chemin et nouveau chemin si un legacy path temporaire est gardé.
6. Le traitement explicite des erreurs de node.
7. Les tests d’intégration du thème natal.
8. Les tests d’architecture empêchant l’ajout de nouvelles étapes procédurales dans `build_natal_result`.

---

## Hors périmètre

CS-228 ne doit pas :

- changer les contrats API publics ;
- changer le frontend ;
- supprimer brutalement les champs historiques de `NatalResult`;
- ajouter transits, synastrie, progressions, directions, returns ou profections ;
- changer la doctrine astrologique ;
- changer les scores ;
- ajouter une persistance du graphe ;
- paralléliser les calculs ;
- introduire un feature flag permanent non justifié.

---

## Stratégie de migration recommandée

### Étape 1 : adapters de nodes

Créer des fonctions de node fines qui adaptent les calculateurs existants :

```python
def calculate_houses_runtime_node(context: CalculationGraphContext) -> tuple[HouseRuntimeData, ...]:
    ...
```

Ces adapters :

- lisent leurs inputs depuis `CalculationGraphContext`;
- appellent les fonctions existantes ;
- retournent un output unique ;
- ne mutent pas le contexte ;
- ne contiennent pas de logique métier dupliquée.

### Étape 2 : registry natal

Créer un registry dédié :

```python
def build_natal_calculation_node_registry() -> CalculationNodeRegistry:
    ...
```

Le registry mappe les codes de calculateurs déclarés dans CS-226 vers les adapters.

### Étape 3 : assemblage `NatalResult`

Créer ou isoler un assembler :

```python
class NatalResultAssembler:
    def assemble(self, execution_result: CalculationGraphExecutionResult) -> NatalResult:
        ...
```

Responsabilités :

- lire les outputs canoniques ;
- construire les projections historiques ;
- préserver les exclusions schema public de `chart_objects` ;
- centraliser les erreurs d’output manquant.

### Étape 4 : retrait contrôlé de l’orchestration procédurale

`build_natal_result` doit devenir mince :

```text
validate inputs
build initial context
run natal graph
assemble NatalResult
```

Si un legacy path temporaire est nécessaire, il doit être :

- privé ;
- documenté ;
- testé en comparaison ;
- assorti d’une date ou story de suppression.

---

## Règles de dépendances

### Interdiction de duplication

Les adapters ne doivent pas recopier les calculs existants.

Interdit :

```python
def calculate_aspects_node(context):
    # nouvelle implémentation locale de l’algorithme d’aspects
```

Autorisé :

```python
def calculate_aspects_node(context):
    return existing_aspect_calculator(...)
```

### Surface canonique

Les nodes calculatoires doivent consommer :

- inputs du contexte ;
- outputs canoniques du graphe ;
- `chart_objects` enrichis quand pertinent.

Ils ne doivent pas consommer une projection legacy comme source de vérité.

### Erreurs

Une erreur de node doit être remontée sous forme contrôlée :

```text
Natal calculation graph failed at node 'houses_runtime': ...
```

Ne pas masquer les erreurs en retournant un résultat partiel silencieux.

---

## Tests attendus

1. `build_natal_result` produit un `NatalResult` complet via le graph runner.
2. `chart_objects` reste présent en interne et absent du JSON public.
3. Les maisons, aspects, dignités, dominance et étoiles fixes restent cohérents.
4. Les projections historiques restent présentes.
5. Une erreur de node est propagée avec le code de node.
6. Les adapters appellent les calculateurs existants sans dupliquer la logique.
7. `build_natal_result` ne contient plus une longue séquence d’orchestration métier.
8. Le graphe exécuté correspond à `natal_chart_v1`.
9. Les tests golden existants restent verts.
10. Aucun changement OpenAPI involontaire.

---

## Critères d’acceptation

La story est acceptée si :

1. `build_natal_result` utilise le calculation graph runner.
2. Les nodes natals sont résolus via un registry explicite.
3. Les résultats publics restent compatibles.
4. `chart_objects` reste la source runtime canonique interne.
5. Les projections legacy ne deviennent pas des dépendances calculatoires.
6. Les erreurs de node sont explicites.
7. Les tests unitaires, intégration et architecture passent.
8. Aucun changement API, DB ou frontend n’est introduit.

---

## Fichiers probablement concernés

À ajuster selon l’arborescence réelle :

```text
backend/app/domain/astrology/natal_calculation.py
backend/app/domain/astrology/runtime/natal_calculation_graph.py
backend/app/domain/astrology/runtime/calculation_graph_runner.py
backend/app/domain/astrology/runtime/natal_calculation_nodes.py
backend/app/domain/astrology/runtime/natal_calculation_registry.py
backend/app/domain/astrology/runtime/natal_result_assembler.py
backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py
backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
backend/tests/unit/domain/astrology/test_natal_result_contract.py
backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
backend/tests/integration/astrology/
```

Recherche initiale :

```powershell
rg -n "def build_natal_result|chart_objects =|FixedStarConjunctionCalculator|DignityPayloadEnricher|DominancePayloadEnricher|ChartSignatureCalculator" backend/app/domain/astrology/natal_calculation.py
```

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
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py
```

Scans anti-régression :

```powershell
rg -n "natal_result\\.planet_positions|natal_result\\.dignity_results|natal_result\\.advanced_conditions" backend/app/domain/astrology/runtime backend/app/domain/astrology/natal_calculation.py -g "*.py"
rg -n "FixedStarConjunctionCalculator\\(|DignityPayloadEnricher\\(|DominancePayloadEnricher\\(" backend/app/domain/astrology/natal_calculation.py
rg -n "chart_objects" backend/app/api frontend/src
```

Les hits doivent être vides, documentés ou limités à l’assemblage/projection autorisé.

---

## Évidence finale attendue

```markdown
## CS-228 Final Evidence

### Graph Execution
- build_natal_result uses natal_chart_v1 through CalculationGraphRunner.
- Natal node registry is explicit.
- Node adapters reuse existing calculators.

### Runtime Outputs
- chart_objects remains canonical internal runtime.
- Houses, aspects, dignities, dominance, fixed stars and signature are produced through graph outputs.
- Legacy projections remain available.

### Compatibility
- No public API or OpenAPI delta.
- chart_objects remains excluded from public JSON.
- Existing golden/integration tests pass.

### Guardrails
- No new procedural orchestration sequence in build_natal_result.
- No calculator depends on legacy projections as source of truth.
- Node failures include node code.

### Commands
- ruff format .
- ruff check .
- pytest -q
- targeted graph/natal tests
```

---

## Risques à surveiller

Le premier risque est de migrer trop gros d’un coup. Si nécessaire, CS-228 peut brancher un sous-graphe natal cohérent, mais elle doit alors documenter précisément ce qui reste procédural et créer une story de fermeture.

Le deuxième risque est de dupliquer les calculateurs dans les node adapters. Les adapters doivent être minces.

Le troisième risque est de conserver deux chemins actifs sans preuve de convergence. Un legacy path temporaire doit être prouvé, borné et testé.

Le quatrième risque est de casser le contrat public. `chart_objects` doit rester interne tant qu’une story API dédiée n’autorise pas son exposition.

---

## Formulation courte pour Codex

```markdown
Implémente CS-228 — Migrate Natal Runtime to Calculation Graph.

Objectif:
Faire exécuter le pipeline natal par le CalculationGraphRunner et la définition `natal_chart_v1`, en conservant le comportement public existant.

À faire:
- Créer les adapters de nodes natals.
- Créer build_natal_calculation_node_registry.
- Brancher build_natal_result sur CalculationGraphRunner.
- Ajouter un assembler NatalResult si nécessaire.
- Préserver chart_objects interne et projections historiques.
- Ajouter tests unitaires, intégration et architecture.
- Vérifier absence de delta OpenAPI/public JSON.

Interdictions:
- Pas de changement API/front/DB.
- Pas de nouvelle doctrine astrologique.
- Pas de duplication des calculateurs.
- Pas de dépendance calculatoire aux projections legacy.
- Pas de legacy path permanent non justifié.

Validation:
- ruff format .
- ruff check .
- pytest -q
- tests ciblés graph/natal.
- scans anti-régression sur orchestration procédurale et surfaces legacy.
```
