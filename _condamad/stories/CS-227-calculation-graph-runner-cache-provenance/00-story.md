# Story CS-227 calculation-graph-runner-cache-provenance: Executer un graphe de calcul avec cache et provenance
Status: done

## 1. Objective

Creer un runner topologique minimal pour executer un `CalculationGraphDefinition` valide avec un contexte initial, un registry explicite de calculateurs,
un cache limite a l'execution et une provenance inspectable par node.

## 2. Trigger / Source

- Source type: architecture-runtime-runner.
- Source reference: `_story_briefs/cs-227-calculation-graph-runner-cache-provenance.md`.
- Reason for change: CS-225 decrit les contrats de graphe et CS-226 decrit le graphe natal; il manque le mecanisme d'execution pur.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story ajoute un runner backend-domain pur, sans API, DB, frontend, cache persistant ou migration du pipeline natal.

## References

- `_story_briefs/cs-227-calculation-graph-runner-cache-provenance.md`.
- `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md`.
- `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-145|RG-147|RG-148`.

## 3. Domain Boundary

Cette story appartient a un seul domaine:

- Domain: `backend/app/domain/astrology/runtime`.
- In scope:
  - creer `CalculationGraphRunner`;
  - creer `CalculationGraphContext`;
  - creer `CalculationNodeRegistry`;
  - creer `CalculationNodeCallable` ou un protocole equivalent;
  - creer `CalculationNodeResult`;
  - creer `CalculationGraphExecutionResult`;
  - creer `CalculationGraphExecutionError` pour porter les erreurs runtime stables;
  - executer les nodes en ordre topologique valide par `CalculationGraphValidator`;
  - resoudre les calculateurs uniquement depuis un registry explicite;
  - gerer un cache en memoire limite a une execution;
  - exposer la provenance minimale par node: inputs consommes, output produit, calculator code;
  - tester un graphe lineaire, un graphe convergent, le cache, les erreurs et l'absence d'import dynamique.
- Out of scope:
  - migrer `build_natal_result`;
  - brancher le graphe natal en production;
  - ajouter un cache persistant;
  - parallelliser les nodes;
  - appeler une API externe;
  - ajouter retries, metriques production, worker, Celery, Prefect, Airflow, networkx ou autre dependance externe;
  - modifier les calculateurs astrologiques existants;
  - changer une route FastAPI, un schema public, OpenAPI, DB, migration, frontend ou prompt.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas faire d'import dynamique de calculator;
  - ne pas ajouter de fallback ou shim pour executer le pipeline natal;
  - ne pas introduire de calcul astrologique nouveau.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story ajoute une infrastructure backend-domain pure qui execute les contrats de graphe existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: nouveaux contrats runtime d'execution et runner sous le runtime astrologique;
  - autorise: tests unitaires de runner avec calculateurs factices;
  - autorise: evidence de neutralite API via `app.routes`, `app.openapi()` et `TestClient`;
  - interdit: migration de `build_natal_result`, changement API, DB, frontend, cache persistant, orchestration parallele ou dependance externe.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'implementation touche une route publique, une migration DB, le frontend, une dependance externe ou `build_natal_result`.
- Additional validation rules:
  - `CalculationGraphRunner.run()` appelle le validator CS-225 avant tout calcul;
  - un graphe invalide retourne `success=False`, ne lance aucun calculateur et expose les erreurs de validation;
  - l'ordre d'execution vient du `topological_order` valide ou d'une resolution equivalente testee comme deterministe;
  - les calculateurs sont resolus seulement par `CalculationNodeRegistry`;
  - `importlib.import_module`, `eval`, `globals()` et resolution magique de fonctions sont interdits;
  - le contexte initial reste immuable pour l'appelant;
  - un output deja present dans le contexte initial produit un `cache_hit=True` sans recalcul;
  - les erreurs de dependance manquante, calculateur inconnu et calculateur en echec ont des messages stables et testables;
  - la provenance associe chaque node a `node_code`, `input_keys`, `output_key` et `calculator`;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le runner devient le mecanisme canonique d'execution des definitions de graphe de calcul. |
| Baseline Snapshot | yes | Les contrats CS-225 et la definition CS-226 doivent etre connus avant ajout. |
| Ownership Routing | yes | Runner, contrats, registry, tests et pipeline natal ont des proprietaires distincts. |
| Allowlist Exception | yes | Le pipeline procedural et les graphes declaratifs non executes restent autorises hors runner. |
| Contract Shape | yes | Context, registry, resultats de node, resultats d'execution et erreurs sont le coeur de la story. |
| Batch Migration | yes | Contrats d'execution, runner, tests, scans et evidence sont livres par lots controlables. |
| Reintroduction Guard | yes | Les scans bloquent import dynamique, dependances externes et deltas API/DB/front. |
| Persistent Evidence | yes | Tests, scans et preuve finale doivent etre conserves dans le dossier CS-227. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/calculation_graph_runner.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_validator.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py` comme definition consommatrice future non migree.
- Runtime/domain artifacts:
  - context immuable de valeurs;
  - registry explicite de calculateurs;
  - resultats de node avec status, cache et provenance;
  - resultat global d'execution avec outputs, node_results, execution_order, cache_hits, provenance et errors;
  - tests unitaires sous `backend/tests/unit/domain/astrology/`.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `app.routes`, `app.openapi()` et `TestClient` sans delta public volontaire;
  - scans cibles anti-import dynamique et anti-dependance externe.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni l'ordre topologique runtime, ni le cache par execution, ni les messages d'erreur, ni la neutralite OpenAPI.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `Get-Content backend/app/domain/astrology/runtime/calculation_graph_validator.py`;
  - `Get-Content backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - recherche ciblee de `CalculationGraphRunner|CalculationGraphContext|CalculationNodeRegistry`;
  - recherche ciblee de `build_natal_result` dans `backend/app/domain/astrology/services/natal_calculation.py`;
  - `Select-String "RG-144|RG-145|RG-147|RG-148" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-227 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend et pipeline natal.
- Expected invariant:
  - le pipeline natal reste procedural;
  - le graphe natal reste non migre en production;
  - le runner reste pur et synchrone;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - nouveau module `calculation_graph_runner.py`;
  - exports package minimaux si le runtime les utilise deja;
  - tests unitaires et evidence CS-227;
  - Registry gap: un invariant dedie au runner de graphe pourra etre ajoute ulterieurement hors generation normale.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Context d'execution | `calculation_graph_runner.py` | route API, DB, frontend |
| Registry de calculateurs | `calculation_graph_runner.py` | import dynamique, global module lookup |
| Execution topologique | `CalculationGraphRunner` | `natal_calculation.py`, infra, worker externe |
| Validation declarative | `calculation_graph_validator.py` | runner dupliquant toutes les regles CS-225 |
| Definition natal | `natal_calculation_graph.py` | runner ou service monolithique |
| Tests unitaires | `backend/tests/unit/domain/astrology/` | tests API opaques pour logique pure |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `natal_calculation.py` | ordre procedural | Pipeline natal hors migration CS-227. | Temporary; exit condition: CS-228 approved. |
| `natal_calculation_graph.py` | definition declarative | Consommateur futur, non execute en production par CS-227. | Temporary; exit condition: integration story approved. |
| `calculation_graph_validator.py` | validation topologique | Source de validation CS-225 a reutiliser. | Permanent. |
| serializers et routes publics | contrats JSON existants | CS-227 ne change pas l'API publique. | Permanent pour cette story. |

Validation rule:

- Toute resolution de calculator par import dynamique, toute migration de `build_natal_result` ou tout cache global bloque l'implementation CS-227.

## 4f. Contract Shape

- Contract type:
  - dataclasses Python immuables avec `frozen=True` et `slots=True`;
  - callable type ou protocole de calculator;
  - registry explicite;
  - runner pur;
  - aucune nouvelle API HTTP.
- Required dataclasses:
  - `CalculationGraphContext`;
  - `CalculationNodeResult`;
  - `CalculationGraphExecutionResult`;
  - `CalculationGraphExecutionError`.
- Required type or protocol:
  - `CalculationNodeCallable = Callable[[CalculationGraphContext], object]` ou `CalculationNodeExecutor`.
- Required class:
  - `CalculationNodeRegistry`;
  - `CalculationGraphRunner`.
- Fields:
  - `values`;
  - `node_code`;
  - `output_key`;
  - `status`;
  - `input_keys`;
  - `calculator`;
  - `cache_hit`;
  - `error`;
  - `graph_code`;
  - `success`;
  - `outputs`;
  - `node_results`;
  - `execution_order`;
  - `errors`.
- Required fields:
  - `values`;
  - `node_code`;
  - `output_key`;
  - `status`;
  - `input_keys`;
  - `calculator`;
  - `cache_hit`;
  - `error`;
  - `graph_code`;
  - `success`;
  - `outputs`;
  - `node_results`;
  - `execution_order`;
  - `cache_hits`;
  - `provenance`;
  - `errors`.
- Optional fields:
  - `error` may be null for successful nodes;
  - `errors` may be empty for successful executions.
- Required result surfaces:
  - `outputs`;
  - `node_results`;
  - `execution_order`;
  - `cache_hits`;
  - `provenance`;
  - `errors`.
- Required behavior:
  - `CalculationGraphContext.get_required(key)` retourne la valeur ou produit un signal de dependance manquante stable;
  - `CalculationGraphRunner(registry).run(definition, initial_context)` retourne un `CalculationGraphExecutionResult`;
  - le cache ne vit que dans la methode `run`;
  - les outputs produits ne mutent pas le contexte initial.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-227.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | pas de context runtime commun | `CalculationGraphContext` | aucun public | context tests | immutability proof | context mute |
| 2 | calculateurs implicites | `CalculationNodeRegistry` | tests factices | registry tests | no dynamic import | import magique |
| 3 | ordre theorique seulement | `CalculationGraphRunner` | tests factices | runner tests | validator called | ordre instable |
| 4 | recomputation locale | cache par `run` | tests factices | cache tests | no global cache | cache persistant |
| 5 | erreurs dispersees | resultats runtime structures | tests factices | error tests | messages stables | erreur opaque |
| 6 | preuve manuelle API neutre | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route ou schema modifie |

Completion rule: chaque batch conserve `pytest -q`, `app.routes`, `app.openapi()`, l'absence de cache global et le pipeline natal procedural.

## 4h. Reintroduction Guard

- Guard target:
  - aucun `networkx`, `igraph`, `graphlib`, Celery, Prefect, Airflow ou dependance externe de workflow dans le runtime;
  - aucun `importlib.import_module`, `eval`, `globals()` ou lookup magique pour resoudre un calculator;
  - aucun import FastAPI, SQLAlchemy, infra, settings, LLM ou frontend dans le runner;
  - aucun changement volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucune mutation de `build_natal_result` pour executer le graphe;
  - aucun cache global, singleton mutable ou stockage persistant de resultats de node.
- Guard mechanism:
  - tests unitaires du runner;
  - tests unitaires du validator CS-225;
  - AST guard ou scans cibles sur imports et lookup interdits;
  - `TestClient` smoke sur OpenAPI;
  - scan cible `rg -n "importlib|eval\\(|globals\\(|networkx|igraph|graphlib|celery|prefect|airflow" backend/app/domain/astrology backend/tests -g "*.py"`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - `backend/tests/architecture` seulement si un guard d'imports transverse est ajoute.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/validation.md` | Conserver tests, lint et resultats cibles CS-227. |
| API neutrality | `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/openapi-routes.md` | Conserver OpenAPI et routes. |
| Runner guards | `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/runner-guards.md` | Prouver registry, cache local et imports. |

## 5. Current State Evidence

- CS-225 introduit les contrats et le validator du graphe de calcul.
- CS-226 declare le graphe natal sans l'executer.
- Le pipeline natal reste orchestre proceduralement dans `natal_calculation.py`.
- Aucun runner topologique, registry de calculateurs ou cache d'execution n'est encore la surface canonique documentee.
- Evidence 1: `_story_briefs/cs-227-calculation-graph-runner-cache-provenance.md` - brief du runner attendu et de ses limites.
- Evidence 2: `_condamad/stories/CS-225-calculation-graph-runtime-contracts/00-story.md` - contrats de graphe deja prets.
- Evidence 3: `_condamad/stories/CS-226-natal-calculation-graph-definition/00-story.md` - definition de graphe deja prete.

## 6. Target State

- `CalculationGraphContext` porte les valeurs d'execution sans muter le contexte initial.
- `CalculationNodeRegistry` resout explicitement les calculateurs par code stable.
- `CalculationGraphRunner` valide la definition avant tout calcul.
- Le runner execute les nodes dans un ordre topologique deterministe.
- Les outputs sont collectes dans `CalculationGraphExecutionResult`.
- Les resultats par node exposent status, cache hit, inputs consommes, output produit, calculator et erreur stable.
- Le cache est local a un appel `run`.
- Les erreurs de validation, input manquant, calculator inconnu et calculateur en echec sont testees.
- Aucun calcul astrologique existant, endpoint, DB, migration ou frontend ne change.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Le runner execute un graphe valide en ordre topologique. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; execution_order. |
| AC2 | Le validator CS-225 est appele avant tout calcul. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; compteur calculator nul. |
| AC3 | Les calculateurs sont resolus uniquement via registry explicite. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; AST guard. |
| AC4 | Les outputs sont collectes dans le resultat global. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC5 | L'input manquant produit un message stable. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC6 | Le cache reste local a l'execution. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; AST guard. |
| AC7 | La provenance minimale est disponible. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; provenance assertions. |
| AC8 | Le contexte initial n'est pas mute. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC9 | Aucun calcul astrologique existant n'est modifie. | `pytest -q backend/tests`; AST guard; diff services/calculators. |
| AC10 | Aucune API publique ne change. | `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`; OpenAPI proof. |
| AC11 | Aucune importation dynamique n'est utilisee. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; scan imports; AST guard. |
| AC12 | Le graphe lineaire est couvert. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC13 | Le graphe convergent est couvert. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC14 | Le calculator inconnu produit un message stable. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC15 | Le calculateur en echec produit un message stable. | `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |
| AC16 | Aucun fichier DB ou frontend n'est modifie. | diff adjacent DB/frontend; `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`. |

## 8. Implementation Tasks

- [ ] Task: creer `calculation_graph_runner.py` avec commentaire global et docstrings en francais. (AC: AC1)
- [ ] Task: ajouter `CalculationGraphContext` immuable avec `get_required`. (AC: AC5, AC8)
- [ ] Task: ajouter `CalculationNodeRegistry` avec resolution explicite des calculateurs. (AC: AC3, AC11)
- [ ] Task: ajouter les resultats `CalculationNodeResult` et `CalculationGraphExecutionResult`. (AC: AC4, AC7)
- [ ] Task: brancher `CalculationGraphValidator().validate(definition)` avant l'execution. (AC: AC2)
- [ ] Task: executer les nodes dans l'ordre topologique deterministe. (AC: AC1, AC12)
- [ ] Task: implementer le cache local a `run` pour les outputs deja presents. (AC: AC6)
- [ ] Task: produire une erreur stable pour input manquant. (AC: AC5)
- [ ] Task: produire une erreur stable pour calculator inconnu. (AC: AC14)
- [ ] Task: produire une erreur stable pour calculateur en echec. (AC: AC15)
- [ ] Task: ajouter le test unitaire de graphe factice lineaire. (AC: AC1, AC12)
- [ ] Task: ajouter le test unitaire de graphe factice convergent. (AC: AC1, AC13)
- [ ] Task: ajouter les tests de validation invalide sans execution de calculator. (AC: AC2)
- [ ] Task: ajouter les tests de registry, cache, provenance et immutabilite du contexte initial. (AC: AC3, AC6, AC7, AC8)
- [ ] Task: ajouter l'AST guard ou scan cible contre import dynamique, cache global et dependance externe. (AC: AC6, AC11)
- [ ] Task: ajouter les preuves `app.routes`, `app.openapi()` et `TestClient` de neutralite API. (AC: AC10)
- [ ] Task: collecter l'evidence finale dans le dossier CS-227. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser `CalculationGraphDefinition`, `CalculationNodeDefinition`, `CalculationInputDefinition` et `CalculationNodeStatus` depuis CS-225.
- Reutiliser `CalculationGraphValidator` pour valider dependances, doublons et cycles.
- Reutiliser `natal_calculation_graph.py` comme contrat de definition future, sans le brancher en production.
- Ne pas dupliquer les calculateurs astrologiques existants.
- Ne pas creer une seconde logique de validation de graphe hors besoin runtime minimal.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter `networkx`, `igraph`, `graphlib`, Celery, Prefect, Airflow ou dependance externe de workflow.
- Ne pas utiliser `importlib.import_module`, `eval`, `globals()` ou lookup magique.
- Ne pas migrer `build_natal_result`.
- Ne pas modifier les calculateurs astrologiques existants.
- Ne pas ajouter de cache global, cache persistant, retry ou thread pool.
- Ne pas ajouter de fallback runtime, shim legacy ou couche compatibility pour executer le pipeline natal.

## 11. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - un smoke `TestClient` sur OpenAPI.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code ou schema public ne change volontairement.

## 12. Files to Inspect First

- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/services/natal_calculation.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-144|RG-145|RG-147|RG-148`.

## 13. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/validation.md`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/openapi-routes.md`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/evidence/runner-guards.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py` seulement si la preuve API neutre n'existe pas deja.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- `backend/app/domain/astrology/services/natal_calculation.py`.
- `backend/app/domain/astrology/calculators`.

## 14. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 15. Validation Plan

Run all Python commands after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_validator.py
```

Run anti-regression scans:

```powershell
rg -n "CalculationGraphRunner|CalculationGraphContext|CalculationNodeRegistry" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "importlib|eval\(|globals\(|networkx|igraph|graphlib|celery|prefect|airflow" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "cache:|_cache|global_cache|persistent_cache" backend/app/domain/astrology/runtime/calculation_graph_runner.py
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

The dedicated API neutrality evidence must name `app.routes`, `app.openapi()` and `TestClient`.

## 16. Regression Risks

- Un ordre topologique instable peut rendre les resultats difficiles a comparer.
- Un cache global peut reutiliser des outputs entre executions independantes.
- Une resolution magique de calculator peut contourner le registry explicite.
- Une erreur runtime opaque peut masquer input manquant et calculator inconnu.
- Une confusion entre runner pur et pipeline natal peut migrer trop tot `build_natal_result`.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend: aucun fichier frontend n'est attendu.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in story evidence.
- Stopper et documenter le blocage dans l'evidence si un AC ne peut pas etre satisfait.
- Do not preserve legacy behavior by adding a fallback, shim or compatibility layer for graph execution.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-227 Final Evidence Template

```markdown
## CS-227 Final Evidence

### Runner
- Added CalculationGraphRunner, CalculationGraphContext and CalculationNodeRegistry.
- Graph validation runs before calculators.
- Linear and convergent fake graphs execute in deterministic topological order.

### Cache and Provenance
- Cache is local to a single run call.
- Initial context remains unchanged.
- Node results expose input keys, output key, calculator and cache hit.

### Guards
- No dynamic import or magical calculator lookup.
- No global or persistent cache.
- No API, DB or frontend changes.
```
